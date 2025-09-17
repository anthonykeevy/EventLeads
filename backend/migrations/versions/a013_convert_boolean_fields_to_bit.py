"""Convert boolean fields to BIT type

Revision ID: a013_convert_boolean_fields_to_bit
Revises: a012_auth_event_audit
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a013_convert_boolean_fields_to_bit'
down_revision = 'a012_auth_event_audit'
branch_labels = None
depends_on = None


def upgrade():
    """Convert EmailVerified from INT to BIT in User table"""
    # SQL Server specific: Convert INT to BIT
    op.execute("""
        ALTER TABLE [User] 
        ALTER COLUMN EmailVerified BIT NOT NULL
    """)
    
    # Set default value for BIT column
    op.execute("""
        ALTER TABLE [User] 
        ADD CONSTRAINT DF_User_EmailVerified DEFAULT 0 FOR EmailVerified
    """)


def downgrade():
    """Convert EmailVerified from BIT back to INT in User table"""
    # Remove default constraint first
    op.execute("""
        ALTER TABLE [User] 
        DROP CONSTRAINT DF_User_EmailVerified
    """)
    
    # Convert BIT back to INT
    op.execute("""
        ALTER TABLE [User] 
        ALTER COLUMN EmailVerified INT NOT NULL
    """)
