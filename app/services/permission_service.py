from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Permissions
from app.repositories.permission_repository import permission_repository
from app.schemas.base_schema import BaseQueryPaginationRequest
from app.schemas.permission import (
    PermissionCreateBody,
    PermissionPagination,
    PermissionUpdateBody,
)


class PermissionService:
    def __init__(self) -> None:
        self.repository = permission_repository

    async def validate_create(
        self, db: AsyncSession, body: PermissionCreateBody
    ) -> None:
        existed = await self.repository.get_by_name(db, body.name)
        if existed:
            raise HTTPException(status_code=400, detail="Permission already exists")

    async def validate_update(
        self, db: AsyncSession, db_obj: Permissions, body: PermissionUpdateBody
    ) -> None:
        if body.name is None:
            return

        existed = await self.repository.get_by_name(db, body.name)
        if existed and existed.id != db_obj.id:
            raise HTTPException(status_code=400, detail="Permission already exists")

    async def create(
        self,
        db: AsyncSession,
        body: PermissionCreateBody,
        current_user: str | None = None,
    ) -> Permissions:
        await self.validate_create(db, body)
        return await self.repository.create_from_data(
            db=db,
            data=body.model_dump(exclude_unset=True),
            current_user=current_user,
        )

    async def get_all(
        self, db: AsyncSession, pagination: BaseQueryPaginationRequest
    ) -> PermissionPagination:
        return await self.repository.get_all(db=db, pagination=pagination)

    async def get_by_id(self, db: AsyncSession, id: str) -> Permissions | None:
        return await self.repository.get_by_id(db=db, id=id)

    async def update(
        self,
        db: AsyncSession,
        id: str,
        body: PermissionUpdateBody,
        current_user: str | None = None,
    ) -> Permissions:
        db_obj = await self.repository.get_by_id(db=db, id=id)
        if not db_obj:
            raise HTTPException(status_code=404, detail="Permission not found")

        await self.validate_update(db, db_obj, body)
        return await self.repository.update_from_data(
            db=db,
            db_obj=db_obj,
            update_data=body.model_dump(exclude_unset=True),
            current_user=current_user,
        )

    async def soft_delete(self, db: AsyncSession, id: str) -> Permissions:
        return await self.repository.soft_delete(db=db, id=id)


permission_service = PermissionService()


async def create_permission(
    db: AsyncSession, body: PermissionCreateBody, current_user: str | None = None
) -> Permissions:
    return await permission_service.create(db=db, body=body, current_user=current_user)


async def get_permission(
    db: AsyncSession, pagination: BaseQueryPaginationRequest
) -> PermissionPagination:
    return await permission_service.get_all(db=db, pagination=pagination)


async def get_permission_by_id(db: AsyncSession, id: str) -> Permissions | None:
    return await permission_service.get_by_id(db=db, id=id)


async def update_permission(
    db: AsyncSession,
    id: str,
    body: PermissionUpdateBody,
    current_user: str | None = None,
) -> Permissions:
    return await permission_service.update(
        db=db, id=id, body=body, current_user=current_user
    )


async def delete_permission(db: AsyncSession, id: str) -> Permissions:
    return await permission_service.soft_delete(db=db, id=id)
