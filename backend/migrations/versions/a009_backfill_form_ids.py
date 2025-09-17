"""Backfill default Form and attach CanvasLayout.FormID

Revision ID: a009_backfill_form_ids
Revises: a008_auth_tokens
Create Date: 2025-09-14
"""
from typing import Sequence, Union

from alembic import op


revision: str = "a009_backfill_form_ids"
down_revision: Union[str, Sequence[str], None] = "a008_auth_tokens"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create a default Form per Event that has CanvasLayouts without FormID
    bind = op.get_bind()
    dialect = bind.dialect.name if bind is not None else ""
    if dialect == "sqlite":
        op.execute(
            "INSERT INTO Form (EventID, Name, Status, CreatedDate) "
            "SELECT DISTINCT cl.EventID, 'Default Form', 'Draft', CURRENT_TIMESTAMP FROM CanvasLayout cl "
            "WHERE cl.FormID IS NULL AND cl.EventID IS NOT NULL AND NOT EXISTS (SELECT 1 FROM Form f WHERE f.EventID = cl.EventID)"
        )
        op.execute(
            "UPDATE CanvasLayout SET FormID = (SELECT f.FormID FROM Form f WHERE f.EventID = CanvasLayout.EventID LIMIT 1) "
            "WHERE FormID IS NULL AND EventID IS NOT NULL"
        )
    else:
        op.execute(
            """
            ;WITH events_with_layouts AS (
                SELECT DISTINCT cl.EventID
                FROM CanvasLayout cl
                WHERE cl.FormID IS NULL AND cl.EventID IS NOT NULL
            )
            INSERT INTO Form (EventID, Name, Status, CreatedDate)
            SELECT ewl.EventID, 'Default Form', 'Draft', GETUTCDATE()
            FROM events_with_layouts ewl
            WHERE NOT EXISTS (
              SELECT 1 FROM Form f WHERE f.EventID = ewl.EventID
            );

            UPDATE cl
            SET cl.FormID = f.FormID
            FROM CanvasLayout cl
            JOIN Form f ON f.EventID = cl.EventID
            WHERE cl.FormID IS NULL AND cl.EventID IS NOT NULL;
            """
        )


def downgrade() -> None:
    # Best-effort revert: detach FormID and delete default forms with no layouts
    bind = op.get_bind()
    dialect = bind.dialect.name if bind is not None else ""
    if dialect == "sqlite":
        op.execute("UPDATE CanvasLayout SET FormID = NULL WHERE FormID IS NOT NULL;")
        op.execute(
            "DELETE FROM Form WHERE Name = 'Default Form' AND Status = 'Draft' AND FormID NOT IN (SELECT DISTINCT FormID FROM CanvasLayout WHERE FormID IS NOT NULL);"
        )
    else:
        op.execute(
            """
            UPDATE CanvasLayout SET FormID = NULL WHERE FormID IS NOT NULL;
            DELETE f
            FROM Form f
            LEFT JOIN CanvasLayout cl ON cl.FormID = f.FormID
            WHERE cl.FormID IS NULL AND f.Name = 'Default Form' AND f.Status = 'Draft';
            """
        )
