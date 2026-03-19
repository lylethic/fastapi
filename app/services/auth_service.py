from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.services.user_service import get_user_by_email
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import ALGORITHM, JWT_SECRET_KEY
from app.db.session import get_db
from app.schemas.user import LoginRequest, Token, UserPublic
from app.utils import create_access_token, verify_password

security = HTTPBearer()
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # token comes from /login

async def authenticate_user(db: AsyncSession, body: LoginRequest) -> Optional[Token]:
    user = await get_user_by_email(db, body.email)
    if not user or not verify_password(body.password, user.password):
        return None

    access_token = create_access_token(
        {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "sub": user.id,
        }
    )
    return Token(access_token=access_token)

async def authorize(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials  # only the JWT string, without "Bearer "
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
    return {
        "id": payload.get("id"),
        "email": payload.get("email"),
        "name": payload.get("name"),
    }
