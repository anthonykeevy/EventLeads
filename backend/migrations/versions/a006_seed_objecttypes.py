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


def _objecttype_has_columns(bind, *cols: str) -> bool:
    try:
        rows = bind.execute(
            sa.text(
                "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_NAME = 'ObjectType'"
            )
        ).fetchall()
        names = {r[0] for r in rows}
        return all(c in names for c in cols)
    except Exception:
        return False


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("ObjectType"):
        return
    # Only seed if expected columns exist (Name, Category, IsSystemDefault)
    if not _objecttype_has_columns(bind, "Name", "Category", "IsSystemDefault"):
        return
    for name in ("TextField", "DropdownField", "CheckboxField"):
        op.execute(
            sa.text(
                "INSERT INTO ObjectType (Name, Category, IsSystemDefault) "
                "SELECT :n, 'Field', 1 WHERE NOT EXISTS (SELECT 1 FROM ObjectType WHERE Name = :n)"
            ),
            {"n": name},
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("ObjectType"):
        return
    if not _objecttype_has_columns(bind, "Name", "IsSystemDefault"):
        return
    op.execute(
        sa.text(
            "DELETE FROM ObjectType WHERE Name IN ('TextField','DropdownField','CheckboxField') AND IsSystemDefault = 1"
        )
    )
