from typing import Optional
import datetime

from sqlalchemy import CHAR, DateTime, ForeignKeyConstraint, Index, String, Text, text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Permissions(Base):
    __tablename__ = "permissions"

    id: Mapped[str] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"), primary_key=True)
    name: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"), nullable=False)
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    deleted: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"))
    active: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'1'"))
    description: Mapped[Optional[str]] = mapped_column(Text(collation="utf8mb4_unicode_ci"))
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"))
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"))

    role_permissions: Mapped[list["RolePermissions"]] = relationship(
        "RolePermissions", back_populates="permission"
    )


class Roles(Base):
    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"), primary_key=True)
    name: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"), nullable=False)
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    deleted: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"))
    active: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'1'"))
    description: Mapped[Optional[str]] = mapped_column(Text(collation="utf8mb4_unicode_ci"))
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"))
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"))

    role_permissions: Mapped[list["RolePermissions"]] = relationship(
        "RolePermissions", back_populates="role"
    )
    user_roles: Mapped[list["UserRoles"]] = relationship("UserRoles", back_populates="role")


class Users(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"), primary_key=True)
    email: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"), nullable=False)
    password: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"), nullable=False)
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    deleted: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"))
    active: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'1'"))
    is_send_email: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'1'"))
    username: Mapped[Optional[str]] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    name: Mapped[Optional[str]] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    profile_pic: Mapped[Optional[str]] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    city: Mapped[Optional[str]] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"))
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"))
    last_login_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    token: Mapped[Optional[str]] = mapped_column(Text(collation="utf8mb4_unicode_ci"))

    user_roles: Mapped[list["UserRoles"]] = relationship("UserRoles", back_populates="user")


class RolePermissions(Base):
    __tablename__ = "role_permissions"
    __table_args__ = (
        ForeignKeyConstraint(["permission_id"], ["permissions.id"], name="role_permissions_ibfk_2"),
        ForeignKeyConstraint(["role_id"], ["roles.id"], name="role_permissions_ibfk_1"),
        Index("permission_id", "permission_id"),
    )

    role_id: Mapped[str] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"), primary_key=True)
    permission_id: Mapped[str] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"), primary_key=True)
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    deleted: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"))
    active: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'1'"))
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"))
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"))

    permission: Mapped["Permissions"] = relationship("Permissions", back_populates="role_permissions")
    role: Mapped["Roles"] = relationship("Roles", back_populates="role_permissions")


class UserRoles(Base):
    __tablename__ = "user_roles"
    __table_args__ = (
        ForeignKeyConstraint(["role_id"], ["roles.id"], name="user_roles_ibfk_2"),
        ForeignKeyConstraint(["user_id"], ["users.id"], name="user_roles_ibfk_1"),
        Index("role_id", "role_id"),
    )

    user_id: Mapped[str] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"), primary_key=True)
    role_id: Mapped[str] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"), primary_key=True)
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    deleted: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"))
    active: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'1'"))
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"))
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"))

    role: Mapped["Roles"] = relationship("Roles", back_populates="user_roles")
    user: Mapped["Users"] = relationship("Users", back_populates="user_roles")

