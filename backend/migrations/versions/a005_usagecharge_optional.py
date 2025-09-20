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


def _fk_type(table: str, column: str) -> sa.types.TypeEngine:
    bind = op.get_bind()
    dialect = bind.dialect.name if bind is not None else ""
    if dialect == "mssql":
        result = bind.execute(
            sa.text(
                "SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_NAME = :t AND COLUMN_NAME = :c"
            ),
            {"t": table, "c": column},
        ).first()
        data_type = (result[0].lower() if result and result[0] else "int")
        if data_type == "bigint":
            return sa.BigInteger()
        return sa.Integer()
    return sa.BigInteger()


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name if bind is not None else ""
    utc_default = sa.text("CURRENT_TIMESTAMP") if dialect == "sqlite" else sa.text("GETUTCDATE()")

    org_fk_type = _fk_type("Organization", "OrganizationID")
    event_fk_type = _fk_type("Event", "EventID")

    op.create_table(
        "UsageCharge",
        sa.Column("UsageChargeID", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("OrganizationID", org_fk_type, sa.ForeignKey("Organization.OrganizationID"), nullable=False),
        sa.Column("EventID", event_fk_type, sa.ForeignKey("Event.EventID"), nullable=False),
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
    bind = op.get_bind()
    dialect = bind.dialect.name if bind is not None else ""
    if dialect == "sqlite":
        op.execute(
            "DROP INDEX IF EXISTS UQ_UsageCharge_Event_Date_Source"
        )
    else:
        op.drop_constraint(
            "UQ_UsageCharge_Event_Date_Source", "UsageCharge", type_="unique"
        )
    op.drop_table("UsageCharge")
