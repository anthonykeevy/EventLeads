import os
from sqlalchemy import create_engine, text

# Load environment
DATABASE_URL = os.environ.get('DATABASE_URL', 'mssql+pyodbc://localhost/EventTrackerDB_Dev?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes')

try:
    engine = create_engine(DATABASE_URL)
    conn = engine.connect()
    
    # Check organization table structure
    result = conn.execute(text("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Organization'"))
    columns = result.fetchall()
    print("Organization table columns:")
    for col in columns:
        print(f"  {col[0]}")
    
    # Check organizations
    result = conn.execute(text("SELECT * FROM Organization"))
    orgs = result.fetchall()
    print(f"\nOrganizations in database ({len(orgs)} found):")
    for org in orgs:
        print(f"  {org}")
    
    conn.close()
except Exception as e:
    print(f"Error: {e}")


