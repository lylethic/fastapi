from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import UserRoles
from app.repositories.user_role_repository import user_role_repository
from app.schemas.base_schema import BaseQueryPaginationRequest
from app.schemas.user_role import (
    UserRoleCreateBody,
    UserRolePagination,
    UserRoleResponse,
    UserRoleUpdateBody,
)


class UserRoleService:
    def __init__(self) -> None:
        self.repository = user_role_repository

    async def get_by_keys(
        self, db: AsyncSession, user_id: str, role_id: str
    ) -> UserRoles | None:
        return await self.repository.get_by_keys(db, user_id, role_id)

    async def create_relation(
        self, db: AsyncSession, body: UserRoleCreateBody
    ) -> UserRoles:
        existing = await self.get_by_keys(db, body.user_id, body.role_id)
        if existing:
            raise HTTPException(
                status_code=400, detail=self.repository.already_exists_message
            )
        return await self.repository.create_relation(db=db, body=body)

    async def get_filtered(
        self,
        db: AsyncSession,
        pagination: BaseQueryPaginationRequest,
        user_id: Optional[str] = None,
        role_id: Optional[str] = None,
    ) -> UserRolePagination:
        return await self.repository.get_filtered(
            db=db,
            pagination=pagination,
            user_id=user_id,
            role_id=role_id,
        )

    async def get_roles_by_user_id(
        self, db: AsyncSession, user_id: str, active: Optional[bool] = True
    ) -> list[UserRoleResponse]:
        return await self.repository.get_roles_by_user_id(
            db=db, user_id=user_id, active=active
        )

    async def update_by_keys(
        self, db: AsyncSession, user_id: str, role_id: str, body: UserRoleUpdateBody
    ) -> UserRoles:
        db_obj = await self.get_by_keys(db, user_id, role_id)
        if not db_obj:
            raise HTTPException(status_code=404, detail=self.repository.not_found_message)

        if body.role_id is not None and body.role_id != role_id:
            duplicate = await self.get_by_keys(db, user_id, body.role_id)
            if duplicate:
                raise HTTPException(
                    status_code=400,
                    detail="User already has this target role",
                )

        return await self.repository.update_by_keys(db=db, db_obj=db_obj, body=body)

    async def soft_delete_by_keys(
        self, db: AsyncSession, user_id: str, role_id: str
    ) -> UserRoles:
        db_obj = await self.get_by_keys(db, user_id, role_id)
        if not db_obj:
            raise HTTPException(status_code=404, detail=self.repository.not_found_message)

        return await self.repository.soft_delete(db=db, db_obj=db_obj)


user_role_service = UserRoleService()


async def create(db: AsyncSession, body: UserRoleCreateBody) -> UserRoles:
    return await user_role_service.create_relation(db=db, body=body)


async def get_all(
    db: AsyncSession,
    pagination: BaseQueryPaginationRequest,
    user_id: Optional[str] = None,
    role_id: Optional[str] = None,
) -> UserRolePagination:
    return await user_role_service.get_filtered(
        db=db,
        pagination=pagination,
        user_id=user_id,
        role_id=role_id,
    )


async def getById(db: AsyncSession, user_id: str, role_id: str) -> UserRoleResponse:
    user_role = await user_role_service.get_by_keys(db, user_id, role_id)
    if not user_role:
        raise HTTPException(status_code=404, detail="User role not found")
    return UserRoleResponse.model_validate(user_role)


async def getRoleByUserId(
    db: AsyncSession, user_id: str, active: Optional[bool] = True
) -> list[UserRoleResponse]:
    return await user_role_service.get_roles_by_user_id(
        db=db, user_id=user_id, active=active
    )


async def update(
    db: AsyncSession, user_id: str, role_id: str, body: UserRoleUpdateBody
) -> UserRoles:
    return await user_role_service.update_by_keys(
        db=db, user_id=user_id, role_id=role_id, body=body
    )


async def delete(db: AsyncSession, user_id: str, role_id: str) -> str:
    await user_role_service.soft_delete_by_keys(
        db=db, user_id=user_id, role_id=role_id
    )
    return "Soft delete success"
