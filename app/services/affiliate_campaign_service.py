from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AffiliateCampaignParticipants, AffiliateCampaignsStatus
from app.repositories.affiliate_campaign_participant_repository import (
    affiliate_campaign_participant_repository,
)
from app.repositories.affiliate_campaign_repository import affiliate_campaign_repository
from app.schemas.affiliate_campaigns import (
    AffiliateCampaignCreateBody,
    AffiliateCampaignPagination,
    AffiliateCampaignParticipantCreateBody,
    AffiliateCampaignParticipantPagination,
    AffiliateCampaignParticipantQueryRequest,
    AffiliateCampaignParticipantUpdateBody,
    AffiliateCampaignQueryRequest,
    AffiliateCampaignUpdateBody,
)
from app.services.affiliate_profile_service import affiliate_profile_service
from app.services.merchant_profile_service import merchant_profile_service


class AffiliateCampaignService:
    def __init__(self) -> None:
        self.repository = affiliate_campaign_repository

    async def validate_merchant(self, db: AsyncSession, merchant_id: str) -> None:
        merchant = await merchant_profile_service.get_by_id(db=db, id=merchant_id)
        if merchant is None:
            raise HTTPException(status_code=400, detail="Merchant profile not found")

    def validate_date_range(
        self,
        start_date: datetime | None,
        end_date: datetime | None,
    ) -> None:
        if start_date and end_date and start_date > end_date:
            raise HTTPException(
                status_code=400,
                detail="Start date must be less than or equal to end date",
            )

    def normalize_campaign_data(self, data: dict) -> dict:
        string_fields = [
            "name",
            "description",
            "landing_page_url",
            "thumbnail_url",
            "terms_conditions",
        ]

        for field in string_fields:
            value = data.get(field)
            if isinstance(value, str):
                value = value.strip()
                data[field] = value or None

        name = data.get("name")
        if name is None:
            return data

        if not isinstance(name, str) or not name:
            raise HTTPException(status_code=400, detail="Campaign name is required")

        return data

    async def post(
        self,
        db: AsyncSession,
        body: AffiliateCampaignCreateBody,
        current_user: str | None = None,
    ):
        await self.validate_merchant(db=db, merchant_id=body.merchant_id)
        self.validate_date_range(body.start_date, body.end_date)
        data = self.normalize_campaign_data(body.model_dump(exclude_unset=True))
        return await self.repository.create_from_data(
            db=db,
            data=data,
            current_user=current_user,
        )

    async def get_all(
        self,
        db: AsyncSession,
        pagination: AffiliateCampaignQueryRequest,
    ) -> AffiliateCampaignPagination:
        return await self.repository.get_all(db=db, pagination=pagination)

    async def get_by_id(self, db: AsyncSession, id: str):
        campaign = await self.repository.get_by_id(db=db, id=id)
        if campaign is None:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return campaign

    async def update(
        self,
        db: AsyncSession,
        id: str,
        body: AffiliateCampaignUpdateBody,
        current_user: str | None = None,
    ):
        db_obj = await self.repository.get_by_id(db=db, id=id)
        if db_obj is None:
            raise HTTPException(status_code=404, detail="Campaign not found")

        update_data = body.model_dump(exclude_unset=True)
        merchant_id = update_data.get("merchant_id")
        if merchant_id:
            await self.validate_merchant(db=db, merchant_id=merchant_id)

        self.validate_date_range(
            update_data.get("start_date", db_obj.start_date),
            update_data.get("end_date", db_obj.end_date),
        )
        update_data = self.normalize_campaign_data(update_data)

        return await self.repository.update_from_data(
            db=db,
            db_obj=db_obj,
            update_data=update_data,
            current_user=current_user,
        )

    async def delete(self, db: AsyncSession, id: str):
        return await self.repository.soft_delete(db=db, id=id)


