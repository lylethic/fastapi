from uuid import uuid4
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import func, or_, select, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

## Model Permission
from app.db.models import Permissions
from app.schemas.base_schema import BaseQueryPaginationRequest
from app.schemas.permission import (
    PermissionPagination,
    PermissionResponse,
    PermissionCreateBody,
    PermissionUpdateBody,
)


## Create
async def create_permission(
    db: AsyncSession, body: PermissionCreateBody, current_user: str | None = None
) -> Permissions:
    result = await db.execute(select(Permissions).where(Permissions.name == body.name))
    checkPermissionExist = result.scalar_one_or_none()
    if checkPermissionExist:
        raise HTTPException(status_code=400, detail="Permission already exists")

    permission = Permissions(
        id=str(uuid4()),
        name=body.name,
        description=body.description,
    )
    if current_user is not None:
        permission.created_by = current_user
    permission.created = datetime.utcnow()

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
    db: AsyncSession, pagination: BaseQueryPaginationRequest
) -> PermissionPagination:
    filters = [Permissions.deleted == False]

    if pagination.search:
        filters.append(
            or_(
                Permissions.id == pagination.search,
                Permissions.name.ilike(f"%{pagination.search}%"),
            )
        )
    if pagination.active is not None:
        filters.append(Permissions.active == pagination.active)

    # Count query
    count_stmt = select(func.count()).select_from(Permissions)
    if filters:
        count_stmt = count_stmt.where(*filters)

    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    total_pages = (
        (total + pagination.page_size - 1) // pagination.page_size if total else 0
    )

    # Data query
    stmt = select(Permissions)
    if filters:
        stmt = stmt.where(*filters)

    stmt = (
        stmt.order_by(Permissions.created.desc())
        .offset((pagination.page - 1) * pagination.page_size)
        .limit(pagination.page_size)
    )

    result = await db.execute(stmt)
    permissions = result.scalars().all()

    return PermissionPagination(
        items=[
            PermissionResponse.model_validate(permission) for permission in permissions
        ],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
    )


## Get by id
async def get_permission_by_id(db: AsyncSession, id: str) -> Permissions:
    result = await db.execute(
        select(Permissions).where(
            and_(Permissions.id == id, Permissions.deleted == False)
        )
    )
    return result.scalar_one_or_none()


## Update
async def update_permission(
    db: AsyncSession,
    id: str,
    body: PermissionUpdateBody,
    current_user: str | None = None,
) -> Permissions:
    result = await db.execute(
        select(Permissions).where(
            and_(Permissions.id == id, Permissions.deleted == False)
        )
    )
    permission = result.scalar_one_or_none()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    if body.name is not None:
        permission.name = body.name
    if body.description is not None:
        permission.description = body.description
    if body.active is not None:
        permission.active = body.active

    if current_user is not None:
        permission.updated_by = current_user
    permission.updated = datetime.utcnow()

    try:
        await db.commit()
        await db.refresh(permission)
        return permission
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Permission already exists")


## Delete
async def delete_permission(db: AsyncSession, id: str) -> Permissions:
    result = await db.execute(
        select(Permissions).where(
            and_(Permissions.id == id, Permissions.deleted == False)
        )
    )
    permission = result.scalar_one_or_none()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    permission.active = False
    permission.deleted = True
    await db.commit()
    await db.refresh(permission)
    return permission
