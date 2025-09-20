import datetime
from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.db import Base


class Role(Base):
    __tablename__ = "Role"

    id: Mapped[int] = mapped_column(
        "RoleID", Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column("RoleName", String(64), nullable=False)
    description: Mapped[str] = mapped_column("RoleDescription", String(255), nullable=True)
    is_system_role: Mapped[bool] = mapped_column("IsSystemRole", nullable=False, default=False)
    permissions: Mapped[str] = mapped_column("Permissions", String(1000), nullable=True)
    created_date: Mapped[datetime.datetime] = mapped_column("CreatedDate", DateTime, nullable=False, default=datetime.datetime.utcnow)
    created_by: Mapped[str] = mapped_column("CreatedBy", String(64), nullable=True)
    last_updated: Mapped[datetime.datetime] = mapped_column("LastUpdated", DateTime, nullable=True)
    updated_by: Mapped[str] = mapped_column("UpdatedBy", String(64), nullable=True)


class User(Base):
    __tablename__ = "User"

    id: Mapped[int] = mapped_column(
        "UserID", BigInteger, primary_key=True, autoincrement=True
    )
    email: Mapped[str] = mapped_column("Email", String(255), nullable=False)
    username: Mapped[str] = mapped_column("Username", String(255), nullable=False)
    first_name: Mapped[str] = mapped_column("FirstName", String(255), nullable=False)
    last_name: Mapped[str] = mapped_column("LastName", String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column("PasswordHash", String(255), nullable=True)
    password_salt: Mapped[str] = mapped_column("PasswordSalt", String(255), nullable=True)
    email_verified: Mapped[bool] = mapped_column("EmailVerified", Boolean, nullable=False, default=False)
    role_id: Mapped[int] = mapped_column("RoleID", ForeignKey("Role.RoleID"), nullable=False)
    created_date: Mapped[datetime.datetime] = mapped_column("CreatedDate", DateTime, nullable=False, default=datetime.datetime.utcnow)

    # Relationships
    role = relationship("Role")


# Token models for authentication flows
class EmailVerificationToken(Base):
    __tablename__ = "emailverificationtoken"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("User.UserID"), nullable=False
    )
    token: Mapped[str] = mapped_column(String(128), nullable=False)
    expires_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False
    )
    consumed_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.datetime.utcnow
    )

    user = relationship("User")


class PasswordResetToken(Base):
    __tablename__ = "passwordresettoken"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("User.UserID"), nullable=False
    )
    token: Mapped[str] = mapped_column(String(128), nullable=False)
    expires_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False
    )
    consumed_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.datetime.utcnow
    )

    user = relationship("User")