import datetime
from typing import Optional
from pydantic import BaseModel

from app.schemas.base_schema import BaseLogEntity, BaseModelPagination


class AffiliateProfileCreateBody(BaseModel):
    user_id: str
    display_name: Optional[str] = None
    affiliate_level: Optional[str] = None
    parent_affiliate_id: Optional[str] = None
    affiliate_code: Optional[str] = None
    traffic_source: Optional[str] = None
    social_channel: Optional[str] = None
    payment_method: Optional[str] = None
    bank_account_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_name: Optional[str] = None
    tax_number: Optional[str] = None
    status: str

    # Swagger sample value
    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "uuid",
                "display_name": "Bảo Ngọc Lục Nguyễn",
                "affiliate_level": "F0",
                "parent_affiliate_id": "uuid",
                "traffic_source": "TIKTOK",
                "social_channel": "https://www.tiktok.com/@lnna198?is_from_webapp=1&sender_device=pc",
                "payment_method": "bank_transfer | ewallet | paypal",
                "bank_account_name": "Nguyễn Lục Bảo Ngọc",
                "bank_account_number": "123123123",
                "bank_name": "MB Bank",
                "tax_number": "",
                "status": "pending",
            }
        }
    }


class AffiliateProfileUpdateBody(BaseModel):
    display_name: Optional[str] = None
    affiliate_level: Optional[str] = None
    parent_affiliate_id: Optional[str] = None
    traffic_source: Optional[str] = None
    social_channel: Optional[str] = None
    payment_method: Optional[str] = None
    bank_account_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_name: Optional[str] = None
    tax_number: Optional[str] = None
    status: Optional[str] = None
    approved_at: Optional[datetime.datetime] = None

    # Swagger sample value
    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "uuid",
                "display_name": "Bảo Ngọc Lục Nguyễn",
                "affiliate_level": "F1",
                "parent_affiliate_id": "uuid",
                "traffic_source": "TIKTOK",
                "social_channel": "https://www.tiktok.com/@lnna198?is_from_webapp=1&sender_device=pc",
                "payment_method": "bank_transfer | ewallet | paypal",
                "bank_account_name": "Nguyễn Lục Bảo Ngọc",
                "bank_account_number": "123123123",
                "bank_name": "MB Bank",
                "tax_number": "",
                "status": "approved",
            }
        }
    }


class AffiliateProfileResponse(BaseLogEntity):
    id: str
    user_id: str
    affiliate_level: Optional[str] = None
    parent_affiliate_id: Optional[str] = None
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
