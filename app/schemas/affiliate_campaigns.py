import datetime
import decimal
from typing import Optional

from fastapi import Query
from pydantic import BaseModel, Field

from app.db.models import (
    AffiliateCampaignParticipantsStatus,
    AffiliateCampaignsAttributionModel,
    AffiliateCampaignsCampaignType,
    AffiliateCampaignsStatus,
)
from app.schemas.base_schema import BaseLogEntity, BaseModelPagination, BaseQueryPaginationRequest


class AffiliateCampaignQueryRequest(BaseQueryPaginationRequest):
    def __init__(
        self,
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
        active: bool | None = Query(True),
        search: Optional[str] = Query(None),
        merchant_id: Optional[str] = Query(None),
        status: Optional[AffiliateCampaignsStatus] = Query(None),
        campaign_type: Optional[AffiliateCampaignsCampaignType] = Query(None),
    ) -> None:
        super().__init__(page=page, page_size=page_size, active=active, search=search)
        self.merchant_id = merchant_id
        self.status = status
        self.campaign_type = campaign_type


class AffiliateCampaignCreateBody(BaseModel):
    merchant_id: str
    name: str
    campaign_type: AffiliateCampaignsCampaignType
    commission_value: decimal.Decimal = Field(..., ge=0)
    cookie_days: int = Field(30, ge=1)
    attribution_model: AffiliateCampaignsAttributionModel = (
        AffiliateCampaignsAttributionModel.LAST_CLICK
    )
    status: AffiliateCampaignsStatus = AffiliateCampaignsStatus.DRAFT
    description: Optional[str] = None
    landing_page_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    commission_rate: Optional[decimal.Decimal] = Field(None, ge=0)
    start_date: Optional[datetime.datetime] = None
    end_date: Optional[datetime.datetime] = None
    terms_conditions: Optional[str] = None


class AffiliateCampaignUpdateBody(BaseModel):
    merchant_id: Optional[str] = None
    name: Optional[str] = None
    campaign_type: Optional[AffiliateCampaignsCampaignType] = None
    commission_value: Optional[decimal.Decimal] = Field(None, ge=0)
    cookie_days: Optional[int] = Field(None, ge=1)
    attribution_model: Optional[AffiliateCampaignsAttributionModel] = None
    status: Optional[AffiliateCampaignsStatus] = None
    description: Optional[str] = None
    landing_page_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    commission_rate: Optional[decimal.Decimal] = Field(None, ge=0)
    start_date: Optional[datetime.datetime] = None
    end_date: Optional[datetime.datetime] = None
    terms_conditions: Optional[str] = None


class AffiliateCampaignResponse(BaseLogEntity):
    id: str
    merchant_id: str
    name: str
    campaign_type: AffiliateCampaignsCampaignType
    commission_value: decimal.Decimal
    cookie_days: int
    attribution_model: AffiliateCampaignsAttributionModel
    status: AffiliateCampaignsStatus
    description: Optional[str] = None
    landing_page_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    commission_rate: Optional[decimal.Decimal] = None
    start_date: Optional[datetime.datetime] = None
    end_date: Optional[datetime.datetime] = None
    terms_conditions: Optional[str] = None

    model_config = {"from_attributes": True}


class AffiliateCampaignPagination(BaseModelPagination[AffiliateCampaignResponse]):
    pass


class AffiliateCampaignParticipantQueryRequest(BaseQueryPaginationRequest):
    def __init__(
        self,
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
        active: bool | None = Query(True),
        search: Optional[str] = Query(None),
        affiliate_id: Optional[str] = Query(None),
        status: Optional[AffiliateCampaignParticipantsStatus] = Query(None),
    ) -> None:
        super().__init__(page=page, page_size=page_size, active=active, search=search)
        self.affiliate_id = affiliate_id
        self.status = status


class AffiliateCampaignParticipantCreateBody(BaseModel):
    affiliate_id: str
    status: AffiliateCampaignParticipantsStatus = (
        AffiliateCampaignParticipantsStatus.PENDING
    )
    note: Optional[str] = None


class AffiliateCampaignParticipantUpdateBody(BaseModel):
    status: Optional[AffiliateCampaignParticipantsStatus] = None
    note: Optional[str] = None


class AffiliateCampaignParticipantResponse(BaseLogEntity):
    campaign_id: str
    affiliate_id: str
    status: AffiliateCampaignParticipantsStatus
    joined_at: datetime.datetime
    approved_at: Optional[datetime.datetime] = None
    note: Optional[str] = None

    model_config = {"from_attributes": True}


class AffiliateCampaignParticipantPagination(
    BaseModelPagination[AffiliateCampaignParticipantResponse]
):
    pass
