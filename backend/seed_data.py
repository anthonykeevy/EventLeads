import os
from sqlalchemy import create_engine, text
from app.core.db import Base
from app.models import User, Role, Organization, Event

# Set environment variables
os.environ['DATABASE_URL'] = 'mssql+pyodbc://localhost/master?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'

# Create engine
engine = create_engine(os.environ['DATABASE_URL'])

print("Seeding database with required data...")

with engine.begin() as conn:
    # Insert default roles
    conn.execute(text("""
        IF NOT EXISTS (SELECT 1 FROM Role WHERE RoleName = 'User')
        INSERT INTO Role (RoleName, RoleDescription, IsSystemRole, CreatedDate) 
        VALUES ('User', 'Standard user role', 1, GETDATE())
    """))
    
    conn.execute(text("""
        IF NOT EXISTS (SELECT 1 FROM Role WHERE RoleName = 'Admin')
        INSERT INTO Role (RoleName, RoleDescription, IsSystemRole, CreatedDate) 
        VALUES ('Admin', 'Administrator role', 1, GETDATE())
    """))
    
    conn.execute(text("""
        IF NOT EXISTS (SELECT 1 FROM Role WHERE RoleName = 'SysAdmin')
        INSERT INTO Role (RoleName, RoleDescription, IsSystemRole, CreatedDate) 
        VALUES ('SysAdmin', 'System administrator role', 1, GETDATE())
    """))
    
    # Insert default organization
    conn.execute(text("""
        IF NOT EXISTS (SELECT 1 FROM Organization WHERE OrganizationName = 'Default Organization')
        INSERT INTO Organization (OrganizationName, OrganizationCode, IsActive, CreatedDate) 
        VALUES ('Default Organization', 'DEFAULT', 1, GETDATE())
    """))

print("Database seeded successfully!")

# Verify data was inserted
with engine.connect() as conn:
    print("\nRoles in database:")
    result = conn.execute(text("SELECT RoleID, RoleName FROM Role"))
    for row in result:
        print(f"  ID: {row[0]}, Name: {row[1]}")
    
    print("\nOrganizations in database:")
    result = conn.execute(text("SELECT OrganizationID, OrganizationName FROM Organization"))
    for row in result:
        print(f"  ID: {row[0]}, Name: {row[1]}")
