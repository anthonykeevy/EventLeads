import os
from sqlalchemy import create_engine, text
from app.core.settings import settings

engine = create_engine(settings.database_url)
conn = engine.connect()

result = conn.execute(text("SELECT UserID, Email, EmailVerified, CreatedDate FROM [User] WHERE Email = 'user@example.com' ORDER BY UserID DESC"))
print("User found:")
for row in result:
    print(f"  ID: {row[0]}, Email: {row[1]}, Verified: {row[2]}, Created: {row[3]}")

conn.close()


