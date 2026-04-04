from fastapi import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Roles
from app.providers.baseProvider import BaseProvider
from app.schemas.base_schema import BaseQueryPaginationRequest
from app.schemas.role import (
    RoleCreateBody,
    RolePagination,
    RoleResponse,
    RoleUpdateBody,
)


class RoleService(
    BaseProvider[
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

    async def validate_create(self, db: AsyncSession, body: RoleCreateBody) -> None:
        existed = await self.get_by_name(db, body.name)
        if existed:
            raise HTTPException(status_code=400, detail="Role already exists")

    async def validate_update(
        self, db: AsyncSession, db_obj: Roles, body: RoleUpdateBody
    ) -> None:
        if body.name is None:
            return

        result = await db.execute(
            select(Roles).where(
                and_(
                    Roles.name == body.name.upper(),
                    Roles.id != db_obj.id,
                    Roles.deleted.is_(False),
                )
            )
        )
        existed = result.scalar_one_or_none()
        if existed:
            raise HTTPException(status_code=400, detail="Role already exists")

    def map_create_data(self, body: RoleCreateBody) -> dict:
        return {
            "name": body.name.upper(),
            "description": body.description,
        }

    def map_update_data(self, body: RoleUpdateBody) -> dict:
        data = body.model_dump(exclude_unset=True)
        if data.get("name") is not None:
            data["name"] = data["name"].upper()
        return data

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


role_service = RoleService()


async def get_role_by_name(db: AsyncSession, name: str) -> Roles | None:
    return await role_service.get_by_name(db=db, name=name)
