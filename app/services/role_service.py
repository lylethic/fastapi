from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import func, or_, select, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

## Model
from app.db.models import Roles

from app.schemas.role import (
    RolePagination, 
    RoleResponse, 
    RoleCreateBody,
    RoleUpdateBody
)

## Create
async def create_role(db: AsyncSession, body: RoleCreateBody) -> Roles:
    result = await db.execute(select(Roles).where(Roles.name == body.name))
    checkRoleExist = result.scalar_one_or_none()
    if checkRoleExist:
        raise HTTPException(status_code=400, detail="Role already exists")

    role = Roles(
        id=str(uuid4()),
        name=body.name.upper(),
        description=body.description,
    )
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
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    search: str | None = None,
    active: bool | None = True,
) -> RolePagination:
    filters = [Roles.deleted == False]

    if search:
        filters.append(
            or_(
                Roles.id == search,
                Roles.name.ilike(f"%{search}%"),
            )
        )

    if active is not None:
        filters.append(Roles.active == active)

    # Count query
    count_stmt = select(func.count()).select_from(Roles)
    if filters:
        count_stmt = count_stmt.where(*filters)

    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    total_pages = (total + page_size - 1) // page_size if total else 0

    # Data query
    stmt = select(Roles)
    if filters:
        stmt = stmt.where(*filters)

    stmt = (
        stmt.order_by(Roles.created.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(stmt)
    roles = result.scalars().all()

    return RolePagination(
        items=[RoleResponse.model_validate(role) for role in roles],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )

## Get by id
async def get_role_by_id(db: AsyncSession, id: str) -> Roles:
    result = await db.execute(select(Roles).where(and_(Roles.id == id, Roles.deleted == False)))
    return result.scalar_one_or_none()

## Update
async def update_role(db: AsyncSession, id: str, body: RoleUpdateBody) -> Roles:
    result = await db.execute(select(Roles).where(Roles.id == id, Roles.deleted == False))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    if body.name is not None:
        role.name = body.name.upper()
    if body.description is not None:
        role.description = body.description
    if body.active is not None:
        role.active = body.active

    try:
        await db.commit()
        await db.refresh(role)
        return role
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Role already exists")

## Soft Delete
async def delete_role(db: AsyncSession, id: str) -> Roles:
    result = await db.execute(select(Roles).where(Roles.id == id, Roles.deleted == False))
    data = result.scalar_one_or_none()

    if not data:
        raise HTTPException(status_code=404, detail="Role not found")
    data.active = False
    data.deleted = True
    await db.commit()
    await db.refresh(data)
    return data

