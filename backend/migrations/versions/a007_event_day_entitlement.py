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


def _fk_type(table: str, column: str) -> sa.types.TypeEngine:
    bind = op.get_bind()
    dialect = bind.dialect.name if bind is not None else ""
    if dialect == "mssql":
        result = bind.execute(
            sa.text(
                "SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = :t AND COLUMN_NAME = :c"
            ),
            {"t": table, "c": column},
        ).first()
        dt = (result[0].lower() if result and result[0] else "int")
        if dt == "bigint":
            return sa.BigInteger()
        return sa.Integer()
    return sa.BigInteger()


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name if bind is not None else ""
    utc_default = sa.text("CURRENT_TIMESTAMP") if dialect == "sqlite" else sa.text("GETUTCDATE()")

    org_fk = _fk_type("Organization", "OrganizationID")
    event_fk = _fk_type("Event", "EventID")
    invoice_fk = _fk_type("Invoice", "InvoiceID")

    op.create_table(
        "EventDayEntitlement",
        sa.Column(
            "EventDayEntitlementID",
            sa.BigInteger(),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column("OrganizationID", org_fk, nullable=False),
        sa.Column("EventID", event_fk, nullable=False),
        sa.Column("EntitlementDate", sa.Date(), nullable=False),
        sa.Column("Amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("InvoiceID", invoice_fk, nullable=True),
        sa.Column(
            "CreatedDate", sa.DateTime(), nullable=False, server_default=utc_default
        ),
        sa.Column("CreatedBy", sa.String(length=100), nullable=True),
    )
    # Add FKs after create to allow conditional existence checks
    inspector = sa.inspect(bind)
    if inspector.has_table("Organization"):
        op.create_foreign_key(
            "FK_EventDayEntitlement_Organization",
            "EventDayEntitlement",
            "Organization",
            ["OrganizationID"],
            ["OrganizationID"],
        )
    if inspector.has_table("Event"):
        op.create_foreign_key(
            "FK_EventDayEntitlement_Event",
            "EventDayEntitlement",
            "Event",
            ["EventID"],
            ["EventID"],
        )
    if inspector.has_table("Invoice"):
        op.create_foreign_key(
            "FK_EventDayEntitlement_Invoice",
            "EventDayEntitlement",
            "Invoice",
            ["InvoiceID"],
            ["InvoiceID"],
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
    bind = op.get_bind()
    dialect = bind.dialect.name if bind is not None else ""
    if dialect == "sqlite":
        op.execute("DROP INDEX IF EXISTS UQ_EventDayEntitlement_Event_Date")
    else:
        op.drop_constraint(
            "UQ_EventDayEntitlement_Event_Date",
            "EventDayEntitlement",
            type_="unique",
        )
    op.drop_table("EventDayEntitlement")
