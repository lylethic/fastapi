import json
import os
from uuid import uuid4
import uuid

from fastapi import Depends, File, HTTPException, UploadFile

from sqlalchemy import func, or_, select, text, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import UPLOAD_DIR
from app.db.models import Users
from app.providers.baseProvider import BaseProvider
from app.utils.token_utils import hash_password

from app.schemas.base_schema import BaseQueryPaginationRequest

from app.services.user_role_service import create as create_user_role
from app.services.role_service import get_role_by_id, get_role_by_name

from app.schemas.user import (
    UserCreateBody,
    UserRegisterBody,
    UserUpdateBody,
    UserResponse,
    UserPagination,
)
from app.schemas.user_role import UserRoleCreateBody

os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


class UserService(
    BaseProvider[
        Users,
        UserCreateBody,
        UserUpdateBody,
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

    async def validate_update(
        self, db: AsyncSession, db_obj: Users, body: UserUpdateBody
    ) -> None:
        if body.email is not None:
            email_result = await db.execute(
                select(Users).where(
                    and_(
                        Users.email == body.email,
                        Users.id != db_obj.id,
                    )
                )
            )
            if email_result.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Email already exists")

        if body.username is not None:
            username_result = await db.execute(
                select(Users).where(
                    and_(
                        Users.username == body.username,
                        Users.id != db_obj.id,
                    )
                )
            )
            if username_result.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Username already exists")

    def map_update_data(self, body: UserUpdateBody) -> dict:
        data = body.model_dump(exclude_unset=True)
        if data.get("password"):
            data["password"] = hash_password(data["password"])
        return data


user_service = UserService()


# create
async def create_user(db: AsyncSession, body: UserCreateBody) -> Users:
    email_result = await db.execute(select(Users).where(Users.email == body.email))
    existing_email = email_result.scalar_one_or_none()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    username_result = await db.execute(
        select(Users).where(Users.username == body.username)
    )
    existing_username = username_result.scalar_one_or_none()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already exists")

    getRole = await get_role_by_id(db, body.role_id)
    if getRole is None:
        raise HTTPException(status_code=400, detail="Role not found")

    try:
        hashed_password = hash_password(body.password)
        # Create new user
        user = Users(
            id=str(uuid4()),
            guid=str(uuid4()),
            username=body.username,
            email=body.email,
            password=hashed_password,
            name=body.name,
            profile_pic=body.profile_pic,
            city=body.city,
        )
        # Add new user
        db.add(user)

        # Assign role to user
        await create_user_role(
            db,
            UserRoleCreateBody(user_id=user.id, role_id=body.role_id),
        )

        await db.commit()
        await db.refresh(user)
        return user
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# Register new user
async def register_user(db: AsyncSession, body: UserRegisterBody) -> Users:
    email_result = await db.execute(
        select(Users).where(and_(Users.email == body.email, Users.deleted == False))
    )
    existing_email = email_result.scalar_one_or_none()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    username_result = await db.execute(
        select(Users).where(
            and_(Users.username == body.username, Users.deleted == False)
        )
    )
    existing_username = username_result.scalar_one_or_none()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already exists")

    getRoleName = await get_role_by_name(db, "CUSTOMER")
    if getRoleName is None:
        raise HTTPException(status_code=400, detail="Role not found")

    try:
        hashed_password = hash_password(body.password)
        # Create new user
        user = Users(
            id=str(uuid4()),
            guid=str(uuid4()),
            username=body.username,
            email=body.email,
            password=hashed_password,
            name=body.name,
            profile_pic=body.profile_pic,
            city=body.city,
        )
        # Add new user
        db.add(user)

        # Assign role to user
        await create_user_role(
            db,
            UserRoleCreateBody(user_id=user.id, role_id=getRoleName.id),
        )

        await db.commit()
        await db.refresh(user)
        return user
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


async def get_user(
    db: AsyncSession, pagination: BaseQueryPaginationRequest
) -> UserPagination:
    return await user_service.get_all(db=db, pagination=pagination)


async def get_user_by_id(db: AsyncSession, id: str) -> Users:
    return await user_service.get_by_id(db=db, id=id)


async def get_user_by_email(db: AsyncSession, email: str) -> Users:
    """
    Get user by email
    """
    result = await db.execute(select(Users).where(Users.email == email))
    return result.scalar_one_or_none()


async def update_user(
    db: AsyncSession, id: str, body: UserUpdateBody, current_user: str | None = None
) -> Users:
    return await user_service.update(db=db, id=id, body=body, current_user=current_user)


async def delete_user(db: AsyncSession, id: str) -> Users:
    result = await db.execute(select(Users).where(Users.id == id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()
    return user


async def uploadImage(db: AsyncSession, id: str, file: UploadFile = File(...)):
    user = await get_user_by_id(db, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type")

    ext = os.path.splitext(file.filename)[1]
    if ext not in ALLOWED_EXTS:
        raise HTTPException(status_code=400, detail="Invalid file extension")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds the limit")

    unique_name = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(UPLOAD_DIR, unique_name)

    # Save file
    with open(save_path, "wb") as f:
        f.write(contents)

    user.profile_pic = unique_name
    await db.commit()
    await db.refresh(user)

    return user


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


async def get_user_detail(db: AsyncSession, user_id: str):
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

    return user


# Get permissions and roles for user
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


async def get_role_permission(db: AsyncSession, user_id: str):
    result = await db.execute(text(QUERY_ROLES_PERMISSIONS), {"user_id": user_id})
    row = result.mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    # Key - value
    user = dict(row)

    if isinstance(user["roles"], str):
        user["roles"] = json.loads(user["roles"])
    if isinstance(user["permissions"], str):
        user["permissions"] = json.loads(user["permissions"])

    user["roles"] = user.get("roles") or []
    user["permissions"] = user.get("permissions") or []

    return user
