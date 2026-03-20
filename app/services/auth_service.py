from typing import Optional

from fastapi.security import HTTPBearer
from app.schemas.user import LoginRequest, AuthResponse
from app.services.user_service import get_user_by_email

from sqlalchemy.ext.asyncio import AsyncSession

from app.utils import create_access_token, verify_password

from app.services.user_service import get_role_permission

security = HTTPBearer()
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # token comes from /login

async def authenticate_user(db: AsyncSession, body: LoginRequest) -> Optional[AuthResponse]:
    user = await get_user_by_email(db, body.email)
    if not user or not verify_password(body.password, user.password):
        return None
    
    permissions = await get_role_permission(db, user.id)

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
        user=permissions
    )