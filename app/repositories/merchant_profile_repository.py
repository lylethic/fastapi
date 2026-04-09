import json

from fastapi import HTTPException
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import MerchantProfiles
from app.repositories.base_repository import BaseRepository
from app.schemas.merchant_profile import (
    MerchantProfilesPagination,
    MerchantProfilesResponse,
)


QUERY_EXTEND_USER = """
SELECT mp.* , JSON_OBJECT('email', u.email,
              'username', u.username,
              'name', u.name,
              'profile_pic', u.profile_pic) as extend_user
FROM merchant_profiles as mp
    left join users as u on mp.user_id = u.id
WHERE mp.id = :id
"""


class MerchantProfileRepository(
    BaseRepository[
        MerchantProfiles,
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

    async def get_by_user_id(
        self, db: AsyncSession, user_id: str
    ) -> MerchantProfiles | None:
        stmt = select(self.model).where(
            self.model.user_id == user_id,
            *self.base_filters(),
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_extend_user(
        self, db: AsyncSession, id: str
    ) -> MerchantProfilesResponse:
        result = await db.execute(text(QUERY_EXTEND_USER), {"id": id})
        row = result.mappings().first()

        if not row:
            raise HTTPException(status_code=404, detail="Merchant profile not found")

        merchant_profile = dict(row)
        if isinstance(merchant_profile["extend_user"], str):
            merchant_profile["extend_user"] = json.loads(
                merchant_profile["extend_user"]
            )

        merchant_profile["extend_user"] = merchant_profile.get("extend_user") or None
        return MerchantProfilesResponse.model_validate(merchant_profile)


merchant_profile_repository = MerchantProfileRepository()
