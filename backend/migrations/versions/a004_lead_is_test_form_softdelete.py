"""Lead: add is_test, form_id, soft-delete metadata

Revision ID: a004_lead_is_test_form_softdelete
Revises: a003_canvaslayout_softdelete
Create Date: 2025-09-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a004_lead_is_test_form_softdelete"
down_revision: Union[str, Sequence[str], None] = "a003_canvaslayout_softdelete"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name if bind is not None else ""
    # Ensure alembic_version.version_num can store this revision id length
    if dialect == "mssql":
        # Widen alembic_version.version_num to store long revision ids
        op.execute(
            "IF EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'alembic_version_pkc') "
            "ALTER TABLE alembic_version DROP CONSTRAINT alembic_version_pkc"
        )
        op.execute(
            "ALTER TABLE alembic_version ALTER COLUMN version_num NVARCHAR(64) NOT NULL"
        )
        op.execute(
            "ALTER TABLE alembic_version ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)"
        )
    inspector = sa.inspect(bind)
    if not inspector.has_table("Lead"):
        # Table not present in this environment; skip
        return
    op.add_column(
        "Lead",
        sa.Column(
            "IsTest", sa.Boolean(), nullable=False, server_default=sa.text("0")
        ),
    )
    op.add_column("Lead", sa.Column("FormID", sa.BigInteger(), nullable=True))
    if dialect != "sqlite":
        op.create_foreign_key(
            "FK_Lead_Form", "Lead", "Form", ["FormID"], ["FormID"]
        )
    op.add_column("Lead", sa.Column("DeletedAt", sa.DateTime(), nullable=True))
    op.add_column(
        "Lead", sa.Column("DeletedBy", sa.String(length=100), nullable=True)
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("Lead"):
        return
    op.drop_column("Lead", "DeletedBy")
    op.drop_column("Lead", "DeletedAt")
    dialect = bind.dialect.name if bind is not None else ""
    if dialect != "sqlite":
        op.drop_constraint("FK_Lead_Form", "Lead", type_="foreignkey")
    op.drop_column("Lead", "FormID")
    op.drop_column("Lead", "IsTest")
