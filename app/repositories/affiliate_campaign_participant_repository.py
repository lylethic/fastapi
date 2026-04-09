from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AffiliateCampaignParticipants
from app.schemas.affiliate_campaigns import (
    AffiliateCampaignParticipantCreateBody,
    AffiliateCampaignParticipantPagination,
    AffiliateCampaignParticipantQueryRequest,
    AffiliateCampaignParticipantResponse,
    AffiliateCampaignParticipantUpdateBody,
)


class AffiliateCampaignParticipantRepository:
    def __init__(self) -> None:
        self.model = AffiliateCampaignParticipants
        self.response_schema = AffiliateCampaignParticipantResponse
        self.pagination_schema = AffiliateCampaignParticipantPagination
        self.not_found_message = "Campaign participant not found"
        self.already_exists_message = "Campaign participant already exists"

    def base_filters(self) -> list[Any]:
        return [self.model.deleted.is_(False)]

    def build_search_filters(self, search: str) -> list[Any]:
        if not search:
            return []
        return [or_(self.model.note.ilike(f"%{search}%"))]

    async def get_by_ids(
        self,
        db: AsyncSession,
        campaign_id: str,
        affiliate_id: str,
    ) -> AffiliateCampaignParticipants | None:
        stmt = select(self.model).where(
            self.model.campaign_id == campaign_id,
            self.model.affiliate_id == affiliate_id,
            *self.base_filters(),
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        db: AsyncSession,
        campaign_id: str,
        pagination: AffiliateCampaignParticipantQueryRequest,
    ) -> AffiliateCampaignParticipantPagination:
        filters = self.base_filters()
        filters.append(self.model.campaign_id == campaign_id)

        if pagination.search:
            filters.extend(self.build_search_filters(pagination.search))

        if pagination.active is not None and hasattr(self.model, "active"):
            filters.append(self.model.active == pagination.active)

        if pagination.affiliate_id:
            filters.append(self.model.affiliate_id == pagination.affiliate_id)

        if pagination.status is not None:
            filters.append(self.model.status == pagination.status)

        count_stmt = select(func.count()).select_from(self.model).where(*filters)
        total_result = await db.execute(count_stmt)
        total = total_result.scalar_one()
        total_pages = (
            (total + pagination.page_size - 1) // pagination.page_size if total else 0
        )

        stmt = (
            select(self.model)
            .where(*filters)
            .order_by(self.model.joined_at.desc())
            .offset((pagination.page - 1) * pagination.page_size)
            .limit(pagination.page_size)
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

    async def create_from_data(
        self,
        db: AsyncSession,
        data: dict[str, Any],
        current_user: str | None = None,
    ) -> AffiliateCampaignParticipants:
        db_obj = self.model(**data)

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

    async def update_from_data(
        self,
        db: AsyncSession,
        db_obj: AffiliateCampaignParticipants,
        update_data: dict[str, Any],
        current_user: str | None = None,
    ) -> AffiliateCampaignParticipants:
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
            raise HTTPException(status_code=400, detail=self.already_exists_message)

    async def soft_delete(
        self,
        db: AsyncSession,
        campaign_id: str,
        affiliate_id: str,
        current_user: str | None = None,
    ) -> AffiliateCampaignParticipants:
        db_obj = await self.get_by_ids(
            db=db,
            campaign_id=campaign_id,
            affiliate_id=affiliate_id,
        )
        if not db_obj:
            raise HTTPException(status_code=404, detail=self.not_found_message)

        if hasattr(db_obj, "active"):
            db_obj.active = False
        if hasattr(db_obj, "deleted"):
            db_obj.deleted = True
        if hasattr(db_obj, "updated"):
            db_obj.updated = datetime.now(timezone.utc)
        if current_user is not None and hasattr(db_obj, "updated_by"):
            db_obj.updated_by = current_user

        await db.commit()
        await db.refresh(db_obj)
        return db_obj


affiliate_campaign_participant_repository = AffiliateCampaignParticipantRepository()
