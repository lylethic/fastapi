from typing import Optional

from pydantic import BaseModel

from app.schemas.base_schema import BaseLogEntity, BaseModelPagination


class PermissionUpSertBody(BaseModel):
    name: str
    description: Optional[str] = None


class PermissionResponse(BaseLogEntity):
    name: str
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class PermissionPagination(BaseModelPagination[PermissionResponse]):
    pass
