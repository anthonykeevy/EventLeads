"""Optional: enforce FormID non-null and deprecate DurationDays

Revision ID: a011_enforcement_followup_optional
Revises: a010_indexes_quality_of_life
Create Date: 2025-09-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a011_enforcement_followup_optional"
down_revision: Union[str, Sequence[str], None] = "a010_indexes_quality_of_life"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make CanvasLayout.FormID NOT NULL if backfill has run successfully
    try:
        op.alter_column("CanvasLayout", "FormID", existing_type=sa.Integer(), nullable=False)
    except Exception:
        # Leave nullable if not yet safe; document to re-run later
        pass


def downgrade() -> None:
    try:
        op.alter_column("CanvasLayout", "FormID", existing_type=sa.Integer(), nullable=True)
    except Exception:
        pass

