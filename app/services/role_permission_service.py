from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import RolePermissions
from app.repositories.role_permission_repository import role_permission_repository
from app.schemas.base_schema import BaseQueryPaginationRequest
from app.schemas.rolepermission import (
    RolePermissionCreateBody,
    RolePermissionPagination,
    RolePermissionUpdateBody,
)


class RolePermissionService:
    def __init__(self) -> None:
        self.repository = role_permission_repository

    async def get_by_keys(
        self, db: AsyncSession, role_id: str, permission_id: str
    ) -> RolePermissions | None:
        return await self.repository.get_by_keys(db, role_id, permission_id)

    async def create(
        self,
        db: AsyncSession,
        body: RolePermissionCreateBody,
        current_user: str | None = None,
    ) -> RolePermissions:
        existing = await self.get_by_keys(db, body.role_id, body.permission_id)
        if existing:
            raise HTTPException(
                status_code=400, detail=self.repository.already_exists_message
            )

        return await self.repository.create_relation(
            db=db,
            body=body,
            current_user=current_user,
        )

    async def get_role_permissions(
        self,
        db: AsyncSession,
        pagination: BaseQueryPaginationRequest,
    ) -> RolePermissionPagination:
        return await self.repository.get_all(db=db, pagination=pagination)

    async def update_by_keys(
        self,
        db: AsyncSession,
        role_id: str,
        permission_id: str,
        body: RolePermissionUpdateBody,
        current_user: str | None = None,
    ) -> RolePermissions:
        db_obj = await self.get_by_keys(db, role_id, permission_id)
        if not db_obj:
            raise HTTPException(status_code=404, detail=self.repository.not_found_message)

        next_role_id = body.role_id if body.role_id is not None else db_obj.role_id
        next_permission_id = (
            body.permission_id
            if body.permission_id is not None
            else db_obj.permission_id
        )
        if (
            next_role_id != db_obj.role_id
            or next_permission_id != db_obj.permission_id
        ):
            duplicate = await self.get_by_keys(db, next_role_id, next_permission_id)
            if duplicate:
                raise HTTPException(
                    status_code=400, detail=self.repository.already_exists_message
                )

        return await self.repository.update_by_keys(
            db=db,
            db_obj=db_obj,
            body=body,
            current_user=current_user,
        )

    async def soft_delete_by_keys(
        self, db: AsyncSession, role_id: str, permission_id: str
    ) -> RolePermissions:
        db_obj = await self.get_by_keys(db, role_id, permission_id)
        if not db_obj:
            raise HTTPException(status_code=404, detail=self.repository.not_found_message)

        return await self.repository.soft_delete(db=db, db_obj=db_obj)


role_permission_service = RolePermissionService()


async def create_role_permission(
    db: AsyncSession, body: RolePermissionCreateBody
) -> RolePermissions:
    return await role_permission_service.create(db=db, body=body)


async def get_role_permissions(
    db: AsyncSession, pagination: BaseQueryPaginationRequest
) -> RolePermissionPagination:
    return await role_permission_service.get_role_permissions(
        db=db, pagination=pagination
    )


async def get_role_permission_by_id(
    db: AsyncSession, role_id: str, permission_id: str
) -> RolePermissions | None:
    return await role_permission_service.get_by_keys(
        db=db, role_id=role_id, permission_id=permission_id
    )


async def update_role_permission(
    db: AsyncSession,
    role_id: str,
    permission_id: str,
    body: RolePermissionUpdateBody,
) -> RolePermissions:
    return await role_permission_service.update_by_keys(
        db=db,
        role_id=role_id,
        permission_id=permission_id,
        body=body,
    )


async def delete_role_permission(
    db: AsyncSession, role_id: str, permission_id: str
) -> RolePermissions:
    return await role_permission_service.soft_delete_by_keys(
        db=db,
        role_id=role_id,
        permission_id=permission_id,
    )
