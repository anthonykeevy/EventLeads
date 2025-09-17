from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column
from ..core.db import Base


class Organization(Base):
    __tablename__ = "organization"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
