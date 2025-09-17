"""Optional: UsageCharge table for accounting/audit

Revision ID: a005_usagecharge_optional
Revises: a004_lead_is_test_form_softdelete
Create Date: 2025-09-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a005_usagecharge_optional"
down_revision: Union[str, Sequence[str], None] = "a004_lead_is_test_form_softdelete"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name if bind is not None else ""
    utc_default = sa.text("CURRENT_TIMESTAMP") if dialect == "sqlite" else sa.text("GETUTCDATE()")
    op.create_table(
        "UsageCharge",
        sa.Column("UsageChargeID", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("OrganizationID", sa.Integer(), sa.ForeignKey("Organization.OrganizationID"), nullable=False),
        sa.Column("EventID", sa.Integer(), sa.ForeignKey("Event.EventID"), nullable=False),
        sa.Column("ChargeDate", sa.Date(), nullable=False),
        sa.Column("Amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("Source", sa.String(length=50), nullable=False),
        sa.Column("CreatedDate", sa.DateTime(), nullable=False, server_default=utc_default),
        sa.Column("CreatedBy", sa.String(length=100), nullable=True),
    )
    if dialect == "sqlite":
        op.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS UQ_UsageCharge_Event_Date_Source ON UsageCharge(EventID, ChargeDate, Source)"
        )
    else:
        op.create_unique_constraint(
            "UQ_UsageCharge_Event_Date_Source", "UsageCharge", ["EventID", "ChargeDate", "Source"]
        )


def downgrade() -> None:
    if dialect == "sqlite":
        op.execute(
            "DROP INDEX IF EXISTS UQ_UsageCharge_Event_Date_Source"
        )
    else:
        op.drop_constraint("UQ_UsageCharge_Event_Date_Source", "UsageCharge", type_="unique")
    op.drop_table("UsageCharge")
