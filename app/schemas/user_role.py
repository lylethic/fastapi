from typing import Optional

from pydantic import BaseModel

from app.schemas.base_schema import BaseLogEntity, BaseModelPagination


class UserRoleCreateBody(BaseModel):
    user_id: str
    role_id: str

class UserRoleUpdateBody(BaseModel):
    role_id: Optional[str] = None
    active: Optional[bool] = True


class UserRoleResponse(BaseLogEntity):
    user_id: str
    role_id: str

    model_config = {"from_attributes": True}


class UserRolePagination(BaseModelPagination[UserRoleResponse]):
    pass
