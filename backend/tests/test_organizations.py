import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from unittest.mock import patch

from app.main import app
from app.core.db import engine
from app.routers.auth import create_jwt_token


client = TestClient(app)


@pytest.fixture
def test_user_token():
    """Create a test JWT token for a user."""
    payload = {
        "UserID": 1,
        "Email": "test@example.com",
        "OrganizationID": None,  # User has no organization initially
        "role": "User"
    }
    return create_jwt_token(payload, "test-secret")


@pytest.fixture
def test_admin_token():
    """Create a test JWT token for an admin user."""
    payload = {
        "UserID": 2,
        "Email": "admin@example.com",
        "OrganizationID": 1,  # Admin already has organization
        "role": "Admin"
    }
    return create_jwt_token(payload, "test-secret")


@pytest.fixture
def cleanup_test_data():
    """Clean up test data after each test."""
    yield
    with engine.begin() as conn:
        # Clean up test organizations and users
        conn.execute(text("DELETE FROM [User] WHERE Email IN ('test@example.com', 'admin@example.com')"))
        conn.execute(text("DELETE FROM Organization WHERE OrganizationName LIKE 'Test Org%'"))


class TestCreateOrganization:
    """Test organization creation endpoint."""
    
    def test_create_organization_success(self, test_user_token, cleanup_test_data):
        """Test successful organization creation."""
        with patch('app.routers.organizations.get_role_id') as mock_get_role:
            mock_get_role.return_value = 1  # Admin role ID
            
            response = client.post(
                "/organizations/",
                json={
                    "name": "Test Organization",
                    "billing_email": "billing@test.com",
                    "billing_address": "123 Test St, Test City, TC 12345",
                    "timezone": "America/New_York"
                },
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["name"] == "Test Organization"
            assert data["timezone"] == "America/New_York"
            assert "id" in data
            assert "created_at" in data
    
    def test_create_organization_minimal_data(self, test_user_token, cleanup_test_data):
        """Test organization creation with minimal required data."""
        with patch('app.routers.organizations.get_role_id') as mock_get_role:
            mock_get_role.return_value = 1  # Admin role ID
            
            response = client.post(
                "/organizations/",
                json={
                    "name": "Minimal Test Org"
                },
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["name"] == "Minimal Test Org"
            assert data["timezone"] == "UTC"  # Default timezone
    
    def test_create_organization_user_already_has_org(self, test_admin_token, cleanup_test_data):
        """Test that user with existing organization cannot create another."""
        response = client.post(
            "/organizations/",
            json={
                "name": "Another Test Organization"
            },
            headers={"Authorization": f"Bearer {test_admin_token}"}
        )
        
        assert response.status_code == 400
        assert "already belongs to an organization" in response.json()["detail"]
    
    def test_create_organization_invalid_data(self, test_user_token):
        """Test organization creation with invalid data."""
        # Missing required name
        response = client.post(
            "/organizations/",
            json={
                "billing_email": "invalid-email"
            },
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 422
        
        # Invalid email format
        response = client.post(
            "/organizations/",
            json={
                "name": "Test Org",
                "billing_email": "not-an-email"
            },
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 422
    
    def test_create_organization_unauthorized(self):
        """Test organization creation without authentication."""
        response = client.post(
            "/organizations/",
            json={
                "name": "Test Organization"
            }
        )
        assert response.status_code == 401


class TestGetOrganization:
    """Test get organization endpoint."""
    
    def test_get_organization_success(self, test_admin_token, cleanup_test_data):
        """Test successful organization retrieval."""
        with engine.begin() as conn:
            # Create a test organization
            conn.execute(text("""
                INSERT INTO Organization (
                    OrganizationName, OrganizationCode, OrganizationSlug,
                    OrganizationEmail, Timezone, IsActive, CreatedDate, CreatedBy,
                    SubscriptionTier, SubscriptionStatus, MaxUsers, MaxEvents
                ) VALUES (
                    'Test Org', 'test-org', 'test-org', 'admin@test.com', 'UTC',
                    1, GETUTCDATE(), 'admin@test.com', 'Basic', 'Active', 5, 10
                )
            """))
            
            # Update user to be part of this organization
            conn.execute(text("""
                UPDATE [User] SET OrganizationID = SCOPE_IDENTITY() WHERE Email = 'admin@example.com'
            """))
        
        response = client.get(
            "/organizations/me",
            headers={"Authorization": f"Bearer {test_admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Org"
        assert data["timezone"] == "UTC"
        assert data["is_active"] is True
    
    def test_get_organization_not_found(self, test_user_token):
        """Test organization retrieval when user has no organization."""
        response = client.get(
            "/organizations/me",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 404
        assert "No organization found" in response.json()["detail"]
    
    def test_get_organization_unauthorized(self):
        """Test organization retrieval without authentication."""
        response = client.get("/organizations/me")
        assert response.status_code == 401


class TestOrganizationValidation:
    """Test organization validation and constraints."""
    
    def test_organization_name_validation(self, test_user_token):
        """Test organization name validation."""
        # Empty name
        response = client.post(
            "/organizations/",
            json={"name": ""},
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 422
        
        # Name too long
        long_name = "a" * 256
        response = client.post(
            "/organizations/",
            json={"name": long_name},
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 422
    
    def test_timezone_validation(self, test_user_token):
        """Test timezone field validation."""
        with patch('app.routers.organizations.get_role_id') as mock_get_role:
            mock_get_role.return_value = 1
            
            # Valid timezone
            response = client.post(
                "/organizations/",
                json={
                    "name": "Test Org",
                    "timezone": "America/Los_Angeles"
                },
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            assert response.status_code == 201
            
            # Empty timezone should default to UTC
            response = client.post(
                "/organizations/",
                json={
                    "name": "Test Org 2",
                    "timezone": ""
                },
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            assert response.status_code == 422  # Empty string not allowed


class TestOrganizationCodeGeneration:
    """Test organization code and slug generation."""
    
    def test_organization_code_generation(self, test_user_token, cleanup_test_data):
        """Test that organization codes are generated correctly."""
        with patch('app.routers.organizations.get_role_id') as mock_get_role:
            mock_get_role.return_value = 1
            
            response = client.post(
                "/organizations/",
                json={"name": "My Awesome Company!"},
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            
            assert response.status_code == 201
            
            # Check that organization was created with proper code
            with engine.begin() as conn:
                org = conn.execute(text("""
                    SELECT OrganizationCode, OrganizationSlug 
                    FROM Organization 
                    WHERE OrganizationName = 'My Awesome Company!'
                """)).fetchone()
                
                assert org is not None
                code = org[0]
                slug = org[1]
                
                # Code should be lowercase, hyphenated
                assert code == code.lower()
                assert "-" in code or len(code) >= 10  # Should have hyphens or random suffix
                assert "my-awesome-company" in code or code.startswith("my-awesome-company")
                
                # Slug should be similar
                assert slug == slug.lower()
                assert "my-awesome-company" in slug or slug.startswith("my-awesome-company")


class TestAdminRoleAssignment:
    """Test that organization creator becomes Admin."""
    
    def test_creator_becomes_admin(self, test_user_token, cleanup_test_data):
        """Test that organization creator is assigned Admin role."""
        with patch('app.routers.organizations.get_role_id') as mock_get_role:
            mock_get_role.return_value = 1  # Admin role ID
            
            response = client.post(
                "/organizations/",
                json={"name": "Test Organization"},
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            
            assert response.status_code == 201
            
            # Check that user was assigned Admin role
            with engine.begin() as conn:
                user = conn.execute(text("""
                    SELECT u.RoleID, r.RoleName 
                    FROM [User] u
                    JOIN Role r ON u.RoleID = r.RoleID
                    WHERE u.Email = 'test@example.com'
                """)).fetchone()
                
                assert user is not None
                assert user[1] == "Admin"  # RoleName should be "Admin"
