import os
from sqlalchemy import create_engine, text
from app.core.settings import settings

engine = create_engine(settings.database_url)
conn = engine.connect()

print("=== EMAILVERIFICATIONTOKEN TABLE COLUMNS ===")
result = conn.execute(text("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'emailverificationtoken' ORDER BY ORDINAL_POSITION"))
for row in result:
    print(f"  {row[0]}")

print("\n=== USER TABLE COLUMNS ===")
result = conn.execute(text("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'User' ORDER BY ORDINAL_POSITION"))
for row in result:
    print(f"  {row[0]}")

conn.close()


