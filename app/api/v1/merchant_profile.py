from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.response import ApiResponse, success_response

from app.db.session import get_db

from app.schemas.base_schema import BaseQueryPaginationRequest

from app.schemas.merchant_profile_schema import (
    MerchantProfilesCreateBody,
    MerchantProfilesPagination,
    MerchantProfilesResponse,
    MerchantProfilesUpdateBody,
)

from app.services.merchant_profile_service import service, get_with_extend_user
from app.services.assistant_service import get_current_user


router = APIRouter(prefix="/merchant_profiles", tags=["MerchantProfiles"])


@router.get("/{id}", summary="Get merchant profile by id")
async def get_by_id_async(id: str, db: AsyncSession = Depends(get_db)):
    result = await get_with_extend_user(db=db, id=id)
    return success_response(
        data=result,
        message="Thành công",
        message_en="Merchant profile retrieved successfully",
    )


@router.delete("/{id}", summary="Delete merchant profile")
async def delete(
    id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await service.soft_delete(db=db, id=id)
    return success_response(
        data=MerchantProfilesResponse.model_validate(result),
        message="Thành công",
        message_en="Merchant profile deleted successfully",
    )


@router.put(
    "/{id}",
    response_model=ApiResponse[MerchantProfilesResponse],
    summary="Update merchant profile",
)
async def update_async(
    id: str,
    payload: MerchantProfilesUpdateBody,
    db: AsyncSession = Depends(get_db),
):
    result = await service.update(db=db, id=id, body=payload)
    return success_response(
        data=MerchantProfilesResponse.model_validate(result),
        message="Thành công",
        message_en="Merchant profile updated successfully",
    )


@router.get(
    "",
    response_model=ApiResponse[MerchantProfilesPagination],
    summary="Get merchant profiles",
)
async def get_all_async(
    db: AsyncSession = Depends(get_db),
    pagination: BaseQueryPaginationRequest = Depends(),
):
    roles = await service.get_all(db=db, pagination=pagination)
    return success_response(
        data=roles,
        message="Thành công",
        message_en="Roles retrieved successfully",
    )


@router.post("", summary="Create merchant profile")
async def post(
    payload: MerchantProfilesCreateBody,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await service.post(db=db, body=payload, current_user=current_user["id"])
    return success_response(
        data=MerchantProfilesResponse.model_validate(result),
        message="Thành công",
        message_en="Merchant profile created successfully",
    )
