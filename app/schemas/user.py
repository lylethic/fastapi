from typing import Optional
from pydantic import BaseModel

from app.schemas.base_schema import BaseLogEntity, BaseModelPagination


class UserCreateBody(BaseModel):
    username: str
    email: str
    password: str
    name: str
    profile_pic: Optional[str] = None
    city: Optional[str] = None

class UserUpdateBody(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    name: Optional[str] = None
    profile_pic: Optional[str] = None
    city: Optional[str] = None
    active: Optional[bool] = True

class UserResponse(BaseLogEntity):
    id: str
    username: str
    email: str
    name: str
    profile_pic: Optional[str] = None
    city: Optional[str] = None

    model_config = {"from_attributes": True}

class UserPagination(BaseModelPagination[UserResponse]):
    pass
