from fastapi import APIRouter, Depends, File, Query, UploadFile, status, HTTPException
from app.services.auth_service import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.response import ApiResponse, success_response
from app.db.session import get_db
from app.schemas.user import (
    UserCreateBody,
    UserPagination,
    UserPermissionRoleResponse,
    UserResponse,
    UserUpdateBody
)
from app.services.user_service import (
   create_user,
   get_user,
   get_user_by_id,
   update_user,
   delete_user,
   uploadImage,
   get_user_detail
)

router = APIRouter(prefix="/users", tags=["Users"])

@router.get(
    "",
    response_model=ApiResponse[UserPagination],
    summary="Get users",
)
async def get_user_api(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = Query(None, title="Search", description="Search by id or name"),
    active: bool | None = Query(1, ge=0, le=1)
):
    data = await get_user(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        active=active
    )
    return success_response(
        data=data,
        message="Thành công",
        message_en="Users retrieved successfully",
    )


@router.get(
    "/me",
    response_model=ApiResponse[UserPermissionRoleResponse],
    summary="Get my info",
)
async def get_my_detail(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    data = await get_user_detail(db=db, user_id=current_user["id"])
    return success_response(
        data=UserPermissionRoleResponse.model_validate(data),
        message="Thành công",
        message_en="User retrieved successfully",
    )

@router.get("/{id}", summary="Get user by id")
async def get_user_by_id_api(id: str, db: AsyncSession = Depends(get_db)):
    data = await get_user_by_id(db=db, id=id)
    if not data:
        return success_response(
            isSuccess=False,
            status_code=404,
            data=None,
            message="Không tìm thấy user",
            message_en="User not found",
        )
    return success_response(
        data=UserResponse.model_validate(data),
        message="Thành công",
        message_en="User retrieved successfully",
    )

@router.post(
    "",
    response_model=ApiResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Create user"
)
async def create_user_api(payload: UserCreateBody, db: AsyncSession = Depends(get_db)):
    user = await create_user(db=db, body=payload)
    return success_response(
        data=UserResponse.model_validate(user),
        message="Thành công",
        message_en="User created successfully",
        status_code=status.HTTP_200_OK,
    )

@router.put("/{id}", summary="Update user")
async def update(id: str, payload: UserUpdateBody, db: AsyncSession = Depends(get_db)):
    data = await update_user(db=db, id=id, body=payload)
    return success_response(
        data=UserResponse.model_validate(data),
        message="Thành công",
        message_en="User updated successfully",
    )

@router.delete("/{id}", summary="Delete user")
async def delete(id: str, db: AsyncSession = Depends(get_db)):
    data = await delete_user(db=db, id=id)
    return success_response(
        data=UserResponse.model_validate(data),
        message="Thành công",
        message_en="User deleted successfully",
    )

@router.post(
    "/{id}/upload",
    response_model=ApiResponse[UserResponse],
    summary="Upload user image",
)
async def upload_image(id: str, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    data = await uploadImage(db=db, id=id, file=file)
    
    if not data:
        return success_response(
        isSuccess=False,
        status_code=400,
        data=UserResponse.model_validate(data),
        message="Thành công",
        message_en="User image uploaded successfully",
    )
    return success_response(
        data=UserResponse.model_validate(data),
        message="Thành công",
        message_en="User image uploaded successfully",
    )

