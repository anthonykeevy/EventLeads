import datetime
from sqlalchemy import (
    BigInteger,
    ForeignKey,
    String,
    DateTime,
    Boolean,
    Integer,
)
from sqlalchemy.orm import Mapped, mapped_column
from ..core.db import Base


class CanvasLayout(Base):
    __tablename__ = "CanvasLayout"
    id: Mapped[int] = mapped_column(
        "CanvasLayoutID", BigInteger, primary_key=True, autoincrement=True
    )
    form_id: Mapped[int] = mapped_column(
        "FormID", ForeignKey("Form.FormID"), nullable=False
    )
    device_type: Mapped[str] = mapped_column(
        "DeviceType", String(32), nullable=False
    )
    aspect_ratio: Mapped[str] = mapped_column(
        "AspectRatio", String(16), nullable=False
    )
    resolution_x: Mapped[int] = mapped_column(
        "ResolutionX", Integer, nullable=False
    )
    resolution_y: Mapped[int] = mapped_column(
        "ResolutionY", Integer, nullable=False
    )
    revision_number: Mapped[int] = mapped_column(
        "RevisionNumber", Integer, nullable=False, default=1
    )
    is_deleted: Mapped[bool] = mapped_column(
        "IsDeleted", Boolean, nullable=False, default=False
    )
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(
        "DeletedAt", DateTime, nullable=True
    )
    deleted_by: Mapped[str | None] = mapped_column(
        "DeletedBy", String(100), nullable=True
    )
