from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import MerchantProfiles
from app.repositories.merchant_profile_repository import merchant_profile_repository
from app.schemas.base_schema import BaseQueryPaginationRequest
from app.schemas.merchant_profile import (
    MerchantProfilesCreateBody,
    MerchantProfilesPagination,
    MerchantProfilesResponse,
    MerchantProfilesUpdateBody,
)
from app.services.user_service import user_service


class MerchantProfilesService:
    def __init__(self) -> None:
        self.repository = merchant_profile_repository

    async def validate_create(
        self, db: AsyncSession, body: MerchantProfilesCreateBody
    ) -> None:
        existed = await user_service.get_by_id(db, body.user_id)
        if existed is None:
            raise HTTPException(status_code=400, detail="User not found")

        existing_profile = await self.repository.get_by_user_id(db, body.user_id)
        if existing_profile is not None:
            raise HTTPException(
                status_code=400, detail="Merchant profile already exists for this user"
            )

    def map_create_data(self, body: MerchantProfilesCreateBody) -> dict:
        return self._normalize_optional_strings(body.model_dump(exclude_unset=True))

    def map_update_data(self, body: MerchantProfilesUpdateBody) -> dict:
        return self._normalize_optional_strings(body.model_dump(exclude_unset=True))

    def _normalize_optional_strings(self, data: dict) -> dict:
        optional_string_fields = [
            "website",
            "contact_name",
            "contact_phone",
            "tax_code",
            "business_type",
            "billing_email",
            "address",
        ]

        for field in optional_string_fields:
            value = data.get(field)
            if isinstance(value, str):
                value = value.strip()
                data[field] = value or None

        company_name = data.get("company_name")
        if isinstance(company_name, str):
            data["company_name"] = company_name.strip()

        return data

    async def post(
        self,
        db: AsyncSession,
        body: MerchantProfilesCreateBody,
        current_user: str | None = None,
    ) -> MerchantProfiles:
        await self.validate_create(db, body)
        return await self.repository.create_from_data(
            db=db,
            data=self.map_create_data(body),
            current_user=current_user,
        )

    async def get_all(
        self, db: AsyncSession, pagination: BaseQueryPaginationRequest
    ) -> MerchantProfilesPagination:
        return await self.repository.get_all(db=db, pagination=pagination)

    async def get_by_id(self, db: AsyncSession, id: str) -> MerchantProfiles | None:
        return await self.repository.get_by_id(db=db, id=id)

    async def update(
        self,
        db: AsyncSession,
        id: str,
        body: MerchantProfilesUpdateBody,
        current_user: str | None = None,
    ) -> MerchantProfiles:
        db_obj = await self.repository.get_by_id(db=db, id=id)
        if not db_obj:
            raise HTTPException(status_code=404, detail="Merchant profile not found")

        return await self.repository.update_from_data(
            db=db,
            db_obj=db_obj,
            update_data=self.map_update_data(body),
            current_user=current_user,
        )

    async def soft_delete(self, db: AsyncSession, id: str) -> MerchantProfiles:
        return await self.repository.soft_delete(db=db, id=id)


async def get_with_extend_user(db: AsyncSession, id: str) -> MerchantProfilesResponse:
    return await merchant_profile_repository.get_with_extend_user(db=db, id=id)


service = MerchantProfilesService()
