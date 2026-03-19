from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.response import ApiResponse, success_response
from app.db.session import get_db
from app.schemas.user import LoginRequest, Token
from app.services.auth_service import (
    authenticate_user
)

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post(
    "/login",
    response_model=ApiResponse[Token],
    status_code=status.HTTP_200_OK,
    summary="Login"
)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await authenticate_user(db=db, body=payload)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return success_response(
        data=result,
        message="Thành công",
        message_en="Login successfully",
        status_code=status.HTTP_200_OK,
    )
