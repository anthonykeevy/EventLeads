"""create_default_organization

Revision ID: 07daad67e877
Revises: a018_add_organization_billing_fields
Create Date: 2025-09-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = 'a019_create_default_organization'
down_revision = 'a018_add_organization_billing_fields'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(text(
        """
        IF NOT EXISTS (SELECT 1 FROM Organization WHERE OrganizationCode = 'DEFAULT')
        BEGIN
            INSERT INTO Organization (OrganizationName, OrganizationCode, IsActive, CreatedDate, CreatedBy, OrganizationSlug, OrganizationEmail, SubscriptionTier, SubscriptionStatus, MaxUsers, MaxEvents, Timezone)
            VALUES ('Default Organization', 'DEFAULT', 1, GETUTCDATE(), 'system', 'default-org', 'admin@example.com', 'Basic', 'Active', 5, 10, 'UTC')
        END
        """
    ))


def downgrade():
    conn = op.get_bind()
    conn.execute(text(
        """
        DELETE FROM Organization WHERE OrganizationCode = 'DEFAULT'
        """
    ))
