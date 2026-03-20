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

router = APIRouter(prefix="/permissions", tags=["Permissions"])

@router.post(
    "",
    response_model=ApiResponse[PermissionResponse],
    status_code=status.HTTP_200_OK,
    summary="Create permission"
)
async def create_permission_api(payload: PermissionCreateBody, db: AsyncSession = Depends(get_db)):
    permission = await create_permission(db=db, body=payload)
    return success_response(
        data=PermissionResponse.model_validate(permission),
        message="Thành công",
        messageEn="Permission created successfully",
        status_code=status.HTTP_200_OK,
    )


@router.get(
    "",
    response_model=ApiResponse[PermissionPagination],
    summary="Get permissions",
)
async def get_permission_api(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = Query(None, title="Search", description="Search by id or name"),
    active: bool | None = Query(1, ge=0, le=1)
):
    permissions = await get_permission(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        active=active
    )
    return success_response(
        data=permissions,
        message="Thành công",
        messageEn="Permissions retrieved successfully",
    )


@router.get("/{id}", summary="Get permission by id")
async def get_permission_by_id_api(id: str, db: AsyncSession = Depends(get_db)):
    permission = await get_permission_by_id(db=db, id=id)
    if not permission:
        return success_response(
            isSuccess=False,
            status_code=404,
            data=None,
            message="Không tìm thấy permission",
            messageEn="Permission not found",
        )
    return success_response(
        data=PermissionResponse.model_validate(permission),
        message="Thành công",
        messageEn="Permission retrieved successfully",
    )


@router.put("/{id}", summary="Update permission")
async def update(id: str, payload: PermissionUpdateBody, db: AsyncSession = Depends(get_db)):
    permission = await update_permission(db=db, id=id, body=payload)
    return success_response(
        data=PermissionResponse.model_validate(permission),
        message="Thành công",
        messageEn="Permission updated successfully",
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
        messageEn="Permission deleted successfully",
    )
