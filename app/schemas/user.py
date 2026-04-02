from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.schemas.base_schema import BaseLogEntity, BaseModelPagination


class UserCreateBody(BaseModel):
    username: str
    email: str
    password: str
    name: str
    profile_pic: Optional[str] = None
    city: Optional[str] = None
    role_id: str


class UserRegisterBody(BaseModel):
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


class UserPermissionRoleResponse(BaseModel):
    """
    Model User with roles and permissions
    """

    id: str
    guid: str
    name: str
    email: str
    username: str
    profile_pic: Optional[str] = None
    city: Optional[str] = None
    last_login_time: Optional[datetime] = None
    roles: List[str] = []
    permissions: List[str] = []


class UserPagination(BaseModelPagination[UserResponse]):
    pass


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=6)


class UserPublic(BaseModel):
    email: str
    name: Optional[str] = None


class AuthResponse(BaseModel):
    access_token: str
    expires_at: Optional[datetime] = None
    user: Optional[object]
