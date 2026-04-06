from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base_schema import BaseLogEntity, BaseModelPagination


class RolePermissionCreateBody(BaseModel):
    role_id: str
    permission_id: str = Field(alias="permisison_id")

    model_config = ConfigDict(populate_by_name=True)

class RolePermissionUpdateBody(BaseModel):
    role_id: Optional[str] = None
    permission_id: Optional[str] = Field(default=None, alias="permisison_id")
    active: Optional[bool] = True

    model_config = ConfigDict(populate_by_name=True)


class RolePermissionResponse(BaseLogEntity):
    role_id: str
    permission_id: str

    model_config = {"from_attributes": True}


class RolePermissionPagination(BaseModelPagination[RolePermissionResponse]):
    pass
