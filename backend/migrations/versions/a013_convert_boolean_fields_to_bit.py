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


def _default_exists(bind) -> bool:
    row = bind.execute(
        sa.text(
            """
            SELECT COUNT(1)
            FROM sys.default_constraints dc
            JOIN sys.columns c ON c.default_object_id = dc.object_id
            JOIN sys.objects o ON o.object_id = c.object_id
            WHERE o.name = 'User' AND c.name = 'EmailVerified'
            """
        )
    ).scalar()
    try:
        return bool(int(row or 0))
    except Exception:
        return False


def upgrade():
    """Convert EmailVerified from INT to BIT in User table"""
    bind = op.get_bind()
    # Convert column type to BIT (idempotent if already BIT)
    try:
        op.execute(
            """
            ALTER TABLE [User]
            ALTER COLUMN EmailVerified BIT NOT NULL
            """
        )
    except Exception:
        pass

    # Add default constraint if not present
    if not _default_exists(bind):
        op.execute(
            """
            ALTER TABLE [User]
            ADD CONSTRAINT DF_User_EmailVerified DEFAULT 0 FOR EmailVerified
            """
        )


def downgrade():
    """Convert EmailVerified from BIT back to INT in User table"""
    bind = op.get_bind()
    # Drop default constraint if exists
    try:
        # Find existing default constraint name dynamically
        row = bind.execute(
            sa.text(
                """
                SELECT dc.name
                FROM sys.default_constraints dc
                JOIN sys.columns c ON c.default_object_id = dc.object_id
                JOIN sys.objects o ON o.object_id = c.object_id
                WHERE o.name = 'User' AND c.name = 'EmailVerified'
                """
            )
        ).first()
        if row and row[0]:
            op.execute(f"ALTER TABLE [User] DROP CONSTRAINT {row[0]}")
    except Exception:
        pass

    try:
        op.execute(
            """
            ALTER TABLE [User]
            ALTER COLUMN EmailVerified INT NOT NULL
            """
        )
    except Exception:
        pass
