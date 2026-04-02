from typing import Optional
import datetime
import enum

from sqlalchemy import (
    CHAR,
    Column,
    DateTime,
    Enum,
    ForeignKeyConstraint,
    Index,
    String,
    Table,
    Text,
    text,
)
from sqlalchemy.dialects.mysql import ENUM, TINYINT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ChatChatType(str, enum.Enum):
    DIRECT = "direct"
    GROUP = "group"


class MessageMessageType(str, enum.Enum):
    TEXT = "text"
    FILE = "file"


class Chat(Base):
    __tablename__ = "chat"
    __table_args__ = (
        Index("idx_chat_on_guid", "guid"),
        Index("idx_chat_on_is_deleted_chat_type", "deleted", "chat_type"),
        Index("uq_chat_guid", "guid", unique=True),
    )

    id: Mapped[str] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"), primary_key=True)
    guid: Mapped[str] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"), nullable=False)
    chat_type: Mapped[ChatChatType] = mapped_column(
        Enum(
            ChatChatType, values_callable=lambda cls: [member.value for member in cls]
        ),
        nullable=False,
    )
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    deleted: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, server_default=text("'0'")
    )
    active: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, server_default=text("'1'")
    )
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"))
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"))

    user: Mapped[list["Users"]] = relationship(
        "Users", secondary="chat_participant", back_populates="chat"
    )
    message: Mapped[list["Message"]] = relationship("Message", back_populates="chat")
    read_status: Mapped[list["ReadStatus"]] = relationship(
        "ReadStatus", back_populates="chat"
    )


class Permissions(Base):
    __tablename__ = "permissions"

    id: Mapped[str] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"), primary_key=True)
    name: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"), nullable=False)
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    deleted: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, server_default=text("'0'")
    )
    active: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, server_default=text("'1'")
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text(collation="utf8mb4_unicode_ci")
    )
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
    deleted: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, server_default=text("'0'")
    )
    active: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, server_default=text("'1'")
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text(collation="utf8mb4_unicode_ci")
    )
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"))
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"))

    role_permissions: Mapped[list["RolePermissions"]] = relationship(
        "RolePermissions", back_populates="role"
    )
    user_roles: Mapped[list["UserRoles"]] = relationship(
        "UserRoles", back_populates="role"
    )


class Users(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"), primary_key=True)
    guid: Mapped[str] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255, "utf8mb4_unicode_ci"), nullable=False
    )
    password: Mapped[str] = mapped_column(
        String(500, "utf8mb4_unicode_ci"), nullable=False
    )
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    deleted: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, server_default=text("'0'")
    )
    active: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, server_default=text("'1'")
    )
    is_send_email: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, server_default=text("'1'")
    )
    username: Mapped[Optional[str]] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    name: Mapped[Optional[str]] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    profile_pic: Mapped[Optional[str]] = mapped_column(
        String(255, "utf8mb4_unicode_ci")
    )
    city: Mapped[Optional[str]] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"))
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"))
    last_login_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    token: Mapped[Optional[str]] = mapped_column(Text(collation="utf8mb4_unicode_ci"))

    chat: Mapped[list["Chat"]] = relationship(
        "Chat", secondary="chat_participant", back_populates="user"
    )
    message: Mapped[list["Message"]] = relationship("Message", back_populates="user")
    read_status: Mapped[list["ReadStatus"]] = relationship(
        "ReadStatus", back_populates="user"
    )
    user_roles: Mapped[list["UserRoles"]] = relationship(
        "UserRoles", back_populates="user"
    )


t_chat_participant = Table(
    "chat_participant",
    Base.metadata,
    Column("user_id", CHAR(36, "utf8mb4_unicode_ci"), primary_key=True),
    Column("chat_id", CHAR(36, "utf8mb4_unicode_ci"), primary_key=True),
    ForeignKeyConstraint(
        ["chat_id"], ["chat.id"], ondelete="CASCADE", name="fk_chat_participant_chat"
    ),
    ForeignKeyConstraint(
        ["user_id"], ["users.id"], ondelete="CASCADE", name="fk_chat_participant_user"
    ),
    Index("fk_chat_participant_chat", "chat_id"),
)


