from fastapi import HTTPException
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Permissions
from app.providers.baseProvider import BaseProvider
from app.schemas.base_schema import BaseQueryPaginationRequest
from app.schemas.permission import (
    PermissionCreateBody,
    PermissionPagination,
    PermissionResponse,
    PermissionUpdateBody,
)


class PermissionService(
    BaseProvider[
        Permissions,
        PermissionCreateBody,
        PermissionUpdateBody,
        PermissionResponse,
        PermissionPagination,
    ]
):
    def __init__(self) -> None:
        super().__init__(
            model=Permissions,
            response_schema=PermissionResponse,
            pagination_schema=PermissionPagination,
            not_found_message="Permission not found",
            already_exists_message="Permission already exists",
            search_fields=["name"],
        )

    async def validate_create(
        self, db: AsyncSession, body: PermissionCreateBody
    ) -> None:
        result = await db.execute(
            select(Permissions).where(
                and_(
                    Permissions.name == body.name,
                    Permissions.deleted.is_(False),
                )
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Permission already exists")

    async def validate_update(
        self, db: AsyncSession, db_obj: Permissions, body: PermissionUpdateBody
    ) -> None:
        if body.name is None:
            return

        result = await db.execute(
            select(Permissions).where(
                and_(
                    Permissions.name == body.name,
                    Permissions.id != db_obj.id,
                    Permissions.deleted.is_(False),
                )
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Permission already exists")

    def build_search_filters(self, search: str) -> list:
        if not search:
            return []
        return [
            or_(
                Permissions.id == search,
                Permissions.name.ilike(f"%{search}%"),
            )
        ]


permission_service = PermissionService()


async def create_permission(
    db: AsyncSession, body: PermissionCreateBody, current_user: str | None = None
) -> Permissions:
    return await permission_service.post(db=db, body=body, current_user=current_user)


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
