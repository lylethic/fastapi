from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Permissions
from app.repositories.base_repository import BaseRepository
from app.schemas.permission import (
    PermissionCreateBody,
    PermissionPagination,
    PermissionResponse,
    PermissionUpdateBody,
)


class PermissionRepository(
    BaseRepository[
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

    def build_search_filters(self, search: str) -> list:
        if not search:
            return []
        return [
            or_(
                Permissions.id == search,
                Permissions.name.ilike(f"%{search}%"),
            )
        ]

    async def get_by_name(self, db: AsyncSession, name: str) -> Permissions | None:
        result = await db.execute(
            select(Permissions).where(
                and_(
                    Permissions.name == name,
                    Permissions.deleted.is_(False),
                )
            )
        )
        return result.scalar_one_or_none()


permission_repository = PermissionRepository()
