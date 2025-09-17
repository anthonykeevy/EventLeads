import os
from sqlalchemy import create_engine, text

# Use the same database URL as the app
engine = create_engine(os.getenv('DATABASE_URL', 'sqlite:///./dev.db'))

with engine.connect() as conn:
    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
    tables = [row[0] for row in result]
    print('Existing tables:', tables)
    
    if 'User' in tables:
        print('User table exists ✓')
    else:
        print('User table missing ✗')


