"""Event: add timezone, end_date, soft-delete

Revision ID: a001_event_timezone_enddate
Revises: d7e114319162
Create Date: 2025-09-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a001_event_timezone_enddate"
down_revision: Union[str, Sequence[str], None] = "d7e114319162"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name if bind is not None else ""
    if dialect == "mssql":
        # Conditionally add columns only if they don't exist
        # (avoid errors on existing schemas)
        op.execute(
            """
            IF COL_LENGTH('dbo.Event','Timezone') IS NULL
              ALTER TABLE [Event] ADD [Timezone] NVARCHAR(64) 
              CONSTRAINT DF_Event_Timezone DEFAULT 'UTC' NOT NULL;
            IF COL_LENGTH('dbo.Event','EndDate') IS NULL
              ALTER TABLE [Event] ADD [EndDate] DATE NULL;
            IF COL_LENGTH('dbo.Event','IsDeleted') IS NULL
              ALTER TABLE [Event] ADD [IsDeleted] BIT 
              CONSTRAINT DF_Event_IsDeleted DEFAULT 0 NOT NULL;
            IF COL_LENGTH('dbo.Event','DeletedAt') IS NULL
              ALTER TABLE [Event] ADD [DeletedAt] DATETIME2 NULL;
            IF COL_LENGTH('dbo.Event','DeletedBy') IS NULL
              ALTER TABLE [Event] ADD [DeletedBy] NVARCHAR(100) NULL;
            """
        )
        # Skip DurationDays backfill since Event table already has proper
        # StartDate/EndDate structure
    else:
        op.add_column(
            "Event",
            sa.Column(
                "Timezone",
                sa.String(length=64),
                nullable=False,
                server_default="UTC",
            ),
        )
        op.add_column("Event", sa.Column("EndDate", sa.Date(), nullable=True))
        op.add_column(
            "Event",
            sa.Column(
                "IsDeleted",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("0"),
            ),
        )
        op.add_column(
            "Event", sa.Column("DeletedAt", sa.DateTime(), nullable=True)
        )
        op.add_column(
            "Event",
            sa.Column("DeletedBy", sa.String(length=100), nullable=True),
        )


def downgrade() -> None:
    # Drop in reverse order
    op.drop_column("Event", "DeletedBy")
    op.drop_column("Event", "DeletedAt")
    op.drop_column("Event", "IsDeleted")
    op.drop_column("Event", "EndDate")
    op.drop_column("Event", "Timezone")