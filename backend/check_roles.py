import os
from sqlalchemy import create_engine, text

# Load environment
DATABASE_URL = os.environ.get('DATABASE_URL', 'mssql+pyodbc://localhost/EventTrackerDB_Dev?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes')

try:
    engine = create_engine(DATABASE_URL)
    conn = engine.connect()
    
    # Check roles
    result = conn.execute(text("SELECT RoleID, RoleName FROM Role"))
    roles = result.fetchall()
    print("Roles in database:")
    for role in roles:
        print(f"  ID: {role[0]}, Name: {role[1]}")
    
    # Check organizations
    result = conn.execute(text("SELECT OrganizationID, Name FROM Organization"))
    orgs = result.fetchall()
    print("\nOrganizations in database:")
    for org in orgs:
        print(f"  ID: {org[0]}, Name: {org[1]}")
    
    conn.close()
except Exception as e:
    print(f"Error: {e}")


