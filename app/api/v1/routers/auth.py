from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.response import ApiResponse, success_response
from app.db.session import get_db
from app.schemas.user import LoginRequest, AuthResponse, UserRegisterBody
from app.services.auth_service import authenticate_user, register_customer

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=ApiResponse[AuthResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register",
)
async def register(payload: UserRegisterBody, db: AsyncSession = Depends(get_db)):
    result = await register_customer(db=db, body=payload)
    return success_response(
        data=result,
        message="Thành công",
        message_en="Register successfully",
        status_code=status.HTTP_200_OK,
    )


@router.post(
    "/login",
    response_model=ApiResponse[AuthResponse],
    status_code=status.HTTP_200_OK,
    summary="Login",
)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await authenticate_user(db=db, body=payload)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invalid email or password",
        )

    return success_response(
        data=result,
        message="Thành công",
        message_en="Login successfully",
        status_code=status.HTTP_200_OK,
    )
