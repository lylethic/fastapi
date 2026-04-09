from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.response import ApiResponse, success_response
from app.constants.permissions import Permission
from app.db.session import get_db
from app.schemas.rolepermission import (
    RolePermissionCreateBody,
    RolePermissionPagination,
    RolePermissionResponse,
    RolePermissionUpdateBody,
)
from app.services.assistant_service import require_permissions
from app.schemas.base_schema import BaseQueryPaginationRequest
from app.services.role_permission_service import role_permission_service

router = APIRouter(prefix="/role-permissions", tags=["Role Permissions"])


@router.post(
    "",
    response_model=ApiResponse[RolePermissionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create role permission",
)
async def create_role_permission_api(
    payload: RolePermissionCreateBody, db: AsyncSession = Depends(get_db)
):
    role_permission = await role_permission_service.create(db=db, body=payload)
    return success_response(
        data=RolePermissionResponse.model_validate(role_permission),
        message="Thành công",
        message_en="Role permission created successfully",
        status_code=status.HTTP_201_CREATED,
    )


@router.get(
    "",
    response_model=ApiResponse[RolePermissionPagination],
    summary="Get role permissions",
)
async def get_role_permissions_api(
    db: AsyncSession = Depends(get_db),
    pagination: BaseQueryPaginationRequest = Depends(),
):
    role_permissions = await role_permission_service.get_role_permissions(
        db=db, pagination=pagination
    )
    return success_response(
        data=role_permissions,
        message="Thành công",
        message_en="Role permissions retrieved successfully",
    )


@router.get(
    "/{role_id}/{permission_id}",
    response_model=ApiResponse[RolePermissionResponse | None],
    summary="Get role permission by composite key",
)
async def get_role_permission_by_id_api(
    role_id: str, permission_id: str, db: AsyncSession = Depends(get_db)
):
    role_permission = await role_permission_service.get_by_keys(
        db=db, role_id=role_id, permission_id=permission_id
    )
    if not role_permission:
        return success_response(
            is_success=False,
            status_code=404,
            data=None,
            message="Không tìm thấy role permission",
            message_en="Role permission not found",
        )
    return success_response(
        data=RolePermissionResponse.model_validate(role_permission),
        message="Thành công",
        message_en="Role permission retrieved successfully",
    )


@router.put(
    "/{role_id}/{permission_id}",
    response_model=ApiResponse[RolePermissionResponse],
    summary="Update role permission",
)
async def update_role_permission_api(
    role_id: str,
    permission_id: str,
    payload: RolePermissionUpdateBody,
    db: AsyncSession = Depends(get_db),
):
    role_permission = await role_permission_service.update_by_keys(
        db=db,
        role_id=role_id,
        permission_id=permission_id,
        body=payload,
    )
    return success_response(
        data=RolePermissionResponse.model_validate(role_permission),
        message="Thành công",
        message_en="Role permission updated successfully",
    )


@router.delete(
    "/{role_id}/{permission_id}",
    response_model=ApiResponse[RolePermissionResponse],
    summary="Delete role permission",
)
async def delete_role_permission_api(
    role_id: str,
    permission_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_permissions(Permission.DELETE)),
):
    await role_permission_service.soft_delete_by_keys(
        db=db,
        role_id=role_id,
        permission_id=permission_id,
    )
    return success_response(
        data=None,
        message="Thành công",
        message_en="Role permission deleted successfully",
    )
