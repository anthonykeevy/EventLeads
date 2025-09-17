#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.core.db import engine
from backend.app.utils.security import hash_password
from sqlalchemy import text

def update_test_passwords():
    """Update test users to use standard UAT password"""
    standard_password = "TestPassword123!"
    salt = ""  # Empty salt for bcrypt
    
    try:
        with engine.begin() as conn:
            # Update all test users to use the standard password
            test_emails = ['user@local.dev', 'admin@local.dev', 'sysadmin@local.dev']
            
            for email in test_emails:
                pwd_hash = hash_password(salt, standard_password)
                conn.execute(
                    text("UPDATE [User] SET PasswordHash = :hash, PasswordSalt = :salt WHERE Email = :email"),
                    {"hash": pwd_hash, "salt": salt, "email": email}
                )
                print(f"✅ Updated password for {email}")
            
            print(f"\n🎯 All test users now use password: {standard_password}")
            print("Ready for UAT testing!")
            
    except Exception as e:
        print(f'❌ Failed to update passwords: {e}')

if __name__ == "__main__":
    update_test_passwords()


