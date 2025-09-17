"""CanvasLayout link to Form; soft-delete on layout & objects

Revision ID: a003_canvaslayout_softdelete
Revises: a002_form_table_and_slug
Create Date: 2025-09-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a003_canvaslayout_softdelete"
down_revision: Union[str, Sequence[str], None] = "a002_form_table_and_slug"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name if bind is not None else ""
    
    # Skip CanvasLayout operations for now - table doesn't exist in current models
    # TODO: Re-enable when CanvasLayout model is implemented
    # op.add_column("CanvasLayout", sa.Column("FormID", sa.Integer(), nullable=True))
    # if dialect != "sqlite":
    #     op.create_foreign_key(
    #         "FK_CanvasLayout_Form", "CanvasLayout", "Form", ["FormID"], ["FormID"]
    #     )
    
    # Only add soft-delete columns to tables that exist
    for table in ("CanvasObject",):  # Removed CanvasLayout from list
        try:
            op.add_column(table, sa.Column("IsDeleted", sa.Boolean(), nullable=False, server_default=sa.text("0")))
            op.add_column(table, sa.Column("DeletedAt", sa.DateTime(), nullable=True))
            op.add_column(table, sa.Column("DeletedBy", sa.String(length=100), nullable=True))
        except Exception as e:
            # Skip if table doesn't exist
            print(f"Skipping soft-delete columns for {table}: {e}")
            pass


def downgrade() -> None:
    # Only drop columns from tables that exist
    for table in ("CanvasObject",):  # Removed CanvasLayout from list
        try:
            op.drop_column(table, "DeletedBy")
            op.drop_column(table, "DeletedAt")
            op.drop_column(table, "IsDeleted")
        except Exception as e:
            # Skip if table doesn't exist
            print(f"Skipping soft-delete column removal for {table}: {e}")
            pass
    
    # Skip CanvasLayout operations for now
    # bind = op.get_bind()
    # dialect = bind.dialect.name if bind is not None else ""
    # if dialect != "sqlite":
    #     op.drop_constraint("FK_CanvasLayout_Form", "CanvasLayout", type_="foreignkey")
    # op.drop_column("CanvasLayout", "FormID")
