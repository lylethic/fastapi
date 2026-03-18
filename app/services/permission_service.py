from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

## Model Permission
from app.db.models import Permissions

from app.schemas.permission import (
    PermissionPagination, 
    PermissionResponse, 
    PermissionCreateBody,
    PermissionUpdateBody
)

## Create
async def create_permission(db: AsyncSession, body: PermissionCreateBody) -> Permissions:
    result = await db.execute(select(Permissions).where(Permissions.name == body.name))
    checkPermissionExist = result.scalar_one_or_none()
    if checkPermissionExist:
        raise HTTPException(status_code=400, detail="Permission already exists")

    permission = Permissions(
        id=str(uuid4()),
        name=body.name,
        description=body.description,
    )
    db.add(permission)

    try:
        await db.commit()
        await db.refresh(permission)
        return permission
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Permission already exists")


## Get all
async def get_permission(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    search: str | None = None,
    active: bool | None = 1
) -> PermissionPagination:
    filters = []

    if search:
        filters.append(
            or_(
                Permissions.id == search,
                Permissions.name.ilike(f"%{search}%")
            )
        )
    if active is not None:
            filters.append(Permissions.active == active)

    # Count query
    count_stmt = select(func.count()).select_from(Permissions)
    if filters:
        count_stmt = count_stmt.where(*filters)

    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    total_pages = (total + page_size - 1) // page_size if total else 0

    # Data query
    stmt = select(Permissions)
    if filters:
        stmt = stmt.where(*filters)

    stmt = (
        stmt.order_by(Permissions.created.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(stmt)
    permissions = result.scalars().all()

    return PermissionPagination(
        items=[PermissionResponse.model_validate(permission) for permission in permissions],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


## Get by id
async def get_permission_by_id(db: AsyncSession, id: str) -> Permissions:
    result = await db.execute(select(Permissions).where(Permissions.id == id))
    return result.scalar_one_or_none()

## Update
async def update_permission(db: AsyncSession, id: str, body: PermissionUpdateBody) -> Permissions:
    result = await db.execute(select(Permissions).where(Permissions.id == id))
    permission = result.scalar_one_or_none()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    if body.name is not None:
        permission.name = body.name
    if body.description is not None:
        permission.description = body.description
    if body.active is not None:
        permission.active = body.active

    await db.commit()
    await db.refresh(permission)
    return permission

## Delete
async def delete_permission(db: AsyncSession, id: str) -> Permissions:
    result = await db.execute(select(Permissions).where(Permissions.id == id))
    permission = result.scalar_one_or_none()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    await db.delete(permission)
    await db.commit()
    return permission
