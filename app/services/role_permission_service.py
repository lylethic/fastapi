from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import and_, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import RolePermissions
from app.providers.baseProvider import BaseProvider
from app.schemas.base_schema import BaseQueryPaginationRequest
from app.schemas.rolepermission import (
    RolePermissionCreateBody,
    RolePermissionPagination,
    RolePermissionResponse,
    RolePermissionUpdateBody,
)


class RolePermissionService(
    BaseProvider[
        RolePermissions,
        RolePermissionCreateBody,
        RolePermissionUpdateBody,
        RolePermissionResponse,
        RolePermissionPagination,
    ]
):
    def __init__(self) -> None:
        super().__init__(
            model=RolePermissions,
            response_schema=RolePermissionResponse,
            pagination_schema=RolePermissionPagination,
            not_found_message="Role permission not found",
            already_exists_message="Role permission already exists",
        )

    def build_search_filters(self, search: str) -> list:
        if not search:
            return []
        return [
            or_(
                RolePermissions.role_id == search,
                RolePermissions.permission_id == search,
            )
        ]

    async def get_by_keys(
        self, db: AsyncSession, role_id: str, permission_id: str
    ) -> RolePermissions | None:
        result = await db.execute(
            select(RolePermissions).where(
                and_(
                    RolePermissions.role_id == role_id,
                    RolePermissions.permission_id == permission_id,
                    *self.base_filters(),
                )
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        db: AsyncSession,
        body: RolePermissionCreateBody,
        current_user: str | None = None,
    ) -> RolePermissions:
        existing = await self.get_by_keys(db, body.role_id, body.permission_id)
        if existing:
            raise HTTPException(status_code=400, detail=self.already_exists_message)

        db_obj = RolePermissions(
            role_id=body.role_id,
            permission_id=body.permission_id,
        )

        now = datetime.now(timezone.utc)
        if hasattr(db_obj, "created"):
            db_obj.created = now
        if current_user is not None and hasattr(db_obj, "created_by"):
            db_obj.created_by = current_user

        db.add(db_obj)
        try:
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=400, detail=self.already_exists_message)

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
            raise HTTPException(status_code=404, detail=self.not_found_message)

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
                raise HTTPException(status_code=400, detail=self.already_exists_message)

        db_obj.role_id = next_role_id
        db_obj.permission_id = next_permission_id
        if body.active is not None:
            db_obj.active = body.active
        if hasattr(db_obj, "updated"):
            db_obj.updated = datetime.now(timezone.utc)
        if current_user is not None and hasattr(db_obj, "updated_by"):
            db_obj.updated_by = current_user

        try:
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=400, detail=self.already_exists_message)

    async def soft_delete_by_keys(
        self, db: AsyncSession, role_id: str, permission_id: str
    ) -> RolePermissions:
        db_obj = await self.get_by_keys(db, role_id, permission_id)
        if not db_obj:
            raise HTTPException(status_code=404, detail=self.not_found_message)

        if hasattr(db_obj, "active"):
            db_obj.active = False
        if hasattr(db_obj, "deleted"):
            db_obj.deleted = True
        if hasattr(db_obj, "updated"):
            db_obj.updated = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(db_obj)
        return db_obj


role_permission_service = RolePermissionService()


async def create_role_permission(
    db: AsyncSession, body: RolePermissionCreateBody
) -> RolePermissions:
    return await role_permission_service.create(db=db, body=body)


async def get_role_permissions(
    db: AsyncSession, pagination: BaseQueryPaginationRequest
) -> RolePermissionPagination:
    return await role_permission_service.get_all(db=db, pagination=pagination)


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
