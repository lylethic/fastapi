from typing import Optional
from datetime import datetime, timedelta, timezone

from fastapi.security import HTTPBearer
from app.schemas.user import LoginRequest, AuthResponse, UserRegisterBody
from app.services.user_service import get_user_by_email, register_user

from sqlalchemy.ext.asyncio import AsyncSession

from app.utils import create_access_token, verify_password

from app.services.user_service import get_role_permission

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES

security = HTTPBearer()
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # token comes from /login


async def authenticate_user(
    db: AsyncSession, body: LoginRequest
) -> Optional[AuthResponse]:
    user = await get_user_by_email(db, body.email)
    if not user or not verify_password(body.password, user.password):
        return None

    expires = datetime.now(timezone.utc) + timedelta(
        minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    permissions = await get_role_permission(db, user.id)

    access_token = create_access_token(
        {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "sub": user.id,
        }
    )
    return AuthResponse(access_token=access_token, expires_at=expires, user=permissions)


async def register_customer(
    db: AsyncSession, body: UserRegisterBody
) -> Optional[AuthResponse]:
    # Add new
    addNewUser = await register_user(db, body)

    expires = datetime.now(timezone.utc) + timedelta(
        minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    permissions = await get_role_permission(db, addNewUser.id)

    access_token = create_access_token(
        {
            "id": addNewUser.id,
            "email": addNewUser.email,
            "name": addNewUser.name,
            "sub": addNewUser.id,
        }
    )
    return AuthResponse(access_token=access_token, expires_at=expires, user=permissions)
