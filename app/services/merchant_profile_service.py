from fastapi import HTTPException
from sqlalchemy import or_, and_, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import MerchantProfiles
import json
from app.providers.baseProvider import BaseProvider

from app.schemas.base_schema import BaseQueryPaginationRequest

from app.schemas.merchant_profile_schema import (
    MerchantProfilesCreateBody,
    MerchantProfilesPagination,
    MerchantProfilesUpdateBody,
    MerchantProfilesResponse,
)


from app.services.user_service import user_service


class MerchantProfilesService(
    BaseProvider[
        MerchantProfiles,
        MerchantProfilesCreateBody,
        MerchantProfilesUpdateBody,
        MerchantProfilesResponse,
        MerchantProfilesPagination,
    ]
):

    def __init__(self) -> None:
        super().__init__(
            model=MerchantProfiles,
            response_schema=MerchantProfilesResponse,
            pagination_schema=MerchantProfilesPagination,
            not_found_message="Merchant profile not found",
            already_exists_message="Merchant profile already exists",
            search_fields=[
                "company_name",
                "website",
                "contact_name",
                "contact_phone",
                "tax_code",
                "business_type",
                "billing_email",
            ],
        )

    async def validate_create(
        self, db: AsyncSession, body: MerchantProfilesCreateBody
    ) -> None:
        existed = await user_service.get_by_id(db, body.user_id)

        if existed is None:
            raise HTTPException(status_code=400, detail="User not found")

        existing_profile = await self.get_by_user_id(db, body.user_id)

        if existing_profile is not None:
            raise HTTPException(
                status_code=400, detail="Merchant profile already exists for this user"
            )

    async def get_by_user_id(
        self, db: AsyncSession, user_id: str
    ) -> MerchantProfiles | None:
        stmt = select(self.model).where(
            self.model.user_id == user_id,
            *self.base_filters(),
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

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


async def get_with_extend_user(db: AsyncSession, id: str) -> MerchantProfilesResponse:
    result = await db.execute(text(QUERY_EXTEND_USER), {"id": id})
    row = result.mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="Merchant profile not found")

    merchant_profile = dict(row)
    if isinstance(merchant_profile["extend_user"], str):
        merchant_profile["extend_user"] = json.loads(merchant_profile["extend_user"])

    merchant_profile["extend_user"] = merchant_profile.get("extend_user") or None

    return MerchantProfilesResponse.model_validate(merchant_profile)


service = MerchantProfilesService()


QUERY_EXTEND_USER = """
SELECT mp.* , JSON_OBJECT('email', u.email,
              'username', u.username,
              'name', u.name,
              'profile_pic', u.profile_pic) as extend_user
FROM merchant_profiles as mp
    left join users as u on mp.user_id = u.id
WHERE mp.id = :id
"""
