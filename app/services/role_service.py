from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Roles
from app.repositories.role_repository import role_repository
from app.schemas.base_schema import BaseQueryPaginationRequest
from app.schemas.role import (
    RoleCreateBody,
    RolePagination,
    RoleUpdateBody,
)


class RoleService:
    def __init__(self) -> None:
        self.repository = role_repository

    async def validate_create(self, db: AsyncSession, body: RoleCreateBody) -> None:
        existed = await self.repository.get_by_name(db, body.name)
        if existed:
            raise HTTPException(status_code=400, detail="Role already exists")

    async def validate_update(
        self, db: AsyncSession, db_obj: Roles, body: RoleUpdateBody
    ) -> None:
        if body.name is None:
            return

        existed = await self.repository.get_by_name(db, body.name)
        if existed and existed.id != db_obj.id:
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

    async def create(
        self,
        db: AsyncSession,
        body: RoleCreateBody,
        current_user: str | None = None,
    ) -> Roles:
        await self.validate_create(db, body)
        return await self.repository.create_from_data(
            db=db,
            data=self.map_create_data(body),
            current_user=current_user,
        )

    async def get_all(
        self, db: AsyncSession, pagination: BaseQueryPaginationRequest
    ) -> RolePagination:
        return await self.repository.get_all(db=db, pagination=pagination)

    async def get_by_id(self, db: AsyncSession, id: str) -> Roles | None:
        return await self.repository.get_by_id(db=db, id=id)

    async def update(
        self,
        db: AsyncSession,
        id: str,
        body: RoleUpdateBody,
        current_user: str | None = None,
    ) -> Roles:
        db_obj = await self.repository.get_by_id(db=db, id=id)
        if not db_obj:
            raise HTTPException(status_code=404, detail="Role not found")

        await self.validate_update(db, db_obj, body)
        return await self.repository.update_from_data(
            db=db,
            db_obj=db_obj,
            update_data=self.map_update_data(body),
            current_user=current_user,
        )

    async def soft_delete(self, db: AsyncSession, id: str) -> Roles:
        return await self.repository.soft_delete(db=db, id=id)

    async def get_by_name(self, db: AsyncSession, name: str) -> Roles | None:
        return await self.repository.get_by_name(db=db, name=name)


role_service = RoleService()
