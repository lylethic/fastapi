from typing import Optional


from fastapi import APIRouter, Depends, Query, status

from sqlalchemy.ext.asyncio import AsyncSession


from app.api.response import ApiResponse, success_response

from app.constants.permissions import Permission

from app.db.session import get_db

from app.schemas.base_schema import BaseQueryPaginationRequest

from app.schemas.user_role import (
    UserRoleCreateBody,
    UserRoleUpdateBody,
    UserRolePagination,
    UserRoleResponse,
)

from app.services.assistant_service import require_permissions

from app.services.user_role_service import (
    create,
    get_all,
    getById,
    getRoleByUserId,
    update,
    delete,
)

router = APIRouter(prefix="/user_roles", tags=["UserRoles"])


@router.post(
    "",
    response_model=ApiResponse[UserRoleResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add role for user",
)
async def create_async(
    payload: UserRoleCreateBody,
    db: AsyncSession = Depends(get_db),
):

    role = await create(db=db, body=payload)
    return success_response(
        data=UserRoleResponse.model_validate(role),
        message="Thành công",
        message_en="Role created successfully",
        status_code=status.HTTP_201_CREATED,
    )


@router.put(
    "/{user_id}/{role_id}",
    response_model=ApiResponse[UserRoleResponse],
    summary="Update role for user",
)
async def update_async(
    user_id: str,
    role_id: str,
    payload: UserRoleUpdateBody,
    db: AsyncSession = Depends(get_db),
    permission_context: dict = Depends(
        require_permissions(Permission.SYS_ADMIN, Permission.EDIT)
    ),
):

    role = await update(db=db, user_id=user_id, role_id=role_id, body=payload)
    return success_response(
        data=UserRoleResponse.model_validate(role),
        message="Thành công",
        message_en="Updated successfully",
    )


@router.delete(
    "/{user_id}/{role_id}",
    response_model=ApiResponse[str],
    summary="Delete role for user",
)
async def delete_async(
    user_id: str,
    role_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_permissions(Permission.DELETE)),
):

    result = await delete(db=db, user_id=user_id, role_id=role_id)
    return success_response(
        data=result,
        message="Thành công",
        message_en="Deleted successfully",
    )
