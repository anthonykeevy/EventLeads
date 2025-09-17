"""Email verification and password reset token tables

Revision ID: a008_auth_tokens
Revises: a007_event_day_entitlement
Create Date: 2025-09-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a008_auth_tokens"
down_revision: Union[str, Sequence[str], None] = "a007_event_day_entitlement"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name if bind is not None else ""
    inspector = sa.inspect(bind)
    utc_default = sa.text("CURRENT_TIMESTAMP") if dialect == "sqlite" else sa.text("GETUTCDATE()")

    if not inspector.has_table("EmailVerificationToken"):
        op.create_table(
            "EmailVerificationToken",
            sa.Column("Id", sa.BigInteger(), primary_key=True, autoincrement=True),
            sa.Column("UserID", sa.BigInteger(), sa.ForeignKey("[User].UserID"), nullable=False),
            sa.Column("Token", sa.String(length=128), nullable=False),
            sa.Column("ExpiresAt", sa.DateTime(), nullable=False),
            sa.Column("ConsumedAt", sa.DateTime(), nullable=True),
            sa.Column(
                "CreatedAt", sa.DateTime(), nullable=False, server_default=utc_default
            ),
        )
        op.create_index(
            "IX_EmailVerificationToken_User",
            "EmailVerificationToken",
            ["UserID"],
        )
        op.create_index(
            "IX_EmailVerificationToken_Expires",
            "EmailVerificationToken",
            ["ExpiresAt"],
        )

    if not inspector.has_table("PasswordResetToken"):
        op.create_table(
            "PasswordResetToken",
            sa.Column("Id", sa.BigInteger(), primary_key=True, autoincrement=True),
            sa.Column("UserID", sa.BigInteger(), sa.ForeignKey("[User].UserID"), nullable=False),
            sa.Column("Token", sa.String(length=128), nullable=False),
            sa.Column("ExpiresAt", sa.DateTime(), nullable=False),
            sa.Column("ConsumedAt", sa.DateTime(), nullable=True),
            sa.Column(
                "CreatedAt", sa.DateTime(), nullable=False, server_default=utc_default
            ),
        )
        op.create_index(
            "IX_PasswordResetToken_User", "PasswordResetToken", ["UserID"]
        )
        op.create_index(
            "IX_PasswordResetToken_Expires",
            "PasswordResetToken",
            ["ExpiresAt"],
        )


def downgrade() -> None:
    op.drop_index("IX_PasswordResetToken_Expires", table_name="PasswordResetToken")
    op.drop_index("IX_PasswordResetToken_User", table_name="PasswordResetToken")
    op.drop_table("PasswordResetToken")

    op.drop_index("IX_EmailVerificationToken_Expires", table_name="EmailVerificationToken")
    op.drop_index("IX_EmailVerificationToken_User", table_name="EmailVerificationToken")
    op.drop_table("EmailVerificationToken")
