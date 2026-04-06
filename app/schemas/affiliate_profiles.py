from typing import Optional
from pydantic import BaseModel

from app.schemas.base_schema import BaseLogEntity, BaseModelPagination


class AffiliateProfileCreateBody(BaseModel):
    user_id: str
    display_name: str
    affiliate_code: str
    traffic_source: str
    social_channel: str
    payment_method: str
    bank_account_name: str
    bank_account_number: str
    bank_name: str
    tax_number: str
    status: str


class AffiliateProfileUpdateBody(BaseModel):
    display_name: str
    traffic_source: str
    social_channel: str
    payment_method: str
    bank_account_name: str
    bank_account_number: str
    bank_name: str
    tax_number: str
    status: str
    approved_at: str


class AffiliateProfileResponse(BaseLogEntity):
    id: str
    user_id: str
    display_name: str
    affiliate_code: str
    traffic_source: str
    social_channel: str
    payment_method: str
    bank_account_name: str
    bank_account_number: str
    bank_name: str
    tax_number: str
    status: str
    approved_at: str

    model_config: {"from_attributes": True}


class AffiliateProfilePagiantion(BaseModelPagination[AffiliateProfileResponse]):
    pass
