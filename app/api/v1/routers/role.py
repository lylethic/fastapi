from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.response import ApiResponse, success_response
from app.db.session import get_db
from app.schemas.role import RolePagination, RoleResponse, RoleCreateBody, RoleUpdateBody
from app.services.role_service import (
   create_role, 
   get_role,
   get_role_by_id,
   update_role,
   delete_role
)

router = APIRouter(prefix="/roles", tags=["Roles"])

@router.post(
    "",
    response_model=ApiResponse[RoleResponse],
    status_code=status.HTTP_200_OK,
    summary="Create role"
)
async def create_role_api(payload: RoleCreateBody, db: AsyncSession = Depends(get_db)):
    role = await create_role(db=db, body=payload)
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
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = Query(None, title="Search", description="Search by id or name"),
    active: bool | None = Query(1, ge=0, le=1)
):
    roles = await get_role(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        active=active
    )
    return success_response(
        data=roles,
        message="Thành công",
        message_en="Roles retrieved successfully",
    )


@router.get("/{id}", summary="Get role by id")
async def get_role_by_id_api(id: str, db: AsyncSession = Depends(get_db)):
    role = await get_role_by_id(db=db, id=id)
    if not role:
        return success_response(
            isSuccess=False,
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
async def update(id: str, payload: RoleUpdateBody, db: AsyncSession = Depends(get_db)):
    role = await update_role(db=db, id=id, body=payload)
    return success_response(
        data=RoleResponse.model_validate(role),
        message="Thành công",
        message_en="Role updated successfully",
    )

@router.delete("/{id}", summary="Delete role")
async def delete(id: str, db: AsyncSession = Depends(get_db)):
    role = await delete_role(db=db, id=id)
    return success_response(
        data=RoleResponse.model_validate(role),
        message="Thành công",
        message_en="Role deleted successfully",
    )
