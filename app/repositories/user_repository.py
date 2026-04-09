import json
import uuid

from fastapi import HTTPException
from sqlalchemy import and_, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Users
from app.repositories.base_repository import BaseRepository
from app.schemas.user import (
    UserPagination,
    UserPermissionRoleResponse,
    UserResponse,
)

QUERY_USER_WITH_ROLES_PERMISSIONS = """
SELECT
    u.id,
    u.guid,
    u.name,
    u.email,
    u.username,
    u.profile_pic,
    u.city,
    u.last_login_time,
    COALESCE(r.roles, JSON_ARRAY()) AS roles,
    COALESCE(p.permissions, JSON_ARRAY()) AS permissions
FROM users u
LEFT JOIN (
    SELECT
        t.user_id,
        JSON_ARRAYAGG(t.role_name) AS roles
    FROM (
        SELECT DISTINCT
            ur.user_id,
            r.name AS role_name
        FROM user_roles ur
        JOIN roles r ON r.id = ur.role_id
        WHERE ur.active = 1
          AND ur.deleted = 0
          AND r.active = 1
          AND r.deleted = 0
    ) t
    GROUP BY t.user_id
) r ON r.user_id = u.id
LEFT JOIN (
    SELECT
        t.user_id,
        JSON_ARRAYAGG(t.permission_name) AS permissions
    FROM (
        SELECT DISTINCT
            ur.user_id,
            p.name AS permission_name
        FROM user_roles ur
        JOIN roles r ON r.id = ur.role_id
        JOIN role_permissions rp ON rp.role_id = r.id
        JOIN permissions p ON p.id = rp.permission_id
        WHERE ur.active = 1
          AND ur.deleted = 0
          AND r.active = 1
          AND r.deleted = 0
          AND rp.active = 1
          AND rp.deleted = 0
          AND p.active = 1
          AND p.deleted = 0
    ) t
    GROUP BY t.user_id
) p ON p.user_id = u.id
WHERE u.id = :user_id
  AND u.active = 1
  AND u.deleted = 0
"""


QUERY_ROLES_PERMISSIONS = """
SELECT
    COALESCE(r.roles, JSON_ARRAY()) AS roles,
    COALESCE(p.permissions, JSON_ARRAY()) AS permissions
FROM users u
LEFT JOIN (
    SELECT
        t.user_id,
        JSON_ARRAYAGG(t.role_name) AS roles
    FROM (
        SELECT DISTINCT
            ur.user_id,
            r.name AS role_name
        FROM user_roles ur
        JOIN roles r ON r.id = ur.role_id
        WHERE ur.active = 1
          AND ur.deleted = 0
          AND r.active = 1
          AND r.deleted = 0
    ) t
    GROUP BY t.user_id
) r ON r.user_id = u.id
LEFT JOIN (
    SELECT
        t.user_id,
        JSON_ARRAYAGG(t.permission_name) AS permissions
    FROM (
        SELECT DISTINCT
            ur.user_id,
            p.name AS permission_name
        FROM user_roles ur
        JOIN roles r ON r.id = ur.role_id
        JOIN role_permissions rp ON rp.role_id = r.id
        JOIN permissions p ON p.id = rp.permission_id
        WHERE ur.active = 1
          AND ur.deleted = 0
          AND r.active = 1
          AND r.deleted = 0
          AND rp.active = 1
          AND rp.deleted = 0
          AND p.active = 1
          AND p.deleted = 0
    ) t
    GROUP BY t.user_id
) p ON p.user_id = u.id
WHERE u.id = :user_id
  AND u.active = 1
  AND u.deleted = 0
"""


class UserRepository(
    BaseRepository[
        Users,
        UserResponse,
        UserPagination,
    ]
):
    def __init__(self) -> None:
        super().__init__(
            model=Users,
            response_schema=UserResponse,
            pagination_schema=UserPagination,
            not_found_message="User not found",
            already_exists_message="User already exists",
            search_fields=["username", "email", "name"],
        )

    def base_filters(self) -> list:
        return []

    def build_search_filters(self, search: str) -> list:
        if not search:
            return []
        return [
            or_(
                Users.username.ilike(f"{search}%"),
                Users.email.ilike(f"{search}%"),
                Users.name.ilike(f"{search}%"),
            )
        ]

    async def get_by_email(self, db: AsyncSession, email: str) -> Users | None:
        result = await db.execute(select(Users).where(Users.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, db: AsyncSession, username: str) -> Users | None:
        result = await db.execute(select(Users).where(Users.username == username))
        return result.scalar_one_or_none()

    async def get_active_by_email(self, db: AsyncSession, email: str) -> Users | None:
        result = await db.execute(
            select(Users).where(and_(Users.email == email, Users.deleted.is_(False)))
        )
        return result.scalar_one_or_none()

    async def get_active_by_username(
        self, db: AsyncSession, username: str
    ) -> Users | None:
        result = await db.execute(
            select(Users).where(
                and_(Users.username == username, Users.deleted.is_(False))
            )
        )
        return result.scalar_one_or_none()

    async def get_by_email_excluding_id(
        self, db: AsyncSession, email: str, user_id: str
    ) -> Users | None:
        result = await db.execute(
            select(Users).where(
                and_(
                    Users.email == email,
                    Users.id != user_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_username_excluding_id(
        self, db: AsyncSession, username: str, user_id: str
    ) -> Users | None:
        result = await db.execute(
            select(Users).where(
                and_(
                    Users.username == username,
                    Users.id != user_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def create_user_record(self, db: AsyncSession, user: Users) -> Users:
        if not user.id:
            user.id = str(uuid.uuid7())
        if not user.guid:
            user.guid = str(uuid.uuid7())

        db.add(user)
        await db.flush()
        return user

    async def hard_delete(self, db: AsyncSession, id: str) -> Users:
        user = await self.get_by_id(db=db, id=id)
        if not user:
            raise HTTPException(status_code=404, detail=self.not_found_message)

        await db.delete(user)
        await db.commit()
        return user

    async def get_user_detail(
        self, db: AsyncSession, user_id: str
    ) -> UserPermissionRoleResponse:
        result = await db.execute(
            text(QUERY_USER_WITH_ROLES_PERMISSIONS), {"user_id": user_id}
        )
        row = result.mappings().first()

        if not row:
            raise HTTPException(status_code=404, detail="User not found")

        user = dict(row)
        if isinstance(user["roles"], str):
            user["roles"] = json.loads(user["roles"])
        if isinstance(user["permissions"], str):
            user["permissions"] = json.loads(user["permissions"])

        user["roles"] = user.get("roles") or []
        user["permissions"] = user.get("permissions") or []
        return UserPermissionRoleResponse.model_validate(user)

    async def get_role_permission(self, db: AsyncSession, user_id: str) -> dict:
        result = await db.execute(text(QUERY_ROLES_PERMISSIONS), {"user_id": user_id})
        row = result.mappings().first()

        if not row:
            raise HTTPException(status_code=404, detail="User not found")

        user = dict(row)
        if isinstance(user["roles"], str):
            user["roles"] = json.loads(user["roles"])
        if isinstance(user["permissions"], str):
            user["permissions"] = json.loads(user["permissions"])

        user["roles"] = user.get("roles") or []
        user["permissions"] = user.get("permissions") or []
        return user


user_repository = UserRepository()
