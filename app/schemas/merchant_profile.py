from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.schemas.base_schema import BaseLogEntity, BaseModelPagination

from app.constants.merchant_profile_enum import BusinessType


class MerchantProfilesCreateBody(BaseModel):
    user_id: str
    company_name: str
    website: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    tax_code: Optional[str] = None
    business_type: Optional[str] = None
    billing_email: Optional[str] = None
    address: Optional[str] = None


class MerchantProfilesUpdateBody(BaseModel):
    company_name: Optional[str] = None
    website: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    tax_code: Optional[str] = None
    business_type: Optional[str] = None
    billing_email: Optional[str] = None
    address: Optional[str] = None


class MerchantProfilesResponse(BaseLogEntity):
    id: str
    user_id: str
    company_name: str
    website: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    tax_code: Optional[str] = None
    business_type: Optional[str] = None
    billing_email: Optional[str] = None
    address: Optional[str] = None
    extend_user: Optional[object] = None

    model_config = {"from_attributes": True}


class MerchantProfilesPagination(BaseModelPagination[MerchantProfilesResponse]):
    pass
