import os
from sqlalchemy import create_engine, text
from app.core.settings import settings

engine = create_engine(settings.database_url)
conn = engine.connect()

print("=== USER RECORD ===")
result = conn.execute(text("SELECT UserID, Email, EmailVerified, CreatedDate FROM [User] WHERE Email = 'user@example.com' ORDER BY UserID DESC"))
for row in result:
    print(f"  ID: {row[0]}, Email: {row[1]}, Verified: {row[2]}, Created: {row[3]}")

print("\n=== VERIFICATION TOKEN ===")
result = conn.execute(text("SELECT id, user_id, token, expires_at, created_at FROM emailverificationtoken WHERE user_id = 7 ORDER BY id DESC"))
for row in result:
    print(f"  ID: {row[0]}, UserID: {row[1]}, Token: {row[2][:20]}..., Expires: {row[3]}, Created: {row[4]}")

conn.close()


