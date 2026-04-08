from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import and_, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import RolePermissions
from app.schemas.base_schema import BaseQueryPaginationRequest
from app.schemas.rolepermission import (
    RolePermissionCreateBody,
    RolePermissionPagination,
    RolePermissionResponse,
    RolePermissionUpdateBody,
)


class RolePermissionRepository:
    not_found_message = "Role permission not found"
    already_exists_message = "Role permission already exists"

    def base_filters(self) -> list:
        return [RolePermissions.deleted.is_(False)]

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

    async def create_relation(
        self,
        db: AsyncSession,
        body: RolePermissionCreateBody,
        current_user: str | None = None,
    ) -> RolePermissions:
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

    async def get_all(
        self,
        db: AsyncSession,
        pagination: BaseQueryPaginationRequest,
    ) -> RolePermissionPagination:
        filters = self.base_filters()
        if pagination.search:
            filters.extend(self.build_search_filters(pagination.search))
        if pagination.active is not None:
            filters.append(RolePermissions.active == pagination.active)

        total_result = await db.execute(
            select(func.count()).select_from(RolePermissions).where(*filters)
        )
        total = total_result.scalar_one()
        total_pages = (
            (total + pagination.page_size - 1) // pagination.page_size if total else 0
        )

        result = await db.execute(
            select(RolePermissions)
            .where(*filters)
            .order_by(RolePermissions.created.desc())
            .offset((pagination.page - 1) * pagination.page_size)
            .limit(pagination.page_size)
        )
        items = result.scalars().all()

        return RolePermissionPagination(
            items=[RolePermissionResponse.model_validate(item) for item in items],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages,
        )

    async def update_by_keys(
        self,
        db: AsyncSession,
        db_obj: RolePermissions,
        body: RolePermissionUpdateBody,
        current_user: str | None = None,
    ) -> RolePermissions:
        next_role_id = body.role_id if body.role_id is not None else db_obj.role_id
        next_permission_id = (
            body.permission_id
            if body.permission_id is not None
            else db_obj.permission_id
        )

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

    async def soft_delete(
        self, db: AsyncSession, db_obj: RolePermissions
    ) -> RolePermissions:
        if hasattr(db_obj, "active"):
            db_obj.active = False
        if hasattr(db_obj, "deleted"):
            db_obj.deleted = True
        if hasattr(db_obj, "updated"):
            db_obj.updated = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(db_obj)
        return db_obj


role_permission_repository = RolePermissionRepository()
