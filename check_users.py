#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.core.db import engine
from sqlalchemy import text

def check_users():
    with engine.begin() as conn:
        users = conn.execute(text("""
            SELECT UserID, Email, EmailVerified, RoleID 
            FROM [User] 
            WHERE Email IN ('user@local.dev', 'admin@local.dev', 'sysadmin@local.dev')
        """)).fetchall()
        
        print("Test User Verification Status:")
        print("=" * 50)
        for user in users:
            print(f"User: {user[1]}")
            print(f"  UserID: {user[0]}")
            print(f"  EmailVerified: {user[2]}")
            print(f"  RoleID: {user[3]}")
            print()

if __name__ == "__main__":
    check_users()


