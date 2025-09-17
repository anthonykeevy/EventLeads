import os
from sqlalchemy import create_engine, text

# Use SQL Server connection
engine = create_engine(os.getenv('DATABASE_URL', 'mssql+pyodbc://sa:YourStrong!Passw0rd@localhost:1433/master?driver=ODBC+Driver+17+for+SQL+Server'))

with engine.connect() as conn:
    result = conn.execute(text("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"))
    tables = [row[0] for row in result]
    print('Existing tables in SQL Server:', tables)
    
    if 'User' in tables:
        print('User table exists ✓')
    else:
        print('User table missing ✗')


