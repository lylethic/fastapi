import os
import uuid

from fastapi import File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import UPLOAD_CAMPAIGN_THUMBNAIL, UPLOAD_DIR
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
from app.services.role_service import role_service
from app.services.user_role_service import user_role_service
from app.utils.token_utils import hash_password
from app.utils.upload import upload_one_image

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

    def map_create_model(self, body: UserCreateBody | UserRegisterBody) -> Users:
        return Users(
            username=body.username,
            email=body.email,
            password=hash_password(body.password),
            name=body.name,
            profile_pic=body.profile_pic,
            city=body.city,
        )

    def map_update_model(self, body: UserUpdateBody) -> tuple[Users, set[str]]:
        data = body.model_dump(exclude_unset=True)
        if data.get("password"):
            data["password"] = hash_password(data["password"])

        return Users(**data), set(data.keys())

    async def create(self, db: AsyncSession, body: UserCreateBody) -> Users:
        await self.validate_create(db, body)

        try:
            user = await self.repository.create_user_record(
                db=db,
                user=self.map_create_model(body),
            )
            await user_role_service.create(
                db=db,
                body=UserRoleCreateBody(user_id=user.id, role_id=body.role_id),
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

        role = await role_service.get_by_name(db, "CUSTOMER")
        if role is None:
            raise HTTPException(status_code=400, detail="Role not found")

        try:
            user = await self.repository.create_user_record(
                db=db,
                user=self.map_create_model(body),
            )
            await user_role_service.create(
                db=db,
                body=UserRoleCreateBody(user_id=user.id, role_id=role.id),
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
        user_model, update_fields = self.map_update_model(body)
        return await self.repository.update(
            db=db,
            id=id,
            body=user_model,
            current_user=current_user,
            fields=update_fields,
        )

    async def delete(self, db: AsyncSession, id: str) -> Users:
        return await self.repository.hard_delete(db=db, id=id)

    async def get_user_detail(
        self, db: AsyncSession, user_id: str
    ) -> UserPermissionRoleResponse:
        return await self.repository.get_user_detail(db=db, user_id=user_id)

    async def get_role_permission(self, db: AsyncSession, user_id: str) -> dict:
        return await self.repository.get_role_permission(db=db, user_id=user_id)

    async def uploadImage(
        self, db: AsyncSession, id: str, file: UploadFile = File(...)
    ):
        user = await self.repository.get_by_id(db, id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        uploaded = await upload_one_image(
            file=file, folder_name=UPLOAD_CAMPAIGN_THUMBNAIL
        )
        user.profile_pic = uploaded["relative_path"]
        await db.commit()
        await db.refresh(user)
        return user


user_service = UserService()
