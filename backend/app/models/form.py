import datetime
from sqlalchemy import BigInteger, ForeignKey, String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from ..core.db import Base


class Form(Base):
    __tablename__ = "Form"

    id: Mapped[int] = mapped_column(
        "FormID", BigInteger, primary_key=True, autoincrement=True
    )
    event_id: Mapped[int] = mapped_column(
        "EventID", ForeignKey("Event.EventID"), nullable=False
    )
    name: Mapped[str] = mapped_column("Name", String(300), nullable=False)
    status: Mapped[str] = mapped_column(
        "Status", String(50), nullable=False, default="Draft"
    )
    public_slug: Mapped[str | None] = mapped_column(
        "PublicSlug", String(80), nullable=True
    )
    # Soft delete and audit fields
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
    created_by: Mapped[str | None] = mapped_column(
        "CreatedBy", String(100), nullable=True
    )
    last_updated: Mapped[datetime.datetime | None] = mapped_column(
        "LastUpdated", DateTime, nullable=True
    )
    updated_by: Mapped[str | None] = mapped_column(
        "UpdatedBy", String(100), nullable=True
    )


