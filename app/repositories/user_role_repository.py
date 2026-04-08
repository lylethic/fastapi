from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import UserRoles
from app.schemas.base_schema import BaseQueryPaginationRequest
from app.schemas.user_role import (
    UserRoleCreateBody,
    UserRolePagination,
    UserRoleResponse,
    UserRoleUpdateBody,
)


class UserRoleRepository:
    not_found_message = "User role not found"
    already_exists_message = "User already has this role"

    def base_filters(self) -> list:
        return [UserRoles.deleted.is_(False)]

    def build_search_filters(self, search: str) -> list:
        if not search:
            return []
        return [
            or_(
                UserRoles.user_id == search,
                UserRoles.role_id == search,
            )
        ]

    async def get_by_keys(
        self, db: AsyncSession, user_id: str, role_id: str
    ) -> UserRoles | None:
        result = await db.execute(
            select(UserRoles).where(
                and_(
                    UserRoles.user_id == user_id,
                    UserRoles.role_id == role_id,
                    *self.base_filters(),
                )
            )
        )
        return result.scalar_one_or_none()

    async def create_relation(
        self, db: AsyncSession, body: UserRoleCreateBody
    ) -> UserRoles:
        db_obj = UserRoles(
            user_id=body.user_id,
            role_id=body.role_id,
            active=True,
            deleted=False,
        )
        if hasattr(db_obj, "created"):
            db_obj.created = datetime.now(timezone.utc)

        try:
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except Exception as exc:
            await db.rollback()
            raise HTTPException(status_code=400, detail=str(exc))

    async def get_filtered(
        self,
        db: AsyncSession,
        pagination: BaseQueryPaginationRequest,
        user_id: str | None = None,
        role_id: str | None = None,
    ) -> UserRolePagination:
        filters = self.base_filters()
        if pagination.search:
            filters.extend(self.build_search_filters(pagination.search))
        if pagination.active is not None:
            filters.append(UserRoles.active == pagination.active)
        if user_id is not None:
            filters.append(UserRoles.user_id == user_id)
        if role_id is not None:
            filters.append(UserRoles.role_id == role_id)

        total_result = await db.execute(
            select(func.count()).select_from(UserRoles).where(*filters)
        )
        total = total_result.scalar_one()
        total_pages = (
            (total + pagination.page_size - 1) // pagination.page_size if total else 0
        )

        result = await db.execute(
            select(UserRoles)
            .where(*filters)
            .order_by(UserRoles.created.desc())
            .offset((pagination.page - 1) * pagination.page_size)
            .limit(pagination.page_size)
        )
        items = result.scalars().all()

        return UserRolePagination(
            items=[UserRoleResponse.model_validate(item) for item in items],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages,
        )

    async def get_roles_by_user_id(
        self, db: AsyncSession, user_id: str, active: bool | None = True
    ) -> list[UserRoleResponse]:
        filters = self.base_filters()
        filters.append(UserRoles.user_id == user_id)
        if active is not None:
            filters.append(UserRoles.active == int(active))

        result = await db.execute(
            select(UserRoles).where(*filters).order_by(UserRoles.created.desc())
        )
        items = result.scalars().all()
        return [UserRoleResponse.model_validate(item) for item in items]

    async def update_by_keys(
        self, db: AsyncSession, db_obj: UserRoles, body: UserRoleUpdateBody
    ) -> UserRoles:
        if body.role_id is not None:
            db_obj.role_id = body.role_id
        if body.active is not None:
            db_obj.active = int(body.active)
        if hasattr(db_obj, "updated"):
            db_obj.updated = datetime.now(timezone.utc)

        try:
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except Exception as exc:
            await db.rollback()
            raise HTTPException(
                status_code=400, detail=f"Update user role failed: {exc}"
            )

    async def soft_delete(self, db: AsyncSession, db_obj: UserRoles) -> UserRoles:
        db_obj.deleted = True
        db_obj.active = False
        if hasattr(db_obj, "updated"):
            db_obj.updated = datetime.now(timezone.utc)

        try:
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except Exception as exc:
            await db.rollback()
            raise HTTPException(
                status_code=400, detail=f"Soft delete user role failed: {exc}"
            )


user_role_repository = UserRoleRepository()
