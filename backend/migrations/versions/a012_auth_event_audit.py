"""AuthEvent audit table for authentication interactions

Revision ID: a012_auth_event_audit
Revises: a011_enforcement_followup_optional
Create Date: 2025-09-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a012_auth_event_audit"
down_revision: Union[str, Sequence[str], None] = "a011_enforcement_followup_optional"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name if bind is not None else ""
    utc_default = sa.text("CURRENT_TIMESTAMP") if dialect == "sqlite" else sa.text("GETUTCDATE()")

    op.create_table(
        "AuthEvent",
        sa.Column("AuthEventID", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("OrganizationID", sa.Integer(), nullable=True),
        sa.Column("UserID", sa.Integer(), nullable=True),
        sa.Column("Email", sa.String(length=256), nullable=True),
        sa.Column("EventType", sa.String(length=64), nullable=False),
        sa.Column("Status", sa.String(length=16), nullable=False),
        sa.Column("ReasonCode", sa.String(length=64), nullable=True),
        sa.Column("RequestID", sa.String(length=64), nullable=True),
        sa.Column("IP", sa.String(length=64), nullable=True),
        sa.Column("UserAgent", sa.String(length=256), nullable=True),
        sa.Column("CreatedDate", sa.DateTime(), nullable=False, server_default=utc_default),
    )

    # Helpful indexes
    op.create_index("IX_AuthEvent_CreatedDate", "AuthEvent", ["CreatedDate"]) 
    op.create_index("IX_AuthEvent_Email", "AuthEvent", ["Email"]) 
    op.create_index("IX_AuthEvent_EventType", "AuthEvent", ["EventType"]) 
    op.create_index("IX_AuthEvent_Status", "AuthEvent", ["Status"]) 


def downgrade() -> None:
    op.drop_index("IX_AuthEvent_Status", table_name="AuthEvent")
    op.drop_index("IX_AuthEvent_EventType", table_name="AuthEvent")
    op.drop_index("IX_AuthEvent_Email", table_name="AuthEvent")
    op.drop_index("IX_AuthEvent_CreatedDate", table_name="AuthEvent")
    op.drop_table("AuthEvent")

