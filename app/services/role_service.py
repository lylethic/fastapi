from uuid import uuid4
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import func, or_, select, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

## Model
from app.db.models import Roles
from app.schemas.base_schema import BaseQueryPaginationRequest
from app.schemas.role import (
    RolePagination,
    RoleResponse,
    RoleCreateBody,
    RoleUpdateBody,
)


## Create
async def create_role(
    db: AsyncSession, body: RoleCreateBody, current_user: str | None = None
) -> Roles:
    result = await db.execute(select(Roles).where(Roles.name == body.name))
    checkRoleExist = result.scalar_one_or_none()
    if checkRoleExist:
        raise HTTPException(status_code=400, detail="Role already exists")

    role = Roles(
        id=str(uuid4()),
        name=body.name.upper(),
        description=body.description,
    )
    role.created = datetime.utcnow()
    if current_user is not None:
        role.created_by = current_user
    db.add(role)

    try:
        await db.commit()
        await db.refresh(role)
        return role
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Role already exists")


## Get all
async def get_role(
    db: AsyncSession, pagination: BaseQueryPaginationRequest
) -> RolePagination:
    filters = [Roles.deleted == False]

    if pagination.search:
        filters.append(
            or_(
                Roles.name.ilike(f"%{pagination.search}%"),
            )
        )

    if pagination.active is not None:
        filters.append(Roles.active == pagination.active)

    # Count query
    count_stmt = select(func.count()).select_from(Roles)
    if filters:
        count_stmt = count_stmt.where(*filters)

    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    total_pages = (
        (total + pagination.page_size - 1) // pagination.page_size if total else 0
    )

    # Data query
    stmt = select(Roles)
    if filters:
        stmt = stmt.where(*filters)

    stmt = (
        stmt.order_by(Roles.created.desc())
        .offset((pagination.page - 1) * pagination.page_size)
        .limit(pagination.page_size)
    )

    result = await db.execute(stmt)
    roles = result.scalars().all()

    return RolePagination(
        items=[RoleResponse.model_validate(role) for role in roles],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
    )


## Get by id
async def get_role_by_id(db: AsyncSession, id: str) -> Roles:
    result = await db.execute(
        select(Roles).where(and_(Roles.id == id, Roles.deleted == False))
    )
    return result.scalar_one_or_none()


async def get_role_by_name(db: AsyncSession, name: str) -> Roles:
    """
    Retrieve a role by its name.

    Args:
        db: Async database session.
        name: Role name to search for.

    Returns:
        The matching role if found and not deleted, otherwise None.
    """
    result = await db.execute(
        select(Roles).where(and_(Roles.name == name, Roles.deleted == False))
    )
    return result.scalar_one_or_none()


## Update
async def update_role(
    db: AsyncSession, id: str, body: RoleUpdateBody, current_user: str | None = None
) -> Roles:
    result = await db.execute(
        select(Roles).where(Roles.id == id, Roles.deleted == False)
    )
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    if body.name is not None:
        role.name = body.name.upper()
    if body.description is not None:
        role.description = body.description
    if body.active is not None:
        role.active = body.active

    if current_user is not None:
        role.updated_by = current_user
    role.updated = datetime.utcnow()

    try:
        await db.commit()
        await db.refresh(role)
        return role
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Role already exists")


## Soft Delete
async def delete_role(db: AsyncSession, id: str) -> Roles:
    result = await db.execute(
        select(Roles).where(Roles.id == id, Roles.deleted == False)
    )
    data = result.scalar_one_or_none()

    if not data:
        raise HTTPException(status_code=404, detail="Role not found")
    data.active = False
    data.deleted = True
    await db.commit()
    await db.refresh(data)
    return data
