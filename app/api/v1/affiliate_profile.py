from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.response import ApiResponse, success_response

from app.constants.permissions import Permission
from app.db.session import get_db

from app.schemas.base_schema import BaseQueryPaginationRequest

from app.schemas.affiliate_profiles import (
    AffiliateProfileCreateBody,
    AffiliateProfilePagination,
    AffiliateProfileResponse,
    AffiliateProfileUpdateBody,
)

from app.services.affiliate_profile_service import affiliate_profile_service
from app.services.assistant_service import get_current_user, require_permissions

router = APIRouter(prefix="/affiliate_profiles", tags=["AffiliateProfiles"])


@router.get("/{id}", summary="Get affiliate profile by id")
async def get_by_id_async(id: str, db: AsyncSession = Depends(get_db)):
    result = await affiliate_profile_service.get_with_extend_user(db=db, id=id)
    return success_response(
        data=result,
        message="Thành công",
        message_en="Affiliate profile retrieved successfully",
    )


@router.delete("/{id}", summary="Delete affiliate profile")
async def delete(
    id: str,
    db: AsyncSession = Depends(get_db),
    permission_context: dict = Depends(
        require_permissions(Permission.SYS_ADMIN, Permission.DELETE)
    ),
):
    await affiliate_profile_service.delete(db=db, id=id)
    return success_response(
        data=None,
        message="Thành công",
        message_en="Merchant profile deleted successfully",
    )


@router.put(
    "/{id}",
    response_model=ApiResponse[AffiliateProfileResponse],
    summary="Update affiliate profile",
)
async def update_async(
    id: str,
    payload: AffiliateProfileUpdateBody,
    db: AsyncSession = Depends(get_db),
):
    result = await affiliate_profile_service.update(db=db, id=id, body=payload)
    return success_response(
        data=AffiliateProfileResponse.model_validate(result),
        message="Thành công",
        message_en="Affiliate profile updated successfully",
    )


@router.get(
    "",
    response_model=ApiResponse[AffiliateProfilePagination],
    summary="Get affiliate profiles",
)
async def get_all_async(
    db: AsyncSession = Depends(get_db),
    pagination: BaseQueryPaginationRequest = Depends(),
):
    profiles = await affiliate_profile_service.get_all(db=db, pagination=pagination)
    return success_response(
        data=profiles,
        message="Thành công",
        message_en="Affiliate profiles retrieved successfully",
    )


@router.post("", summary="Create affiliate profile")
async def post(
    payload: AffiliateProfileCreateBody,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await affiliate_profile_service.create(
        db=db,
        body=payload,
        current_user=current_user["id"],
    )
    return success_response(
        data=AffiliateProfileResponse.model_validate(result),
        message="Thành công",
        message_en="Affiliate profile created successfully",
    )
