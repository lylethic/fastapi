from fastapi import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Roles
from app.providers.baseProvider import BaseProvider
from app.schemas.base_schema import BaseQueryPaginationRequest
from app.schemas.affiliate_profiles import (
    AffiliateProfileCreateBody,
    AffiliateProfilePagiantion,
    AffiliateProfileResponse,
    AffiliateProfileUpdateBody,
)
