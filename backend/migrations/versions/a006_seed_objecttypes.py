"""Seed default ObjectType rows

Revision ID: a006_seed_objecttypes
Revises: a005_usagecharge_optional
Create Date: 2025-09-14
"""
from typing import Sequence, Union

from alembic import op


revision: str = "a006_seed_objecttypes"
down_revision: Union[str, Sequence[str], None] = "a005_usagecharge_optional"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Cross-dialect inserts guarded by NOT EXISTS
    for name in ("TextField", "DropdownField", "CheckboxField"):
        op.execute(
            f"INSERT INTO ObjectType (Name, Category, IsSystemDefault) SELECT '{name}', 'Field', 1 WHERE NOT EXISTS (SELECT 1 FROM ObjectType WHERE Name = '{name}')"
        )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM ObjectType WHERE Name IN ('TextField','DropdownField','CheckboxField') AND IsSystemDefault = 1;
        """
    )
