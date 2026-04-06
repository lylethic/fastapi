from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Roles
from app.schemas.role import (
    RoleCreateBody,
    RolePagination,
    RoleResponse,
    RoleUpdateBody,
)
from app.repositories.base_repository import BaseRepository


class RoleRepository(
    BaseRepository[
        Roles,
        RoleCreateBody,
        RoleUpdateBody,
        RoleResponse,
        RolePagination,
    ]
):
    def __init__(self) -> None:
        super().__init__(
            model=Roles,
            response_schema=RoleResponse,
            pagination_schema=RolePagination,
            not_found_message="Role not found",
            already_exists_message="Role already exists",
            search_fields=["name"],
        )

    async def get_by_name(self, db: AsyncSession, name: str) -> Roles | None:
        result = await db.execute(
            select(Roles).where(
                and_(
                    Roles.name == name.upper(),
                    Roles.deleted.is_(False),
                )
            )
        )
        return result.scalar_one_or_none()


role_repository = RoleRepository()
