from typing import Optional

from pydantic import BaseModel

from app.schemas.base_schema import BaseLogEntity, BaseModelPagination


class RoleCreateBody(BaseModel):
    name: str
    description: Optional[str] = None

class RoleUpdateBody(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = 1


class RoleResponse(BaseLogEntity):
    id: str
    name: str
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class RolePagination(BaseModelPagination[RoleResponse]):
    pass
