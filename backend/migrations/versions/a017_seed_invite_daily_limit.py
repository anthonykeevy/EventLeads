"""Seed invite_daily_limit in GlobalSetting (idempotent)

Revision ID: a017_seed_invite_daily_limit
Revises: a016_invitation_table
Create Date: 2025-09-18
"""
from typing import Sequence, Union

from alembic import op  # type: ignore[attr-defined]
import sqlalchemy as sa


revision: str = "a017_seed_invite_daily_limit"
down_revision: Union[str, Sequence[str], None] = (
    "a016_invitation_table"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Insert only if not exists, handling both legacy and new column names
    try:
        op.execute(
            """
            IF NOT EXISTS (
              SELECT 1 FROM GlobalSetting WHERE COALESCE(SettingKey, [Key]) = 'invite_daily_limit'
            )
            BEGIN
              INSERT INTO GlobalSetting (SettingKey, SettingValue, ValueType, Scope)
              VALUES ('invite_daily_limit', '10', 'int', 'global')
            END
            """
        )
    except Exception:
        # Fallback for SQLite (no IF NOT EXISTS in this form)
        try:
            op.execute(
                "INSERT INTO GlobalSetting (SettingKey, SettingValue, ValueType, Scope) SELECT 'invite_daily_limit','10','int','global' "
                "WHERE NOT EXISTS (SELECT 1 FROM GlobalSetting WHERE COALESCE(SettingKey, [Key]) = 'invite_daily_limit')"
            )
        except Exception:
            # Last resort with legacy columns
            op.execute(
                "INSERT INTO GlobalSetting ([Key], [Value], ValueType, Scope) SELECT 'invite_daily_limit','10','int','global' "
                "WHERE NOT EXISTS (SELECT 1 FROM GlobalSetting WHERE COALESCE(SettingKey, [Key]) = 'invite_daily_limit')"
            )


def downgrade() -> None:
    try:
        op.execute(
            "DELETE FROM GlobalSetting WHERE COALESCE(SettingKey, [Key]) = 'invite_daily_limit'"
        )
    except Exception:
        pass




