import os
from sqlalchemy import create_engine, text

# Load environment
DATABASE_URL = os.environ.get('DATABASE_URL', 'mssql+pyodbc://sa:YourStrong!Passw0rd@localhost:1433/master?driver=ODBC+Driver+17+for+SQL+Server')

try:
    engine = create_engine(DATABASE_URL)
    conn = engine.connect()
    result = conn.execute(text("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"))
    tables = [row[0] for row in result]
    print("Existing tables:", tables)
    conn.close()
except Exception as e:
    print(f"Error: {e}")