class AffiliateCampaignParticipantService:
    def __init__(self) -> None:
        self.repository = affiliate_campaign_participant_repository
        self.campaign_repository = affiliate_campaign_repository

    async def validate_campaign_and_affiliate(
        self,
        db: AsyncSession,
        campaign_id: str,
        affiliate_id: str,
    ):
        campaign = await self.campaign_repository.get_by_id(db=db, id=campaign_id)
        if campaign is None:
            raise HTTPException(status_code=400, detail="Campaign not found")

        affiliate = await affiliate_profile_service.get_by_id(db=db, id=affiliate_id)
        if affiliate is None:
            raise HTTPException(status_code=400, detail="Affiliate profile not found")

        return campaign

    def normalize_participant_data(self, data: dict) -> dict:
        note = data.get("note")
        if isinstance(note, str):
            note = note.strip()
            data["note"] = note or None

        status = data.get("status")
        if status is not None:
            data["approved_at"] = (
                datetime.now(timezone.utc)
                if status == "approved"
                else None
            )

        return data

    async def get_all(
        self,
        db: AsyncSession,
        campaign_id: str,
        pagination: AffiliateCampaignParticipantQueryRequest,
    ) -> AffiliateCampaignParticipantPagination:
        await self.get_by_campaign_id(db=db, campaign_id=campaign_id)
        return await self.repository.get_all(
            db=db,
            campaign_id=campaign_id,
            pagination=pagination,
        )

    async def get_by_campaign_id(self, db: AsyncSession, campaign_id: str):
        campaign = await self.campaign_repository.get_by_id(db=db, id=campaign_id)
        if campaign is None:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return campaign

    async def get_by_ids(
        self,
        db: AsyncSession,
        campaign_id: str,
        affiliate_id: str,
    ) -> AffiliateCampaignParticipants:
        participant = await self.repository.get_by_ids(
            db=db,
            campaign_id=campaign_id,
            affiliate_id=affiliate_id,
        )
        if participant is None:
            raise HTTPException(status_code=404, detail="Campaign participant not found")
        return participant

    async def post(
        self,
        db: AsyncSession,
        campaign_id: str,
        body: AffiliateCampaignParticipantCreateBody,
        current_user: str | None = None,
    ) -> AffiliateCampaignParticipants:
        campaign = await self.validate_campaign_and_affiliate(
            db=db,
            campaign_id=campaign_id,
            affiliate_id=body.affiliate_id,
        )

        if campaign.status == AffiliateCampaignsStatus.CLOSED:
            raise HTTPException(status_code=400, detail="Campaign is closed")

        data = body.model_dump(exclude_unset=True)
        data["campaign_id"] = campaign_id
        data = self.normalize_participant_data(data)
        return await self.repository.create_from_data(
            db=db,
            data=data,
            current_user=current_user,
        )

    async def update(
        self,
        db: AsyncSession,
        campaign_id: str,
        affiliate_id: str,
        body: AffiliateCampaignParticipantUpdateBody,
        current_user: str | None = None,
    ) -> AffiliateCampaignParticipants:
        db_obj = await self.get_by_ids(
            db=db,
            campaign_id=campaign_id,
            affiliate_id=affiliate_id,
        )

        update_data = self.normalize_participant_data(
            body.model_dump(exclude_unset=True)
        )
        return await self.repository.update_from_data(
            db=db,
            db_obj=db_obj,
            update_data=update_data,
            current_user=current_user,
        )

    async def delete(
        self,
        db: AsyncSession,
        campaign_id: str,
        affiliate_id: str,
        current_user: str | None = None,
    ) -> AffiliateCampaignParticipants:
        return await self.repository.soft_delete(
            db=db,
            campaign_id=campaign_id,
            affiliate_id=affiliate_id,
            current_user=current_user,
        )


affiliate_campaign_service = AffiliateCampaignService()
affiliate_campaign_participant_service = AffiliateCampaignParticipantService()
