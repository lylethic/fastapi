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
from app.services.role_permission_service import (
    create_role_permission,
    delete_role_permission,
    get_role_permission_by_id,
    get_role_permissions,
    update_role_permission,
)


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
    role_permission = await create_role_permission(db=db, body=payload)
    return success_response(
        data=RolePermissionResponse.model_validate(role_permission),
        message="Thành công",
        messageEn="Role permission created successfully",
        status_code=status.HTTP_201_CREATED,
    )


@router.get(
    "",
    response_model=ApiResponse[RolePermissionPagination],
    summary="Get role permissions",
)
async def get_role_permissions_api(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = Query(None, title="Search", description="Search by role_id or permission_id"),
    active: bool | None = Query(True),
):
    role_permissions = await get_role_permissions(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        active=active,
    )
    return success_response(
        data=role_permissions,
        message="Thành công",
        messageEn="Role permissions retrieved successfully",
    )


@router.get(
    "/{role_id}/{permission_id}",
    response_model=ApiResponse[RolePermissionResponse | None],
    summary="Get role permission by composite key",
)
async def get_role_permission_by_id_api(
    role_id: str, permission_id: str, db: AsyncSession = Depends(get_db)
):
    role_permission = await get_role_permission_by_id(
        db=db, role_id=role_id, permission_id=permission_id
    )
    if not role_permission:
        return success_response(
            isSuccess=False,
            status_code=404,
            data=None,
            message="Không tìm thấy role permission",
            messageEn="Role permission not found",
        )
    return success_response(
        data=RolePermissionResponse.model_validate(role_permission),
        message="Thành công",
        messageEn="Role permission retrieved successfully",
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
    role_permission = await update_role_permission(
        db=db,
        role_id=role_id,
        permission_id=permission_id,
        body=payload,
    )
    return success_response(
        data=RolePermissionResponse.model_validate(role_permission),
        message="Thành công",
        messageEn="Role permission updated successfully",
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
    role_permission = await delete_role_permission(
        db=db,
        role_id=role_id,
        permission_id=permission_id,
    )
    return success_response(
        data=RolePermissionResponse.model_validate(role_permission),
        message="Thành công",
        messageEn="Role permission deleted successfully",
    )
