from datetime import datetime
from typing import Optional

from fastapi import HTTPException

from app.schemas.base_schema import BaseQueryPaginationRequest
from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import UserRoles

from app.schemas.user_role import (
    UserRoleCreateBody,
    UserRoleUpdateBody,
    UserRoleResponse,
    UserRolePagination,
)


async def create(db: AsyncSession, body: UserRoleCreateBody) -> UserRoles:
    smtp = select(UserRoles).where(
        and_(UserRoles.role_id == body.role_id, UserRoles.user_id == body.user_id)
    )
    result = await db.execute(smtp)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="User already has this role")

    user_role = UserRoles(
        user_id=body.user_id, role_id=body.role_id, active=1, deleted=0
    )
    try:
        db.add(user_role)
        await db.commit()
        await db.refresh(user_role)

        return user_role
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


async def get_all(
    db: AsyncSession,
    pagination: BaseQueryPaginationRequest,
    user_id: Optional[str] = None,
    role_id: Optional[str] = None,
) -> UserRolePagination:
    filters = []

    if pagination.active is not None:
        filters = [UserRoles.active == pagination.active]

    if user_id is not None:
        filters.append(UserRoles.user_id == user_id)

    if role_id is not None:
        filters.append(UserRoles.role_id == role_id)

    # Count query
    count_stmt = select(func.count()).select_from(UserRoles)
    if filters:
        count_stmt = count_stmt.where(*filters)

    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()
    total_pages = (
        (total + pagination.page_size - 1) // pagination.page_size if total else 0
    )

    stmt = select(UserRoles)
    if filters:
        stmt = stmt.where(*filters)

    stmt = (
        stmt.order_by(UserRoles.created.desc())
        .offset((pagination.page - 1) * pagination.page_size)
        .limit(pagination.page_size)
    )

    result = await db.execute(stmt)
    user_roles = result.scalars().all()

    return UserRolePagination(
        items=[UserRoleResponse.model_validate(user_role) for user_role in user_roles],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
    )


async def getById(db: AsyncSession, user_id: str, role_id: str) -> UserRoleResponse:
    stmt = select(UserRoles).where(
        and_(UserRoles.user_id == user_id, UserRoles.role_id == role_id)
    )
    result = await db.execute(stmt)
    user_role = result.scalar_one_or_none()

    if not user_role:
        raise HTTPException(status_code=404, detail="User role not found")

    return UserRoleResponse.model_validate(user_role)


async def getRoleByUserId(
    db: AsyncSession, user_id: str, active: Optional[bool] = True
) -> list[UserRoleResponse]:
    filters = [UserRoles.user_id == user_id]

    if active is not None:
        filters.append(UserRoles.active == int(active))

    stmt = select(UserRoles).where(*filters).order_by(UserRoles.created.desc())
    result = await db.execute(stmt)
    user_roles = result.scalars().all()

    return [UserRoleResponse.model_validate(item) for item in user_roles]


async def update(
    db: AsyncSession, user_id: str, role_id: str, body: UserRoleUpdateBody
) -> UserRoles:
    stmt = select(UserRoles).where(
        and_(UserRoles.user_id == user_id, UserRoles.role_id == role_id)
    )
    result = await db.execute(stmt)
    user_role = result.scalar_one_or_none()

    if not user_role:
        raise HTTPException(status_code=404, detail="User role not found")

    # Change role to another role
    if body.role_id is not None and body.role_id != role_id:
        check_stmt = select(UserRoles).where(
            and_(UserRoles.user_id == user_id, UserRoles.role_id == body.role_id)
        )
        check_result = await db.execute(check_stmt)
        duplicate = check_result.scalar_one_or_none()

        if duplicate:
            raise HTTPException(
                status_code=400, detail="User already has this target role"
            )

        user_role.role_id = body.role_id

    if body.active is not None:
        user_role.active = int(body.active)

    user_role.updated = datetime.utcnow()

    try:
        await db.commit()
        await db.refresh(user_role)
        return user_role
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=400, detail=f"Update user role failed: {str(e)}"
        )


async def delete(db: AsyncSession, user_id: str, role_id: str) -> str:
    stmt = select(UserRoles).where(
        and_(UserRoles.user_id == user_id, UserRoles.role_id == role_id)
    )
    result = await db.execute(stmt)
    user_role = result.scalar_one_or_none()

    if not user_role:
        raise HTTPException(status_code=404, detail="User role not found")

    user_role.deleted = 1
    user_role.active = 0
    user_role.updated = datetime.utcnow()

    try:
        await db.commit()
        await db.refresh(user_role)
        return "Soft delete success"
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=400, detail=f"Soft delete user role failed: {str(e)}"
        )
