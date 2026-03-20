from typing import Optional

from pydantic import BaseModel

from app.schemas.base_schema import BaseLogEntity, BaseModelPagination


class PermissionCreateBody(BaseModel):
    name: str
    description: Optional[str] = None

class PermissionUpdateBody(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = 1


class PermissionResponse(BaseLogEntity):
    id: str
    name: str
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class PermissionPagination(BaseModelPagination[PermissionResponse]):
    pass
