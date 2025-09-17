"""Create CanvasLayout table linked to Form

Revision ID: a014_canvaslayout_table
Revises: a013_convert_boolean_fields_to_bit
Create Date: 2025-09-17
"""
from typing import Sequence, Union

from alembic import op  # type: ignore[attr-defined]
import sqlalchemy as sa


revision: str = "a014_canvaslayout_table"
down_revision: Union[str, Sequence[str], None] = (
    "a013_convert_boolean_fields_to_bit"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()  # type: ignore[attr-defined]
    dialect = bind.dialect.name if bind is not None else ""

    op.create_table(
        "CanvasLayout",
        sa.Column(
            "CanvasLayoutID", sa.BigInteger(), primary_key=True, autoincrement=True
        ),
        sa.Column("FormID", sa.BigInteger(), nullable=False),
        sa.Column("DeviceType", sa.String(length=32), nullable=False),
        sa.Column("AspectRatio", sa.String(length=16), nullable=False),
        sa.Column("ResolutionX", sa.Integer(), nullable=False),
        sa.Column("ResolutionY", sa.Integer(), nullable=False),
        sa.Column(
            "RevisionNumber",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1"),
        ),
        sa.Column(
            "IsDeleted",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("DeletedAt", sa.DateTime(), nullable=True),
        sa.Column("DeletedBy", sa.String(length=100), nullable=True),
    )
    # Add FK if supported
    if dialect != "sqlite":
        op.create_foreign_key(  # type: ignore[attr-defined]
            "FK_CanvasLayout_Form",
            "CanvasLayout",
            "Form",
            ["FormID"],
            ["FormID"],
        )


def downgrade() -> None:
    bind = op.get_bind()  # type: ignore[attr-defined]
    dialect = bind.dialect.name if bind is not None else ""
    if dialect != "sqlite":
        op.drop_constraint(  # type: ignore[attr-defined]
            "FK_CanvasLayout_Form", "CanvasLayout", type_="foreignkey"
        )
    op.drop_table("CanvasLayout")  # type: ignore[attr-defined]


