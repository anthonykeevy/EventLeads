#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.core.db import engine
from backend.app.utils.security import verify_password
from sqlalchemy import text

def debug_login():
    email = "user@local.dev"
    password = "TestPassword123!"
    
    try:
        with engine.begin() as conn:
            # Step 1: Check if user exists
            user = conn.execute(
                text("SELECT TOP 1 * FROM [User] WHERE Email = :email ORDER BY UserID DESC"),
                {"email": email}
            ).mappings().first()
            
            if not user:
                print("❌ User not found")
                return
            
            print(f"✅ User found: {user['Email']}")
            print(f"  UserID: {user['UserID']}")
            print(f"  EmailVerified: {user['EmailVerified']}")
            print(f"  PasswordHash: {user['PasswordHash'][:20]}...")
            print(f"  PasswordSalt: '{user['PasswordSalt']}'")
            
            # Step 2: Check password verification
            is_valid = verify_password(
                user.get("PasswordSalt"), 
                user.get("PasswordHash"), 
                password
            )
            print(f"  Password valid: {is_valid}")
            
            # Step 3: Check role lookup
            role_id = user.get("RoleID")
            print(f"  RoleID: {role_id}")
            
            # Check if role exists
            role = conn.execute(
                text("SELECT RoleID, Name FROM Role WHERE RoleID = :role_id"),
                {"role_id": role_id}
            ).mappings().first()
            
            if role:
                print(f"  Role: {role['Name']}")
            else:
                print("  ❌ Role not found")
                
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_login()


