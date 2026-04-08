import datetime
from typing import Optional
from pydantic import BaseModel

from app.schemas.base_schema import BaseLogEntity, BaseModelPagination


class AffiliateProfileCreateBody(BaseModel):
    user_id: str
    display_name: Optional[str] = None
    affiliate_code: Optional[str] = None
    traffic_source: Optional[str] = None
    social_channel: Optional[str] = None
    payment_method: Optional[str] = None
    bank_account_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_name: Optional[str] = None
    tax_number: Optional[str] = None
    status: str


class AffiliateProfileUpdateBody(BaseModel):
    display_name: Optional[str] = None
    traffic_source: Optional[str] = None
    social_channel: Optional[str] = None
    payment_method: Optional[str] = None
    bank_account_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_name: Optional[str] = None
    tax_number: Optional[str] = None
    status: Optional[str] = None
    approved_at: Optional[datetime.datetime] = None


class AffiliateProfileResponse(BaseLogEntity):
    id: str
    user_id: str
    display_name: Optional[str] = None
    affiliate_code: Optional[str] = None
    traffic_source: Optional[str] = None
    social_channel: Optional[str] = None
    payment_method: Optional[str] = None
    bank_account_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_name: Optional[str] = None
    tax_number: Optional[str] = None
    status: Optional[str] = None
    approved_at: Optional[datetime.datetime] = None
    extend_user: Optional[object] = None
    model_config = {"from_attributes": True}


class AffiliateProfilePagination(BaseModelPagination[AffiliateProfileResponse]):
    pass
