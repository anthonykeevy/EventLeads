"""EventDayEntitlement table for prepaid access days

Revision ID: a007_event_day_entitlement
Revises: a006_seed_objecttypes
Create Date: 2025-09-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a007_event_day_entitlement"
down_revision: Union[str, Sequence[str], None] = "a006_seed_objecttypes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name if bind is not None else ""
    utc_default = sa.text("CURRENT_TIMESTAMP") if dialect == "sqlite" else sa.text("GETUTCDATE()")
    op.create_table(
        "EventDayEntitlement",
        sa.Column("EventDayEntitlementID", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("OrganizationID", sa.Integer(), sa.ForeignKey("Organization.OrganizationID"), nullable=False),
        sa.Column("EventID", sa.Integer(), sa.ForeignKey("Event.EventID"), nullable=False),
        sa.Column("EntitlementDate", sa.Date(), nullable=False),
        sa.Column("Amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("InvoiceID", sa.Integer(), sa.ForeignKey("Invoice.InvoiceID"), nullable=True),
        sa.Column("CreatedDate", sa.DateTime(), nullable=False, server_default=utc_default),
        sa.Column("CreatedBy", sa.String(length=100), nullable=True),
    )
    if dialect == "sqlite":
        op.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS UQ_EventDayEntitlement_Event_Date ON EventDayEntitlement(EventID, EntitlementDate)"
        )
    else:
        op.create_unique_constraint(
            "UQ_EventDayEntitlement_Event_Date", "EventDayEntitlement", ["EventID", "EntitlementDate"]
        )


def downgrade() -> None:
    if dialect == "sqlite":
        op.execute("DROP INDEX IF EXISTS UQ_EventDayEntitlement_Event_Date")
    else:
        op.drop_constraint("UQ_EventDayEntitlement_Event_Date", "EventDayEntitlement", type_="unique")
    op.drop_table("EventDayEntitlement")
