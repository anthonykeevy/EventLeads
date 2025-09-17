#!/usr/bin/env python3
"""
Check users and roles in the database and provide test credentials
"""
import pyodbc
import hashlib
import secrets

def connect_db():
    """Connect to the database using Windows Authentication"""
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=EventTrackerDB_Dev;Trusted_Connection=yes;'
    try:
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def check_users_and_roles():
    """Check what users and roles exist in the database"""
    conn = connect_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    try:
        # Check users
        cursor.execute('SELECT UserID, Email, Username, RoleID FROM [User]')
        users = cursor.fetchall()
        print("Current users in database:")
        for user in users:
            print(f"  ID: {user[0]}, Email: {user[1]}, Username: {user[2]}, RoleID: {user[3]}")
        
        # Check roles
        cursor.execute('SELECT RoleID, Name FROM Role')
        roles = cursor.fetchall()
        print("\nCurrent roles in database:")
        for role in roles:
            print(f"  ID: {role[0]}, Name: {role[1]}")
            
    except Exception as e:
        print(f"Error querying database: {e}")
    finally:
        conn.close()

def create_test_credentials():
    """Create test credentials for UAT testing"""
    print("\n" + "="*50)
    print("UAT TEST CREDENTIALS")
    print("="*50)
    
    # Standard test credentials
    test_users = [
        {
            "role": "SystemAdmin",
            "email": "sysadmin@local.dev",
            "password": "TestPassword123!"
        },
        {
            "role": "Admin", 
            "email": "admin@local.dev",
            "password": "TestPassword123!"
        },
        {
            "role": "User",
            "email": "user@local.dev", 
            "password": "TestPassword123!"
        }
    ]
    
    for user in test_users:
        print(f"\n{user['role']}:")
        print(f"  Email: {user['email']}")
        print(f"  Password: {user['password']}")
    
    print("\n" + "="*50)
    print("UAT TESTING INSTRUCTIONS")
    print("="*50)
    print("1. Start the application: .\\scripts\\start-dev.ps1")
    print("2. Open browser: http://localhost:3000")
    print("3. Use the credentials above to test:")
    print("   - Signup flow (create new account)")
    print("   - Login flow (use existing accounts)")
    print("   - Password reset flow")
    print("   - Protected route access")
    print("4. Check MailHog: http://localhost:8025 for emails")

if __name__ == "__main__":
    print("EventLeads - User & Role Check")
    print("="*40)
    
    check_users_and_roles()
    create_test_credentials()


