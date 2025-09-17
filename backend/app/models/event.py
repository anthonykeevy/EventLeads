import datetime
from sqlalchemy import BigInteger, ForeignKey, String, DateTime, Boolean, Date
from sqlalchemy.orm import Mapped, mapped_column
from ..core.db import Base


class Event(Base):
    __tablename__ = "Event"

    id: Mapped[int] = mapped_column(
        "EventID", BigInteger, primary_key=True, autoincrement=True
    )
    org_id: Mapped[int] = mapped_column(
        "OrganizationID",
        ForeignKey("Organization.OrganizationID"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column("Name", String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        "Status", String(32), nullable=False, default="draft"
    )
    # v0.2 fields per docs/shards/02-data-schema.md
    timezone: Mapped[str] = mapped_column(
        "Timezone", String(64), nullable=False, default="UTC"
    )
    start_date: Mapped[datetime.date | None] = mapped_column(
        "StartDate", Date, nullable=True
    )
    end_date: Mapped[datetime.date | None] = mapped_column(
        "EndDate", Date, nullable=True
    )
    # Soft delete per shard standards
    is_deleted: Mapped[bool] = mapped_column(
        "IsDeleted", Boolean, nullable=False, default=False
    )
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(
        "DeletedAt", DateTime, nullable=True
    )
    deleted_by: Mapped[str | None] = mapped_column(
        "DeletedBy", String(100), nullable=True
    )
    created_date: Mapped[datetime.datetime] = mapped_column(
        "CreatedDate",
        DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
    )
