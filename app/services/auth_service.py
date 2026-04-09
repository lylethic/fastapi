from typing import Optional
from datetime import datetime, timedelta, timezone

from app.schemas.user import LoginRequest, AuthResponse, UserRegisterBody
from app.services.user_service import user_service

from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.token_utils import create_access_token, verify_password

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES


class AuthService:
    async def authenticate(
        self, db: AsyncSession, body: LoginRequest
    ) -> Optional[AuthResponse]:
        user = await user_service.get_by_email(db, body.email)
        if not user or not verify_password(body.password, user.password):
            return None

        expires = datetime.now(timezone.utc) + timedelta(
            minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        permissions = await user_service.get_role_permission(db, user.id)

        access_token = create_access_token(
            {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "sub": user.id,
            }
        )
        return AuthResponse(
            access_token=access_token,
            expires_at=expires,
            user=permissions,
        )

    async def register(self, db: AsyncSession, body: UserRegisterBody) -> AuthResponse:
        user = await user_service.register(db, body)

        expires = datetime.now(timezone.utc) + timedelta(
            minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        permissions = await user_service.get_role_permission(db, user.id)

        access_token = create_access_token(
            {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "sub": user.id,
            }
        )
        return AuthResponse(
            access_token=access_token,
            expires_at=expires,
            user=permissions,
        )


auth_service = AuthService()
