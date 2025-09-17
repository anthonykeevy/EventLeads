import datetime
from sqlalchemy import BigInteger, ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from ..core.db import Base


class Event(Base):
    __tablename__ = "Event"

    id: Mapped[int] = mapped_column(
        "EventID", BigInteger, primary_key=True, autoincrement=True
    )
    org_id: Mapped[int] = mapped_column(
        "OrganizationID", ForeignKey("Organization.OrganizationID"), nullable=False
    )
    name: Mapped[str] = mapped_column("Name", String(255), nullable=False)
    status: Mapped[str] = mapped_column("Status", String(32), nullable=False, default="draft")
    created_date: Mapped[datetime.datetime] = mapped_column("CreatedDate", DateTime, nullable=False, default=datetime.datetime.utcnow)
