from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.response import ApiResponse, success_response
from app.db.session import get_db
from app.schemas.affiliate_campaigns import (
    AffiliateCampaignCreateBody,
    AffiliateCampaignPagination,
    AffiliateCampaignParticipantCreateBody,
    AffiliateCampaignParticipantPagination,
    AffiliateCampaignParticipantQueryRequest,
    AffiliateCampaignParticipantResponse,
    AffiliateCampaignParticipantUpdateBody,
    AffiliateCampaignQueryRequest,
    AffiliateCampaignResponse,
    AffiliateCampaignUpdateBody,
)
from app.services.assistant_service import get_current_user
from app.services.affiliate_campaign_service import (
    affiliate_campaign_participant_service,
    affiliate_campaign_service,
)

router = APIRouter(prefix="/affiliate_campaigns", tags=["AffiliateCampaigns"])


@router.get(
    "",
    response_model=ApiResponse[AffiliateCampaignPagination],
    summary="Get campaigns",
)
async def get_all_campaigns(
    db: AsyncSession = Depends(get_db),
    pagination: AffiliateCampaignQueryRequest = Depends(),
):
    campaigns = await affiliate_campaign_service.get_all(db=db, pagination=pagination)
    return success_response(
        data=campaigns,
        message="Thành công",
        message_en="Campaigns retrieved successfully",
    )


@router.get(
    "/{id}",
    response_model=ApiResponse[AffiliateCampaignResponse],
    summary="Get campaign by id",
)
async def get_campaign_by_id(
    id: str,
    db: AsyncSession = Depends(get_db),
):
    campaign = await affiliate_campaign_service.get_by_id(db=db, id=id)
    return success_response(
        data=AffiliateCampaignResponse.model_validate(campaign),
        message="Thành công",
        message_en="Campaign retrieved successfully",
    )


@router.post(
    "",
    response_model=ApiResponse[AffiliateCampaignResponse],
    summary="Create campaign",
)
async def create_campaign(
    payload: AffiliateCampaignCreateBody,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    campaign = await affiliate_campaign_service.post(
        db=db,
        body=payload,
        current_user=current_user["id"],
    )
    return success_response(
        data=AffiliateCampaignResponse.model_validate(campaign),
        message="Thành công",
        message_en="Campaign created successfully",
    )


@router.put(
    "/{id}",
    response_model=ApiResponse[AffiliateCampaignResponse],
    summary="Update campaign",
)
async def update_campaign(
    id: str,
    payload: AffiliateCampaignUpdateBody,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    campaign = await affiliate_campaign_service.update(
        db=db,
        id=id,
        body=payload,
        current_user=current_user["id"],
    )
    return success_response(
        data=AffiliateCampaignResponse.model_validate(campaign),
        message="Thành công",
        message_en="Campaign updated successfully",
    )


@router.delete(
    "/{id}",
    response_model=ApiResponse[AffiliateCampaignResponse],
    summary="Delete campaign",
)
async def delete_campaign(
    id: str,
    db: AsyncSession = Depends(get_db),
):
    campaign = await affiliate_campaign_service.delete(db=db, id=id)
    return success_response(
        data=AffiliateCampaignResponse.model_validate(campaign),
        message="Thành công",
        message_en="Campaign deleted successfully",
    )


@router.get(
    "/{campaign_id}/participants",
    response_model=ApiResponse[AffiliateCampaignParticipantPagination],
    summary="Get campaign participants",
)
async def get_campaign_participants(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
    pagination: AffiliateCampaignParticipantQueryRequest = Depends(),
):
    participants = await affiliate_campaign_participant_service.get_all(
        db=db,
        campaign_id=campaign_id,
        pagination=pagination,
    )
    return success_response(
        data=participants,
        message="Thành công",
        message_en="Campaign participants retrieved successfully",
    )


@router.get(
    "/{campaign_id}/participants/{affiliate_id}",
    response_model=ApiResponse[AffiliateCampaignParticipantResponse],
    summary="Get campaign participant by ids",
)
async def get_campaign_participant(
    campaign_id: str,
    affiliate_id: str,
    db: AsyncSession = Depends(get_db),
):
    participant = await affiliate_campaign_participant_service.get_by_ids(
        db=db,
        campaign_id=campaign_id,
        affiliate_id=affiliate_id,
    )
    return success_response(
        data=AffiliateCampaignParticipantResponse.model_validate(participant),
        message="Thành công",
        message_en="Campaign participant retrieved successfully",
    )


@router.post(
    "/{campaign_id}/participants",
    response_model=ApiResponse[AffiliateCampaignParticipantResponse],
    summary="Create campaign participant",
)
async def create_campaign_participant(
    campaign_id: str,
    payload: AffiliateCampaignParticipantCreateBody,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    participant = await affiliate_campaign_participant_service.post(
        db=db,
        campaign_id=campaign_id,
        body=payload,
        current_user=current_user["id"],
    )
    return success_response(
        data=AffiliateCampaignParticipantResponse.model_validate(participant),
        message="Thành công",
        message_en="Campaign participant created successfully",
    )


@router.put(
    "/{campaign_id}/participants/{affiliate_id}",
    response_model=ApiResponse[AffiliateCampaignParticipantResponse],
    summary="Update campaign participant",
)
async def update_campaign_participant(
    campaign_id: str,
    affiliate_id: str,
    payload: AffiliateCampaignParticipantUpdateBody,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    participant = await affiliate_campaign_participant_service.update(
        db=db,
        campaign_id=campaign_id,
        affiliate_id=affiliate_id,
        body=payload,
        current_user=current_user["id"],
    )
    return success_response(
        data=AffiliateCampaignParticipantResponse.model_validate(participant),
        message="Thành công",
        message_en="Campaign participant updated successfully",
    )


@router.delete(
    "/{campaign_id}/participants/{affiliate_id}",
    response_model=ApiResponse[AffiliateCampaignParticipantResponse],
    summary="Delete campaign participant",
)
async def delete_campaign_participant(
    campaign_id: str,
    affiliate_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    participant = await affiliate_campaign_participant_service.delete(
        db=db,
        campaign_id=campaign_id,
        affiliate_id=affiliate_id,
        current_user=current_user["id"],
    )
    return success_response(
        data=AffiliateCampaignParticipantResponse.model_validate(participant),
        message="Thành công",
        message_en="Campaign participant deleted successfully",
    )
