from __future__ import annotations

from datetime import datetime, timezone
import secrets
import string
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field, constr
from sqlalchemy import text

from ..core.db import engine
from ..schemas.organization import CreateOrganizationRequest, OrganizationResponse, OrganizationSummary
from .auth import auth_dependency, get_role_id, write_auth_event


router = APIRouter(prefix="/organizations", tags=["organizations"])


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _generate_organization_code(name: str) -> str:
    """Generate a unique organization code from the name."""
    # Convert to lowercase, replace spaces with hyphens, remove special chars
    code = ''.join(c.lower() if c.isalnum() else '-' for c in name)
    # Remove multiple consecutive hyphens
    code = '-'.join(part for part in code.split('-') if part)
    # Limit length
    code = code[:50]
    # Add random suffix if needed for uniqueness
    if len(code) < 10:
        code += '-' + ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(6))
    return code


def _generate_organization_slug(name: str) -> str:
    """Generate a unique organization slug from the name."""
    # Similar to code but shorter and more URL-friendly
    slug = ''.join(c.lower() if c.isalnum() else '-' for c in name)
    slug = '-'.join(part for part in slug.split('-') if part)
    slug = slug[:100]
    if len(slug) < 5:
        slug += '-' + ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(4))
    return slug


@router.post("/", response_model=OrganizationSummary, status_code=201)
async def create_organization(
    request: CreateOrganizationRequest,
    current_user: dict = Depends(auth_dependency),
    http_request: Request = None
):
    """
    Create a new organization and assign the current user as Admin.
    
    This endpoint is used by the onboarding wizard to create an organization
    for a first-time user. The creator automatically becomes an Admin.
    """
    user_id = current_user.get("UserID")
    user_email = current_user.get("Email")
    
    if not user_id or not user_email:
        raise HTTPException(status_code=401, detail="Invalid user session")
    
    # Check if user already has an organization
    with engine.begin() as conn:
        existing_org = conn.execute(
            text("SELECT OrganizationID FROM [User] WHERE UserID = :uid"),
            {"uid": user_id}
        ).fetchone()
        
        if existing_org and existing_org[0]:
            raise HTTPException(
                status_code=400, 
                detail="User already belongs to an organization. Only one organization per user is allowed."
            )
    
    # Generate unique organization code and slug
    org_code = _generate_organization_code(request.name)
    org_slug = _generate_organization_slug(request.name)
    
    # Create the organization
    with engine.begin() as conn:
        # Insert organization
        result = conn.execute(
            text("""
                INSERT INTO Organization (
                    OrganizationName, OrganizationCode, OrganizationSlug, 
                    OrganizationEmail, BillingEmail, BillingAddress, Timezone,
                    IsActive, CreatedDate, CreatedBy, SubscriptionTier, 
                    SubscriptionStatus, MaxUsers, MaxEvents
                ) 
                OUTPUT INSERTED.OrganizationID
                VALUES (
                    :name, :code, :slug, :email, :billing_email, :billing_address, :timezone,
                    1, GETUTCDATE(), :created_by, 'Basic', 'Active', 5, 10
                )
            """),
            {
                "name": request.name,
                "code": org_code,
                "slug": org_slug,
                "email": user_email,  # Use user's email as org email initially
                "billing_email": request.billing_email,
                "billing_address": request.billing_address,
                "timezone": request.timezone,
                "created_by": user_email
            }
        )
        
        org_id = result.fetchone()[0]
        
        # Get Admin role ID
        admin_role_id = get_role_id(conn, "Admin")
        
        # Update user to be part of this organization with Admin role
        conn.execute(
            text("""
                UPDATE [User] 
                SET OrganizationID = :org_id, RoleID = :role_id
                WHERE UserID = :user_id
            """),
            {
                "org_id": org_id,
                "role_id": admin_role_id,
                "user_id": user_id
            }
        )
        
        # Log the organization creation event
        write_auth_event(
            engine,
            event_type="organization_created",
            status="success",
            org_id=org_id,
            user_id=user_id,
            email=user_email,
            reason="Organization created via onboarding wizard",
            request=http_request
        )
    
    # Return organization summary (excluding sensitive billing info)
    return OrganizationSummary(
        id=org_id,
        name=request.name,
        timezone=request.timezone,
        created_at=_now()
    )


@router.get("/me", response_model=OrganizationResponse)
async def get_my_organization(
    current_user: dict = Depends(auth_dependency)
):
    """Get the current user's organization details."""
    user_id = current_user.get("UserID")
    org_id = current_user.get("OrganizationID")
    
    if not user_id or not org_id:
        raise HTTPException(status_code=404, detail="No organization found for user")
    
    with engine.begin() as conn:
        org = conn.execute(
            text("""
                SELECT OrganizationID, OrganizationName, OrganizationCode, IsActive,
                       CreatedDate, CreatedBy, OrganizationSlug, OrganizationEmail,
                       OrganizationPhone, BillingAddress, BillingEmail, Timezone,
                       SubscriptionTier, SubscriptionStatus, MaxUsers, MaxEvents
                FROM Organization 
                WHERE OrganizationID = :org_id AND IsActive = 1
            """),
            {"org_id": org_id}
        ).fetchone()
        
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        return OrganizationResponse(
            id=org[0],
            name=org[1],
            code=org[2],
            is_active=org[3] != 0,  # Convert BIT to boolean
            created_at=org[4],
            created_by=org[5],
            slug=org[6],
            email=org[7],
            phone=org[8],
            billing_address=org[9],
            billing_email=org[10],
            timezone=org[11],
            subscription_tier=org[12],
            subscription_status=org[13],
            max_users=org[14],
            max_events=org[15]
        )




