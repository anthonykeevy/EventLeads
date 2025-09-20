"""Create Form table with slug and soft-delete

Revision ID: a002_form_table_and_slug
Revises: a001_event_timezone_enddate
Create Date: 2025-09-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a002_form_table_and_slug"
down_revision: Union[str, Sequence[str], None] = "a001_event_timezone_enddate"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _event_id_type() -> sa.types.TypeEngine:
    bind = op.get_bind()
    dialect = bind.dialect.name if bind is not None else ""
    if dialect == "mssql":
        # Introspect Event.EventID to choose matching type
        result = bind.execute(
            sa.text(
                "SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_NAME = 'Event' AND COLUMN_NAME = 'EventID'"
            )
        ).first()
        data_type = (result[0].lower() if result and result[0] else "int")
        if data_type == "bigint":
            return sa.BigInteger()
        return sa.Integer()
    # Default for other dialects
    return sa.BigInteger()


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name if bind is not None else ""
    utc_default = sa.text("CURRENT_TIMESTAMP") if dialect == "sqlite" else sa.text("GETUTCDATE()")

    event_fk_type = _event_id_type()

    op.create_table(
        "Form",
        sa.Column("FormID", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("EventID", event_fk_type, sa.ForeignKey("Event.EventID"), nullable=False),
        sa.Column("Name", sa.String(length=300), nullable=False),
        sa.Column("Status", sa.String(length=50), nullable=False),
        sa.Column("PublicSlug", sa.String(length=80), nullable=True),
        sa.Column("IsDeleted", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("DeletedAt", sa.DateTime(), nullable=True),
        sa.Column("DeletedBy", sa.String(length=100), nullable=True),
        sa.Column("CreatedDate", sa.DateTime(), nullable=False, server_default=utc_default),
        sa.Column("CreatedBy", sa.String(length=100), nullable=True),
        sa.Column("LastUpdated", sa.DateTime(), nullable=True),
        sa.Column("UpdatedBy", sa.String(length=100), nullable=True),
    )
    # Filtered unique index on PublicSlug where not null
    if dialect == "sqlite":
        op.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS UX_Form_PublicSlug "
            "ON Form(PublicSlug) WHERE PublicSlug IS NOT NULL"
        )
    else:
        # SQL Server doesn't support IF NOT EXISTS in CREATE INDEX directly
        op.execute(
            "CREATE UNIQUE INDEX UX_Form_PublicSlug ON [Form]([PublicSlug]) "
            "WHERE [PublicSlug] IS NOT NULL"
        )


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name if bind is not None else ""
    if dialect == "sqlite":
        op.execute("DROP INDEX IF EXISTS UX_Form_PublicSlug")
    else:
        op.execute("DROP INDEX UX_Form_PublicSlug ON Form")
    op.drop_table("Form")
