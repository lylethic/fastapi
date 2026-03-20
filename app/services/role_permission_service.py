from fastapi import HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import RolePermissions
from app.schemas.base_schema import BaseQueryPaginationRequest
from app.schemas.rolepermission import (
    RolePermissionCreateBody,
    RolePermissionPagination,
    RolePermissionResponse,
    RolePermissionUpdateBody,
)


async def create_role_permission(
    db: AsyncSession, body: RolePermissionCreateBody
) -> RolePermissions:
    result = await db.execute(
        select(RolePermissions).where(
            RolePermissions.role_id == body.role_id,
            RolePermissions.permission_id == body.permission_id,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Role permission already exists")

    role_permission = RolePermissions(
        role_id=body.role_id,
        permission_id=body.permission_id,
    )
    db.add(role_permission)

    try:
        await db.commit()
        await db.refresh(role_permission)
        return role_permission
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Role permission already exists")


async def get_role_permissions(
    db: AsyncSession, pagination: BaseQueryPaginationRequest
) -> RolePermissionPagination:
    filters = []

    if pagination.search:
        filters.append(
            or_(
                RolePermissions.role_id == pagination.search,
                RolePermissions.permission_id == pagination.search,
            )
        )

    if pagination.active is not None:
        filters.append(RolePermissions.active == pagination.active)

    count_stmt = select(func.count()).select_from(RolePermissions)
    if filters:
        count_stmt = count_stmt.where(*filters)

    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()
    total_pages = (
        (total + pagination.page_size - 1) // pagination.page_size if total else 0
    )

    stmt = select(RolePermissions)
    if filters:
        stmt = stmt.where(*filters)

    stmt = (
        stmt.order_by(RolePermissions.created.desc())
        .offset((pagination.page - 1) * pagination.page_size)
        .limit(pagination.page_size)
    )

    result = await db.execute(stmt)
    items = result.scalars().all()

    return RolePermissionPagination(
        items=[RolePermissionResponse.model_validate(item) for item in items],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
    )


async def get_role_permission_by_id(
    db: AsyncSession, role_id: str, permission_id: str
) -> RolePermissions | None:
    result = await db.execute(
        select(RolePermissions).where(
            RolePermissions.role_id == role_id,
            RolePermissions.permission_id == permission_id,
        )
    )
    return result.scalar_one_or_none()


async def update_role_permission(
    db: AsyncSession,
    role_id: str,
    permission_id: str,
    body: RolePermissionUpdateBody,
) -> RolePermissions:
    role_permission = await get_role_permission_by_id(db, role_id, permission_id)
    if not role_permission:
        raise HTTPException(status_code=404, detail="Role permission not found")

    next_role_id = body.role_id if body.role_id is not None else role_permission.role_id
    next_permission_id = (
        body.permission_id
        if body.permission_id is not None
        else role_permission.permission_id
    )

    if (
        next_role_id != role_permission.role_id
        or next_permission_id != role_permission.permission_id
    ):
        duplicate_result = await db.execute(
            select(RolePermissions).where(
                RolePermissions.role_id == next_role_id,
                RolePermissions.permission_id == next_permission_id,
            )
        )
        duplicate = duplicate_result.scalar_one_or_none()
        if duplicate:
            raise HTTPException(
                status_code=400, detail="Role permission already exists"
            )

    role_permission.role_id = next_role_id
    role_permission.permission_id = next_permission_id
    if body.active is not None:
        role_permission.active = body.active

    try:
        await db.commit()
        await db.refresh(role_permission)
        return role_permission
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Role permission already exists")


async def delete_role_permission(
    db: AsyncSession, role_id: str, permission_id: str
) -> RolePermissions:
    role_permission = await get_role_permission_by_id(db, role_id, permission_id)
    if not role_permission:
        raise HTTPException(status_code=404, detail="Role permission not found")

    await db.delete(role_permission)
    await db.commit()
    return role_permission
