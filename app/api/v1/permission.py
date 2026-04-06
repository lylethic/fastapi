from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.response import ApiResponse, success_response
from app.constants.permissions import Permission
from app.db.session import get_db
from app.schemas.permission import (
    PermissionCreateBody,
    PermissionPagination,
    PermissionResponse,
    PermissionUpdateBody,
)
from app.services.assistant_service import require_permissions
from app.services.permission_service import (
    create_permission,
    delete_permission,
    get_permission,
    get_permission_by_id,
    update_permission,
)
from app.schemas.base_schema import BaseQueryPaginationRequest
from app.services.assistant_service import get_current_user

router = APIRouter(prefix="/permissions", tags=["Permissions"])


@router.post(
    "",
    response_model=ApiResponse[PermissionResponse],
    status_code=status.HTTP_200_OK,
    summary="Create permission",
)
async def create_permission_api(
    payload: PermissionCreateBody,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    permission_context: dict = Depends(
        require_permissions(Permission.SYS_ADMIN, Permission.WRITE)
    ),
):
    permission = await create_permission(
        db=db, body=payload, current_user=current_user["id"]
    )
    return success_response(
        data=PermissionResponse.model_validate(permission),
        message="Thành công",
        message_en="Permission created successfully",
        status_code=status.HTTP_200_OK,
    )


@router.get(
    "",
    response_model=ApiResponse[PermissionPagination],
    summary="Get permissions",
)
async def get_permission_api(
    db: AsyncSession = Depends(get_db),
    pagination: BaseQueryPaginationRequest = Depends(),
):
    permissions = await get_permission(db=db, pagination=pagination)
    return success_response(
        data=permissions,
        message="Thành công",
        message_en="Permissions retrieved successfully",
    )


@router.get("/{id}", summary="Get permission by id")
async def get_permission_by_id_api(id: str, db: AsyncSession = Depends(get_db)):
    permission = await get_permission_by_id(db=db, id=id)
    if not permission:
        return success_response(
            is_success=False,
            status_code=404,
            data=None,
            message="Không tìm thấy permission",
            message_en="Permission not found",
        )
    return success_response(
        data=PermissionResponse.model_validate(permission),
        message="Thành công",
        message_en="Permission retrieved successfully",
    )


@router.put("/{id}", summary="Update permission")
async def update(
    id: str,
    payload: PermissionUpdateBody,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    permission = await update_permission(
        db=db, id=id, body=payload, current_user=current_user["id"]
    )
    return success_response(
        data=PermissionResponse.model_validate(permission),
        message="Thành công",
        message_en="Permission updated successfully",
    )


@router.delete("/{id}", summary="Delete permission")
async def delete(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_permissions(Permission.DELETE)),
):
    permission = await delete_permission(db=db, id=id)
    return success_response(
        data=PermissionResponse.model_validate(permission),
        message="Thành công",
        message_en="Permission deleted successfully",
    )
