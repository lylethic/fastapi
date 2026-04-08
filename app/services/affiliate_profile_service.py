from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AffiliateProfiles
from app.repositories.affiliate_profile_repository import affiliate_profile_repository
from app.schemas.base_schema import BaseQueryPaginationRequest
from app.schemas.affiliate_profiles import (
    AffiliateProfileCreateBody,
    AffiliateProfilePagination,
    AffiliateProfileResponse,
    AffiliateProfileUpdateBody,
)
from app.services.user_service import user_service
from app.utils.random import generate_random_code


class AffiliateProfilesService:
    def __init__(self) -> None:
        self.repository = affiliate_profile_repository

    async def validate_create(
        self, db: AsyncSession, body: AffiliateProfileCreateBody
    ) -> None:
        existed = await user_service.get_by_id(db, body.user_id)
        if existed is None:
            raise HTTPException(status_code=400, detail="User not found")

        existing_profile = await self.repository.get_by_user_id(db, body.user_id)
        if existing_profile is not None:
            raise HTTPException(
                status_code=400, detail="Affiliate profile already exists for this user"
            )

    def map_create_data(self, body: AffiliateProfileCreateBody) -> dict:
        return self._normalize_optional_strings(body.model_dump(exclude_unset=True))

    def map_update_data(self, body: AffiliateProfileUpdateBody) -> dict:
        return self._normalize_optional_strings(body.model_dump(exclude_unset=True))

    def _normalize_optional_strings(self, data: dict) -> dict:
        optional_string_fields = [
            "display_name",
            "traffic_source",
            "social_channel",
            "payment_method",
            "bank_account_name",
            "bank_account_number",
            "bank_name",
            "tax_number",
        ]

        for field in optional_string_fields:
            value = data.get(field)
            if isinstance(value, str):
                value = value.strip()
                data[field] = value or None

        return data

    async def post(
        self,
        db: AsyncSession,
        body: AffiliateProfileCreateBody,
        current_user: str | None = None,
    ) -> AffiliateProfiles:
        body.affiliate_code = generate_random_code()
        await self.validate_create(db, body)
        return await self.repository.create_from_data(
            db=db,
            data=self.map_create_data(body),
            current_user=current_user,
        )

    async def get_all(
        self, db: AsyncSession, pagination: BaseQueryPaginationRequest
    ) -> AffiliateProfilePagination:
        return await self.repository.get_all(db, pagination)

    async def get(self, db: AsyncSession, id: str) -> AffiliateProfiles | None:
        return await self.repository.get_by_id(db, id)

    async def update(
        self,
        db: AsyncSession,
        id: str,
        body: AffiliateProfileUpdateBody,
        current_user: str | None = None,
    ) -> AffiliateProfiles | None:
        db_obj = await self.repository.get_by_id(db, id)
        if not db_obj:
            raise HTTPException(status_code=404, detail="Affiliate profile not found")

        if body.status == "approved":
            body.approved_at = datetime.now()
        else:
            body.approved_at = None

        return await self.repository.update_from_data(
            db=db,
            db_obj=db_obj,
            update_data=self.map_update_data(body),
            current_user=current_user,
        )

    async def delete(self, db: AsyncSession, id: str) -> bool:
        return await self.repository.soft_delete(db, id)


async def get_with_extend_user(db: AsyncSession, id: str) -> AffiliateProfileResponse:
    return await affiliate_profile_repository.get_with_extend_user(db=db, id=id)


service = AffiliateProfilesService()
