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
        messageEn="Role created successfully",
        status_code=status.HTTP_201_CREATED,
    )


# @router.get(
#     "",
#     response_model=ApiResponse[UserRolePagination],
#     summary="Get user roles",
# )
# async def get_all_async(
#     pagination: BaseQueryPaginationRequest = Depends(),
#     user_id: Optional[str] = Query(default=None),
#     role_id: Optional[str] = Query(default=None),
#     db: AsyncSession = Depends(get_db),
# ):

#     roles = await get_all(
#         db=db,
#         pagination=pagination,
#         user_id=user_id,
#         role_id=role_id,
#     )
#     return success_response(
#         data=roles,
#         message="Thành công",
#         messageEn="Roles retrieved successfully",
#     )


# @router.get(
#     "/detail",
#     response_model=ApiResponse[UserRoleResponse],
#     summary="Get user role by user_id and role_id",
# )
# async def get_by_id_async(
#     user_id: str = Query(...),
#     role_id: str = Query(...),
#     db: AsyncSession = Depends(get_db),
# ):

#     role = await getById(db=db, user_id=user_id, role_id=role_id)
#     return success_response(
#         data=role,
#         message="Thành công",
#         messageEn="Role retrieved successfully",
#     )


# @router.get(
#     "/by-user/{user_id}",
#     response_model=ApiResponse[list[UserRoleResponse]],
#     summary="Get roles by user id",
# )
# async def get_role_by_user_id_async(
#     user_id: str,
#     active: Optional[bool] = Query(default=True),
#     db: AsyncSession = Depends(get_db),
# ):

#     roles = await getRoleByUserId(db=db, user_id=user_id, active=active)
#     return success_response(
#         data=roles,
#         message="Thành công",
#         messageEn="Roles retrieved successfully",
#     )


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
):

    role = await update(db=db, user_id=user_id, role_id=role_id, body=payload)
    return success_response(
        data=UserRoleResponse.model_validate(role),
        message="Thành công",
        messageEn="Updated successfully",
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
        messageEn="Deleted successfully",
    )
