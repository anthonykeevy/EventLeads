"""add organization billing fields

Revision ID: a018_add_organization_billing_fields
Revises: a017_seed_invite_daily_limit
Create Date: 2025-01-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql

# revision identifiers, used by Alembic.
revision: str = 'a018_add_organization_billing_fields'
down_revision: Union[str, Sequence[str], None] = 'a017_seed_invite_daily_limit'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add BillingEmail and Timezone fields to Organization table."""
    bind = op.get_bind()
    dialect = bind.dialect.name if bind is not None else ""
    
    # Add BillingEmail field
    op.add_column('Organization', 
        sa.Column('BillingEmail', sa.String(length=320), nullable=True)
    )
    
    # Add Timezone field with default value
    op.add_column('Organization', 
        sa.Column('Timezone', sa.String(length=100), nullable=False, server_default='UTC')
    )
    
    # Update existing records to have UTC timezone
    if dialect == "mssql":
        op.execute("UPDATE Organization SET Timezone = 'UTC' WHERE Timezone IS NULL")
    else:
        op.execute("UPDATE Organization SET Timezone = 'UTC' WHERE Timezone IS NULL")


def downgrade() -> None:
    """Remove BillingEmail and Timezone fields from Organization table."""
    op.drop_column('Organization', 'Timezone')
    op.drop_column('Organization', 'BillingEmail')




