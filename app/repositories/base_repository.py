from __future__ import annotations

import uuid

from datetime import datetime, timezone

from typing import Any, Generic, List, Optional, TypeVar

from fastapi import HTTPException

from pydantic import BaseModel

from sqlalchemy import func, or_, select

from sqlalchemy.exc import IntegrityError

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import DeclarativeMeta


from app.schemas.base_schema import BaseQueryPaginationRequest

ModelType = TypeVar("ModelType")

CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)

UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

ResponseSchemaType = TypeVar("ResponseSchemaType", bound=BaseModel)

PaginationSchemaType = TypeVar("PaginationSchemaType", bound=BaseModel)


class BaseRepository(
    Generic[
        ModelType,
        CreateSchemaType,
        UpdateSchemaType,
        ResponseSchemaType,
        PaginationSchemaType,
    ]
):
    """Base repository for CRUD operations."""

    def __init__(
        self,
        model: DeclarativeMeta,
        response_schema: type[ResponseSchemaType],
        pagination_schema: type[PaginationSchemaType],
        *,
        not_found_message: str = "Item not found",
        already_exists_message: str = "Item already exists",
        search_fields: list[str] | None = None,
        default_order_field: str = "created",
    ) -> None:
        self.model = model
        self.response_schema = response_schema
        self.pagination_schema = pagination_schema
        self.not_found_message = not_found_message
        self.already_exists_message = already_exists_message
        self.search_fields = search_fields or []
        self.default_order_field = default_order_field

    # =========================
    # Hooks for child class override
    # =========================
    async def validate_create(self, db: AsyncSession, body: CreateSchemaType) -> None:
        return None

    async def validate_update(
        self, db: AsyncSession, db_obj: ModelType, body: UpdateSchemaType
    ) -> None:
        return None

    def map_create_data(self, body: CreateSchemaType) -> dict[str, Any]:
        return body.model_dump(exclude_unset=True)

    def map_update_data(self, body: UpdateSchemaType) -> dict[str, Any]:
        return body.model_dump(exclude_unset=True)

    def base_filters(self) -> list[Any]:
        filters: list[Any] = []
        if hasattr(self.model, "deleted"):
            filters.append(self.model.deleted.is_(False))
        return filters

    def build_search_filters(self, search: str) -> list[Any]:
        if not search or not self.search_fields:
            return []

        conditions = []
        for field_name in self.search_fields:
            field = getattr(self.model, field_name, None)
            if field is not None:
                conditions.append(field.ilike(f"%{search}%"))

        if not conditions:
            return []

        return [or_(*conditions)]

    def get_order_field(self):
        return getattr(self.model, self.default_order_field, None)

    async def get_by_id(self, db: AsyncSession, id: str) -> Optional[ModelType]:
        """Get one by id"""
        stmt = select(self.model).where(
            self.model.id == id,
            *self.base_filters(),
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get(self, db: AsyncSession, id: str) -> Optional[ModelType]:
        """Get one"""
        return await self.get_by_id(db, id)

    async def get_all(
        self,
        db: AsyncSession,
        pagination: BaseQueryPaginationRequest,
    ) -> PaginationSchemaType:
        """Get multi item with filters"""
        filters = self.base_filters()

        if pagination.search:
            filters.extend(self.build_search_filters(pagination.search))

        if pagination.active is not None and hasattr(self.model, "active"):
            filters.append(self.model.active == pagination.active)

        count_stmt = select(func.count()).select_from(self.model)

        if filters:
            count_stmt = count_stmt.where(*filters)

        total_result = await db.execute(count_stmt)
        total = total_result.scalar_one()

        total_pages = (
            (total + pagination.page_size - 1) // pagination.page_size if total else 0
        )

        stmt = select(self.model)

        if filters:
            stmt = stmt.where(*filters)

        order_field = self.get_order_field()

        if order_field is not None:
            stmt = stmt.order_by(order_field.desc())

        stmt = stmt.offset((pagination.page - 1) * pagination.page_size).limit(
            pagination.page_size
        )

        result = await db.execute(stmt)
        items = result.scalars().all()

        return self.pagination_schema(
            items=[self.response_schema.model_validate(item) for item in items],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages,
        )

    async def post(
        self,
        db: AsyncSession,
        body: CreateSchemaType,
        current_user: str | None = None,
    ) -> ModelType:
        """Create new item"""
        await self.validate_create(db, body)

        data = self.map_create_data(body)
        return await self.create_from_data(
            db=db,
            data=data,
            current_user=current_user,
        )

    async def create_from_data(
        self,
        db: AsyncSession,
        data: dict[str, Any],
        current_user: str | None = None,
    ) -> ModelType:
        """Create new item from prepared data"""

        db_obj = self.model(
            id=str(uuid.uuid7()),
            **data,
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
            raise HTTPException(
                status_code=400,
                detail=self.already_exists_message,
            )

    async def update(
        self,
        db: AsyncSession,
        id: str,
        body: UpdateSchemaType,
        current_user: str | None = None,
    ) -> ModelType:
        """Update item"""
        db_obj = await self.get_by_id(db, id)

        if not db_obj:
            raise HTTPException(status_code=404, detail=self.not_found_message)

        await self.validate_update(db, db_obj, body)

        update_data = self.map_update_data(body)
        return await self.update_from_data(
            db=db,
            db_obj=db_obj,
            update_data=update_data,
            current_user=current_user,
        )

    async def update_from_data(
        self,
        db: AsyncSession,
        db_obj: ModelType,
        update_data: dict[str, Any],
        current_user: str | None = None,
    ) -> ModelType:
        """Update existing item from prepared data"""

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        now = datetime.now(timezone.utc)

        if hasattr(db_obj, "updated"):
            db_obj.updated = now

        if current_user is not None and hasattr(db_obj, "updated_by"):
            db_obj.updated_by = current_user

        try:

            await db.commit()
            await db.refresh(db_obj)

            return db_obj

        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=400,
                detail=self.already_exists_message,
            )

    async def delete(self, db: AsyncSession, id: str) -> bool:
        """Delete item"""
        db_obj = await self.get(db, id)

        if db_obj is None:
            return False

        if hasattr(db_obj, "active"):
            db_obj.active = False

        if hasattr(db_obj, "deleted"):
            db_obj.deleted = True

        if hasattr(db_obj, "updated"):
            db_obj.updated = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(db_obj)

        return True

    async def soft_delete(self, db: AsyncSession, id: str) -> ModelType:
        """Soft delete one item and return updated object"""
        db_obj = await self.get_by_id(db, id)

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

    async def delete_multi(seft, db: AsyncSession, ids: List[str]) -> int:
        """Soft delete multiple items.
        Returns:
            int: Number of items soft deleted
        """

        if not ids:
            return 0

        result = await db.execute(select(seft.model).where(seft.model.id.in_(ids)))

        db_objs = result.scalars().all()

        if not db_objs:
            return 0

        now = datetime.now(timezone.utc)

        for item in db_objs:
            if hasattr(item, "active"):
                item.active = False

            if hasattr(item, "deleted"):
                item.deleted = True

            if hasattr(item, "updated"):
                item.updated = now

        await db.commit()
        for item in db_objs:
            await db.refresh(item)
        return len(db_objs)
