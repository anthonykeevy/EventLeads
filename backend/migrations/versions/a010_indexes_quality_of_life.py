"""Add QoL indexes for performance

Revision ID: a010_indexes_quality_of_life
Revises: a009_backfill_form_ids
Create Date: 2025-09-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a010_indexes_quality_of_life"
down_revision: Union[str, Sequence[str], None] = "a009_backfill_form_ids"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from alembic import op as _op
    bind = _op.get_bind()
    dialect = bind.dialect.name if bind is not None else ""
    inspector = sa.inspect(bind)
    if dialect == "sqlite":
        op.execute("CREATE INDEX IF NOT EXISTS IDX_Lead_Event_SubmittedAt ON Lead(EventID, SubmittedAt)")
        op.execute("CREATE INDEX IF NOT EXISTS IDX_Lead_Form_IsTest ON Lead(FormID, IsTest)")
        op.execute(
            "CREATE INDEX IF NOT EXISTS IDX_EventDayEntitlement_Event_Date ON EventDayEntitlement(EventID, EntitlementDate)"
        )
        op.execute("CREATE INDEX IF NOT EXISTS IDX_CanvasLayout_Form ON CanvasLayout(FormID)")
    else:
        if inspector.has_table("Lead"):
            op.execute(
                "CREATE INDEX IDX_Lead_Event_SubmittedAt ON Lead(EventID, SubmittedAt DESC)"
            )
            op.execute("CREATE INDEX IDX_Lead_Form_IsTest ON Lead(FormID, IsTest)")
        if inspector.has_table("EventDayEntitlement"):
            op.execute(
                "CREATE INDEX IDX_EventDayEntitlement_Event_Date ON EventDayEntitlement(EventID, EntitlementDate)"
            )
        if inspector.has_table("CanvasLayout"):
            op.execute("CREATE INDEX IDX_CanvasLayout_Form ON CanvasLayout(FormID)")


def downgrade() -> None:
    from alembic import op as _op
    bind = _op.get_bind()
    dialect = bind.dialect.name if bind is not None else ""
    inspector = sa.inspect(bind)
    if dialect == "sqlite":
        op.execute("DROP INDEX IF EXISTS IDX_CanvasLayout_Form")
        op.execute("DROP INDEX IF EXISTS IDX_EventDayEntitlement_Event_Date")
        op.execute("DROP INDEX IF EXISTS IDX_Lead_Form_IsTest")
        op.execute("DROP INDEX IF EXISTS IDX_Lead_Event_SubmittedAt")
    else:
        if inspector.has_table("CanvasLayout"):
            op.execute("DROP INDEX IDX_CanvasLayout_Form ON CanvasLayout")
        if inspector.has_table("EventDayEntitlement"):
            op.execute(
                "DROP INDEX IDX_EventDayEntitlement_Event_Date ON EventDayEntitlement"
            )
        if inspector.has_table("Lead"):
            op.execute("DROP INDEX IDX_Lead_Form_IsTest ON Lead")
            op.execute("DROP INDEX IDX_Lead_Event_SubmittedAt ON Lead")
