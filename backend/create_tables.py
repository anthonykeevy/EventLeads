import os
from sqlalchemy import create_engine
from app.core.db import Base
from app.models import User, Role, Organization, Event

# Set environment variables
os.environ['DATABASE_URL'] = 'mssql+pyodbc://localhost/master?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'

# Create engine
engine = create_engine(os.environ['DATABASE_URL'])

# Create all tables
print("Creating database tables...")
Base.metadata.create_all(engine)
print("Tables created successfully!")

# Verify tables were created
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"))
    tables = [row[0] for row in result]
    print('Created tables:', tables)
