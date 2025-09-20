"""Create Invitation table with indexes

Revision ID: a016_invitation_table
Revises: a015_globalsetting_table
Create Date: 2025-09-18
"""
from typing import Sequence, Union

from alembic import op  # type: ignore[attr-defined]
import sqlalchemy as sa


revision: str = "a016_invitation_table"
down_revision: Union[str, Sequence[str], None] = (
    "a015_globalsetting_table"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()  # type: ignore[attr-defined]
    dialect = bind.dialect.name if bind is not None else ""

    op.create_table(
        "Invitation",
        sa.Column("InvitationID", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("OrganizationID", sa.BigInteger(), nullable=False),
        sa.Column("Email", sa.String(length=320), nullable=False),
        sa.Column("Role", sa.String(length=50), nullable=False),
        sa.Column("Token", sa.String(length=128), nullable=False, unique=True),
        sa.Column("ExpiresAt", sa.DateTime(), nullable=False),
        sa.Column("ConsumedAt", sa.DateTime(), nullable=True),
        sa.Column("CreatedBy", sa.BigInteger(), nullable=True),
        sa.Column("CreatedAt", sa.DateTime(), nullable=False, server_default=sa.text("GETDATE()" if dialect == "mssql" else "CURRENT_TIMESTAMP")),
    )

    # Helpful indexes
    op.create_index("IX_Invitation_Org_CreatedAt", "Invitation", ["OrganizationID", "CreatedAt"])  # type: ignore[attr-defined]
    op.create_index("IX_Invitation_Email", "Invitation", ["Email"])  # type: ignore[attr-defined]


def downgrade() -> None:
    op.drop_index("IX_Invitation_Email", table_name="Invitation")  # type: ignore[attr-defined]
    op.drop_index("IX_Invitation_Org_CreatedAt", table_name="Invitation")  # type: ignore[attr-defined]
    op.drop_table("Invitation")  # type: ignore[attr-defined]




