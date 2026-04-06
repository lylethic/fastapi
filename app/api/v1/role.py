from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.response import ApiResponse, success_response
from app.constants.permissions import Permission
from app.db.session import get_db
from app.schemas.role import (
    RolePagination,
    RoleResponse,
    RoleCreateBody,
    RoleUpdateBody,
)
from app.schemas.base_schema import BaseQueryPaginationRequest
from app.services.assistant_service import get_current_user
from app.services.assistant_service import require_permissions
from app.services.role_service import role_service

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.post(
    "",
    response_model=ApiResponse[RoleResponse],
    status_code=status.HTTP_200_OK,
    summary="Create role",
)
async def create_role_api(
    payload: RoleCreateBody,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    permission_context: dict = Depends(
        require_permissions(Permission.SYS_ADMIN, Permission.WRITE)
    ),
):
    role = await role_service.create(
        db=db, body=payload, current_user=current_user["id"]
    )
    return success_response(
        data=RoleResponse.model_validate(role),
        message="Thành công",
        message_en="Role created successfully",
        status_code=status.HTTP_200_OK,
    )


@router.get(
    "",
    response_model=ApiResponse[RolePagination],
    summary="Get roles",
)
async def get_role_api(
    db: AsyncSession = Depends(get_db),
    pagination: BaseQueryPaginationRequest = Depends(),
):
    roles = await role_service.get_all(db=db, pagination=pagination)
    return success_response(
        data=roles,
        message="Thành công",
        message_en="Roles retrieved successfully",
    )


@router.get("/{id}", summary="Get role by id")
async def get_role_by_id_api(id: str, db: AsyncSession = Depends(get_db)):
    role = await role_service.get_by_id(db=db, id=id)
    if not role:
        return success_response(
            is_success=False,
            status_code=404,
            data=None,
            message="Không tìm thấy role",
            message_en="Role not found",
        )
    return success_response(
        data=RoleResponse.model_validate(role),
        message="Thành công",
        message_en="Role retrieved successfully",
    )


@router.put("/{id}", summary="Update role")
async def update(
    id: str,
    payload: RoleUpdateBody,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    require_permissions: dict = Depends(
        require_permissions(Permission.SYS_ADMIN, Permission.EDIT)
    ),
):
    role = await role_service.update(
        db=db, id=id, body=payload, current_user=current_user["id"]
    )
    return success_response(
        data=RoleResponse.model_validate(role),
        message="Thành công",
        message_en="Role updated successfully",
    )


@router.delete("/{id}", summary="Delete role")
async def delete(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(
        require_permissions(Permission.SYS_ADMIN, Permission.DELETE)
    ),
):
    role = await role_service.soft_delete(db=db, id=id)
    return success_response(
        data=RoleResponse.model_validate(role),
        message="Thành công",
        message_en="Role deleted successfully",
    )
