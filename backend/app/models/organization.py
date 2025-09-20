import datetime
from sqlalchemy import BigInteger, String, DateTime, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from ..core.db import Base


class Organization(Base):
    __tablename__ = "Organization"

    id: Mapped[int] = mapped_column(
        "OrganizationID", BigInteger, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column("OrganizationName", String(255), nullable=False)
    code: Mapped[str] = mapped_column("OrganizationCode", String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column("IsActive", Boolean, nullable=False, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column("CreatedDate", DateTime, nullable=False, default=datetime.datetime.utcnow)
    created_by: Mapped[str] = mapped_column("CreatedBy", String(100), nullable=False)
    last_updated: Mapped[datetime.datetime] = mapped_column("LastUpdated", DateTime, nullable=True)
    updated_by: Mapped[str] = mapped_column("UpdatedBy", String(100), nullable=True)
    slug: Mapped[str] = mapped_column("OrganizationSlug", String(100), nullable=False, default="default-org")
    email: Mapped[str] = mapped_column("OrganizationEmail", String(320), nullable=False, default="admin@example.com")
    phone: Mapped[str] = mapped_column("OrganizationPhone", String(20), nullable=True)
    billing_address: Mapped[str] = mapped_column("BillingAddress", String(500), nullable=True)
    subscription_tier: Mapped[str] = mapped_column("SubscriptionTier", String(50), nullable=False, default="Basic")
    subscription_status: Mapped[str] = mapped_column("SubscriptionStatus", String(20), nullable=False, default="Active")
    max_users: Mapped[int] = mapped_column("MaxUsers", Integer, nullable=False, default=5)
    max_events: Mapped[int] = mapped_column("MaxEvents", Integer, nullable=False, default=10)
    
    # New fields we need to add via migration
    billing_email: Mapped[str] = mapped_column("BillingEmail", String(320), nullable=True)
    timezone: Mapped[str] = mapped_column("Timezone", String(100), nullable=False, default="UTC")
