"""Create GlobalSetting table and seed invite token TTL

Revision ID: a015_globalsetting_table
Revises: a014_canvaslayout_table
Create Date: 2025-09-18
"""
from typing import Sequence, Union

from alembic import op  # type: ignore[attr-defined]
import sqlalchemy as sa


revision: str = "a015_globalsetting_table"
down_revision: Union[str, Sequence[str], None] = (
    "a014_canvaslayout_table"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()  # type: ignore[attr-defined]
    dialect = bind.dialect.name if bind is not None else ""

    # Use non-reserved column names to avoid SQL Server keyword conflicts
    op.create_table(
        "GlobalSetting",
        sa.Column(
            "GlobalSettingID", sa.BigInteger(), primary_key=True, autoincrement=True
        ),
        sa.Column("SettingKey", sa.String(length=100), nullable=True, unique=False),
        sa.Column("SettingValue", sa.String(length=4000), nullable=True),
        sa.Column("ValueType", sa.String(length=32), nullable=True),
        sa.Column(
            "Scope",
            sa.String(length=32),
            nullable=False,
            server_default=sa.text("'global'" if dialect != "sqlite" else "global"),
        ),
        # Legacy columns (nullable) in case earlier partial runs created them
        sa.Column("Key", sa.String(length=100), nullable=True),
        sa.Column("Value", sa.String(length=4000), nullable=True),
    )

    # Seed initial settings
    try:
        op.execute(
            "INSERT INTO GlobalSetting (SettingKey, SettingValue, ValueType, Scope) VALUES ('invite_token_ttl_hours', '48', 'int', 'global')"
        )
        op.execute(
            "INSERT INTO GlobalSetting (SettingKey, SettingValue, ValueType, Scope) VALUES ('invite_daily_limit', '10', 'int', 'global')"
        )
    except Exception:
        # Fallback for legacy column names
        op.execute(
            "INSERT INTO GlobalSetting ([Key], [Value], ValueType, Scope) VALUES ('invite_token_ttl_hours', '48', 'int', 'global')"
        )
        op.execute(
            "INSERT INTO GlobalSetting ([Key], [Value], ValueType, Scope) VALUES ('invite_daily_limit', '10', 'int', 'global')"
        )


def downgrade() -> None:
    # Best-effort delete seed rows regardless of column naming
    try:
        op.execute(
            "DELETE FROM GlobalSetting WHERE COALESCE(SettingKey, [Key]) IN ('invite_token_ttl_hours','invite_daily_limit')"
        )
    except Exception:
        pass

    op.drop_table("GlobalSetting")  # type: ignore[attr-defined]
