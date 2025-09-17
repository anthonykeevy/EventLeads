"""Seed default ObjectType rows

Revision ID: a006_seed_objecttypes
Revises: a005_usagecharge_optional
Create Date: 2025-09-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a006_seed_objecttypes"
down_revision: Union[str, Sequence[str], None] = "a005_usagecharge_optional"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("ObjectType"):
        return
    # Cross-dialect inserts guarded by NOT EXISTS
    for name in ("TextField", "DropdownField", "CheckboxField"):
        op.execute(
            f"INSERT INTO ObjectType (Name, Category, IsSystemDefault) SELECT '{name}', 'Field', 1 "
            f"WHERE NOT EXISTS (SELECT 1 FROM ObjectType WHERE Name = '{name}')"
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("ObjectType"):
        return
    op.execute(
        "DELETE FROM ObjectType WHERE Name IN "
        "('TextField','DropdownField','CheckboxField') AND IsSystemDefault = 1"
    )
