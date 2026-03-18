from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.response import ApiResponse, success_response
from app.db.session import get_db
from app.schemas.permission import PermissionPagination, PermissionResponse, PermissionUpSertBody
from app.services.permission_service import (
    create_permission,
    get_permission,
    get_permission_by_id,
    update_permission,
)


router = APIRouter(prefix="/permissions", tags=["Permissions"])


@router.post(
    "",
    response_model=ApiResponse[PermissionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create permission",
    description="Tao moi mot permission trong he thong",
)
def create_permission_api(payload: PermissionUpSertBody, db: Session = Depends(get_db)):
    permission = create_permission(
        db=db,
        name=payload.name,
        description=payload.description,
    )
    return success_response(
        data=PermissionResponse.model_validate(permission),
        message="Tao permission thanh cong",
        message_en="Permission created successfully",
        status_code=status.HTTP_201_CREATED,
    )


@router.get(
    "",
    response_model=ApiResponse[PermissionPagination],
    summary="Get permissions",
)
def get_permission_api(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = Query(None, title="Search", description="Search by id or name"),
):
    permissions = get_permission(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
    )
    return success_response(
        data=permissions,
        message="Lay danh sach permission thanh cong",
        message_en="Permissions retrieved successfully",
    )


@router.get("/{id}", summary="Get permission by id")
def get_permission_by_id_api(id: str, db: Session = Depends(get_db)):
    permission = get_permission_by_id(db=db, id=id)
    if not permission:
        return success_response(
            isSuccess=False,
            status_code=404,
            data=None,
            message="Permission not found",
            message_en="Permission not found",
        )
    return success_response(
        data=PermissionResponse.model_validate(permission),
        message="Lay permission thanh cong",
        message_en="Permission retrieved successfully",
    )


@router.put("/{id}", summary="Update permission")
def update(id: str,  payload: PermissionUpSertBody, db: Session = Depends(get_db)):
    permission = update_permission(
        db=db, 
        id=id, 
        name=payload.name, 
        description=payload.description
    )
    return success_response(
        data=PermissionResponse.model_validate(permission),
        message="Cap nhat permission thanh cong",
        message_en="Permission updated successfully",
    )