class Message(Base):
    __tablename__ = "message"
    __table_args__ = (
        ForeignKeyConstraint(
            ["chat_id"], ["chat.id"], ondelete="CASCADE", name="fk_message_chat"
        ),
        ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_message_user"),
        Index("idx_message_on_chat_id", "chat_id"),
        Index("idx_message_on_user_id", "user_id"),
        Index("idx_message_on_user_id_chat_id", "chat_id", "user_id"),
        Index("uq_message_guid", "guid", unique=True),
    )

    id: Mapped[str] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"), primary_key=True)
    guid: Mapped[str] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"), nullable=False)
    message_type: Mapped[MessageMessageType] = mapped_column(
        Enum(
            MessageMessageType,
            values_callable=lambda cls: [member.value for member in cls],
        ),
        nullable=False,
        server_default=text("'text'"),
    )
    content: Mapped[str] = mapped_column(
        String(5000, "utf8mb4_unicode_ci"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"), nullable=False)
    chat_id: Mapped[str] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"), nullable=False)
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    deleted: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, server_default=text("'0'")
    )
    active: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, server_default=text("'1'")
    )
    file_name: Mapped[Optional[str]] = mapped_column(String(50, "utf8mb4_unicode_ci"))
    file_path: Mapped[Optional[str]] = mapped_column(String(1000, "utf8mb4_unicode_ci"))
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"))
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"))

    chat: Mapped["Chat"] = relationship("Chat", back_populates="message")
    user: Mapped["Users"] = relationship("Users", back_populates="message")


class ReadStatus(Base):
    __tablename__ = "read_status"
    __table_args__ = (
        ForeignKeyConstraint(
            ["chat_id"], ["chat.id"], ondelete="CASCADE", name="fk_read_status_chat"
        ),
        ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_read_status_user"),
        Index("idx_read_status_on_chat_id", "chat_id"),
        Index("idx_read_status_on_user_id", "user_id"),
    )

    id: Mapped[str] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"), primary_key=True)
    user_id: Mapped[str] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"), nullable=False)
    chat_id: Mapped[str] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"), nullable=False)
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    deleted: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, server_default=text("'0'")
    )
    active: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, server_default=text("'1'")
    )
    last_read_message_id: Mapped[Optional[str]] = mapped_column(
        CHAR(36, "utf8mb4_unicode_ci")
    )
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"))
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"))

    chat: Mapped["Chat"] = relationship("Chat", back_populates="read_status")
    user: Mapped["Users"] = relationship("Users", back_populates="read_status")


class RolePermissions(Base):
    __tablename__ = "role_permissions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["permission_id"], ["permissions.id"], name="role_permissions_ibfk_2"
        ),
        ForeignKeyConstraint(["role_id"], ["roles.id"], name="role_permissions_ibfk_1"),
        Index("permission_id", "permission_id"),
    )

    role_id: Mapped[str] = mapped_column(
        CHAR(36, "utf8mb4_unicode_ci"), primary_key=True
    )
    permission_id: Mapped[str] = mapped_column(
        CHAR(36, "utf8mb4_unicode_ci"), primary_key=True
    )
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    deleted: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, server_default=text("'0'")
    )
    active: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, server_default=text("'1'")
    )
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"))
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"))

    permission: Mapped["Permissions"] = relationship(
        "Permissions", back_populates="role_permissions"
    )
    role: Mapped["Roles"] = relationship("Roles", back_populates="role_permissions")


class UserRoles(Base):
    __tablename__ = "user_roles"
    __table_args__ = (
        ForeignKeyConstraint(["role_id"], ["roles.id"], name="user_roles_ibfk_2"),
        ForeignKeyConstraint(["user_id"], ["users.id"], name="user_roles_ibfk_1"),
        Index("role_id", "role_id"),
    )

    user_id: Mapped[str] = mapped_column(
        CHAR(36, "utf8mb4_unicode_ci"), primary_key=True
    )
    role_id: Mapped[str] = mapped_column(
        CHAR(36, "utf8mb4_unicode_ci"), primary_key=True
    )
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    deleted: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, server_default=text("'0'")
    )
    active: Mapped[int] = mapped_column(
        TINYINT(1), nullable=False, server_default=text("'1'")
    )
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"))
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36, "utf8mb4_unicode_ci"))

    role: Mapped["Roles"] = relationship("Roles", back_populates="user_roles")
    user: Mapped["Users"] = relationship("Users", back_populates="user_roles")
