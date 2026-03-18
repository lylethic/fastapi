from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

## Model Permission
from app.db.models import Permissions

from app.schemas.permission import PermissionPagination, PermissionResponse

def create_permission(db: Session, name: str, description: str | None = None) -> Permissions:
    permission = Permissions(
        id=str(uuid4()),
        name=name,
        description=description,
    )
    db.add(permission)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Permission already exists")

    db.refresh(permission)
    return permission

## Get all
def get_permission(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    search: str | None = None,
) -> PermissionPagination:
    query = db.query(Permissions)

    if search:
        query = query.filter(
            or_(
                Permissions.id == search,
                Permissions.name.ilike(f"%{search}%"),
            )
        )

    total = query.count()
    total_pages = (total + page_size - 1) // page_size if total else 0
    permissions = (
        query.order_by(Permissions.created.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PermissionPagination(
        items=[PermissionResponse.model_validate(permission) for permission in permissions],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )

## Get by id
def get_permission_by_id(db: Session, id: str) -> Permissions:
    result = db.query(Permissions).filter(Permissions.id == id).first() 
    return result

## Update
def update_permission(db: Session, id: str, name: str, description: str | None = None) -> Permissions:
    permission = db.query(Permissions).filter(Permissions.id == id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    permission.name = name
    permission.description = description

    db.commit()
    db.refresh(permission)
    return permission

## Delete
def delete_permission(db: Session, id: str) -> Permissions:
    permission = db.query(Permissions).filter(Permissions.id == id).first()
    if not permission:  
        raise HTTPException(status_code=404, detail="Permission not found")

    db.delete(permission)
    db.commit()
    return permission

