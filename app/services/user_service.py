import os
import uuid

from fastapi import File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import UPLOAD_DIR
from app.db.models import Users
from app.repositories.role_repository import role_repository
from app.repositories.user_repository import user_repository
from app.schemas.base_schema import BaseQueryPaginationRequest
from app.schemas.user import (
    UserCreateBody,
    UserPagination,
    UserPermissionRoleResponse,
    UserRegisterBody,
    UserUpdateBody,
)
from app.schemas.user_role import UserRoleCreateBody
from app.services.role_service import get_role_by_name
from app.services.user_role_service import create as create_user_role
from app.utils.token_utils import hash_password

os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


class UserService:
    def __init__(self) -> None:
        self.repository = user_repository

    async def validate_create(self, db: AsyncSession, body: UserCreateBody) -> None:
        existing_email = await self.repository.get_by_email(db, body.email)
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")

        existing_username = await self.repository.get_by_username(db, body.username)
        if existing_username:
            raise HTTPException(status_code=400, detail="Username already exists")

        role = await role_repository.get_by_id(db, body.role_id)
        if role is None:
            raise HTTPException(status_code=400, detail="Role not found")

    async def validate_update(
        self, db: AsyncSession, db_obj: Users, body: UserUpdateBody
    ) -> None:
        if body.email is not None:
            existing_email = await self.repository.get_by_email_excluding_id(
                db,
                body.email,
                db_obj.id,
            )
            if existing_email:
                raise HTTPException(status_code=400, detail="Email already exists")

        if body.username is not None:
            existing_username = await self.repository.get_by_username_excluding_id(
                db,
                body.username,
                db_obj.id,
            )
            if existing_username:
                raise HTTPException(status_code=400, detail="Username already exists")

    def map_create_data(self, body: UserCreateBody | UserRegisterBody) -> dict:
        return {
            "username": body.username,
            "email": body.email,
            "password": hash_password(body.password),
            "name": body.name,
            "profile_pic": body.profile_pic,
            "city": body.city,
        }

    def map_update_data(self, body: UserUpdateBody) -> dict:
        data = body.model_dump(exclude_unset=True)
        if data.get("password"):
            data["password"] = hash_password(data["password"])
        return data

    async def create(self, db: AsyncSession, body: UserCreateBody) -> Users:
        await self.validate_create(db, body)

        try:
            user = await self.repository.create_user_record(
                db=db,
                data=self.map_create_data(body),
            )
            await create_user_role(
                db,
                UserRoleCreateBody(user_id=user.id, role_id=body.role_id),
            )
            await db.refresh(user)
            return user
        except HTTPException:
            await db.rollback()
            raise
        except Exception as exc:
            await db.rollback()
            raise HTTPException(status_code=400, detail=str(exc))

    async def register(self, db: AsyncSession, body: UserRegisterBody) -> Users:
        existing_email = await self.repository.get_active_by_email(db, body.email)
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")

        existing_username = await self.repository.get_active_by_username(
            db, body.username
        )
        if existing_username:
            raise HTTPException(status_code=400, detail="Username already exists")

        role = await get_role_by_name(db, "CUSTOMER")
        if role is None:
            raise HTTPException(status_code=400, detail="Role not found")

        try:
            user = await self.repository.create_user_record(
                db=db,
                data=self.map_create_data(body),
            )
            await create_user_role(
                db,
                UserRoleCreateBody(user_id=user.id, role_id=role.id),
            )
            await db.refresh(user)
            return user
        except HTTPException:
            await db.rollback()
            raise
        except Exception as exc:
            await db.rollback()
            raise HTTPException(status_code=400, detail=str(exc))

    async def get_all(
        self, db: AsyncSession, pagination: BaseQueryPaginationRequest
    ) -> UserPagination:
        return await self.repository.get_all(db=db, pagination=pagination)

    async def get_by_id(self, db: AsyncSession, id: str) -> Users | None:
        return await self.repository.get_by_id(db=db, id=id)

    async def get_by_email(self, db: AsyncSession, email: str) -> Users | None:
        return await self.repository.get_by_email(db=db, email=email)

    async def update(
        self,
        db: AsyncSession,
        id: str,
        body: UserUpdateBody,
        current_user: str | None = None,
    ) -> Users:
        db_obj = await self.repository.get_by_id(db=db, id=id)
        if not db_obj:
            raise HTTPException(status_code=404, detail="User not found")

        await self.validate_update(db, db_obj, body)
        return await self.repository.update_from_data(
            db=db,
            db_obj=db_obj,
            update_data=self.map_update_data(body),
            current_user=current_user,
        )

    async def delete(self, db: AsyncSession, id: str) -> Users:
        return await self.repository.hard_delete(db=db, id=id)

    async def get_user_detail(
        self, db: AsyncSession, user_id: str
    ) -> UserPermissionRoleResponse:
        return await self.repository.get_user_detail(db=db, user_id=user_id)

    async def get_role_permission(self, db: AsyncSession, user_id: str) -> dict:
        return await self.repository.get_role_permission(db=db, user_id=user_id)


user_service = UserService()


async def create_user(db: AsyncSession, body: UserCreateBody) -> Users:
    return await user_service.create(db=db, body=body)


async def register_user(db: AsyncSession, body: UserRegisterBody) -> Users:
    return await user_service.register(db=db, body=body)


async def get_user(
    db: AsyncSession, pagination: BaseQueryPaginationRequest
) -> UserPagination:
    return await user_service.get_all(db=db, pagination=pagination)


async def get_user_by_id(db: AsyncSession, id: str) -> Users | None:
    return await user_service.get_by_id(db=db, id=id)


async def get_user_by_email(db: AsyncSession, email: str) -> Users | None:
    return await user_service.get_by_email(db=db, email=email)


async def update_user(
    db: AsyncSession, id: str, body: UserUpdateBody, current_user: str | None = None
) -> Users:
    return await user_service.update(
        db=db, id=id, body=body, current_user=current_user
    )


async def delete_user(db: AsyncSession, id: str) -> Users:
    return await user_service.delete(db=db, id=id)


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

    with open(save_path, "wb") as file_obj:
        file_obj.write(contents)

    user.profile_pic = unique_name
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_detail(db: AsyncSession, user_id: str):
    return await user_service.get_user_detail(db=db, user_id=user_id)


async def get_role_permission(db: AsyncSession, user_id: str):
    return await user_service.get_role_permission(db=db, user_id=user_id)
