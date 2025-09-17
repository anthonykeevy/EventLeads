from sqlalchemy import BigInteger, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from ..core.db import Base


class AuthEvent(Base):
    __tablename__ = "AuthEvent"

    AuthEventID: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    OrganizationID: Mapped[int | None] = mapped_column(Integer, nullable=True)
    UserID: Mapped[int | None] = mapped_column(Integer, nullable=True)
    Email: Mapped[str | None] = mapped_column(String(256), nullable=True)
    EventType: Mapped[str] = mapped_column(String(64), nullable=False)
    Status: Mapped[str] = mapped_column(String(16), nullable=False)
    ReasonCode: Mapped[str | None] = mapped_column(String(64), nullable=True)
    RequestID: Mapped[str | None] = mapped_column(String(64), nullable=True)
    IP: Mapped[str | None] = mapped_column(String(64), nullable=True)
    UserAgent: Mapped[str | None] = mapped_column(String(256), nullable=True)
    CreatedDate: Mapped[str | None] = mapped_column(DateTime, nullable=True)

