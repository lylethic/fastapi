import json

from fastapi import HTTPException
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AffiliateProfiles
from app.repositories.base_repository import BaseRepository
from app.schemas.affiliate_profiles import (
    AffiliateProfileCreateBody,
    AffiliateProfilePagination,
    AffiliateProfileResponse,
    AffiliateProfileUpdateBody,
)

QUERY_EXTEND_USER = """
SELECT ap.* , JSON_OBJECT('email', u.email,
              'username', u.username,
              'name', u.name,
              'profile_pic', u.profile_pic) as extend_user
FROM affiliate_profiles as ap
    left join users as u on ap.user_id = u.id
WHERE ap.id = :id
"""


class AffiliateProfileRepository(
    BaseRepository[
        AffiliateProfiles,
        AffiliateProfileCreateBody,
        AffiliateProfileUpdateBody,
        AffiliateProfileResponse,
        AffiliateProfilePagination,
    ]
):
    def __init__(self) -> None:
        super().__init__(
            model=AffiliateProfiles,
            response_schema=AffiliateProfileResponse,
            pagination_schema=AffiliateProfilePagination,
            not_found_message="Affiliate profile not found",
            already_exists_message="Affiliate profile already exists",
            search_fields=["display_name", "affiliate_code", "status"],
        )

    async def get_by_user_id(
        self, db: AsyncSession, user_id: str
    ) -> AffiliateProfiles | None:
        stmt = select(self.model).where(
            self.model.user_id == user_id,
            *self.base_filters(),
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_extend_user(
        self, db: AsyncSession, id: str
    ) -> AffiliateProfileResponse:
        result = await db.execute(text(QUERY_EXTEND_USER), {"id": id})
        row = result.mappings().first()

        if not row:
            raise HTTPException(status_code=404, detail="Affiliate profile not found")

        affiliate_profile = dict(row)
        if isinstance(affiliate_profile["extend_user"], str):
            affiliate_profile["extend_user"] = json.loads(
                affiliate_profile["extend_user"]
            )

        affiliate_profile["extend_user"] = affiliate_profile.get("extend_user") or None
        return AffiliateProfileResponse.model_validate(affiliate_profile)


affiliate_profile_repository = AffiliateProfileRepository()
