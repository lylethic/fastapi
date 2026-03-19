import hashlib
import hmac
import os
import secrets
from uuid import uuid4
import uuid

from fastapi import File, HTTPException, UploadFile

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from passlib.context import CryptContext

from app.db.models import Users

from app.schemas.user import (
    UserCreateBody,
    UserUpdateBody,
    UserResponse,
    UserPagination
)


# Define upload image
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
PBKDF2_ITERATIONS = 600000

def hash_password(password: str) -> str:
    try:
        salt = secrets.token_hex(16)
        hashed = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            PBKDF2_ITERATIONS,
        ).hex()
        return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt}${hashed}"
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Password hashing failed") from exc


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if hashed_password.startswith("pbkdf2_sha256$"):
        _, iterations, salt, stored_hash = hashed_password.split("$", 3)
        computed_hash = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt.encode("utf-8"),
            int(iterations),
        ).hex()
        return hmac.compare_digest(computed_hash, stored_hash)

    return pwd_context.verify(plain_password, hashed_password)


# create
async def create_user(db: AsyncSession, body: UserCreateBody) -> Users:
    email_result = await db.execute(
        select(Users).where(Users.email == body.email)
    )
    existing_email = email_result.scalar_one_or_none()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    username_result = await db.execute(
        select(Users).where(Users.username == body.username)
    )
    existing_username = username_result.scalar_one_or_none()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = Users(
        id=str(uuid4()),
        username=body.username,
        email=body.email,
        password=hash_password(body.password),
        name=body.name,
        profile_pic=body.profile_pic,
        city=body.city,
    )

    db.add(user)

    try:
        await db.commit()
        await db.refresh(user)
        return user
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
      
async def get_user(db: AsyncSession, page: int = 1, page_size= 10, search: str | None = None, active: bool | None = True) -> UserPagination:
    filters = []

    if search:
        filters.append(
            or_(
                Users.id == search,
                Users.username.ilike(f"%{search}%"),
                Users.email.ilike(f"%{search}%"),
                Users.name.ilike(f"%{search}%"),
            )
        )
    
    if active is not None:
        filters.append(Users.active == active)

    # Count query
    count_stmt = select(func.count()).select_from(Users)
    if filters:
        count_stmt = count_stmt.where(*filters)

    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    total_pages = (total + page_size - 1) // page_size if total else 0

    # Data query
    stmt = select(Users)
    if filters:
        stmt = stmt.where(*filters)
    
    stmt = (
        stmt.order_by(Users.created.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(stmt)
    users = result.scalars().all()

    return UserPagination(
        items=[UserResponse.model_validate(user) for user in users],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

async def get_user_by_id(db:AsyncSession, id:str) -> Users:
    result = await db.execute(select(Users).where(Users.id == id))
    return result.scalar_one_or_none()

async def update_user(db: AsyncSession, id: str, body: UserUpdateBody) -> Users:
    result = await db.execute(select(Users).where(Users.id == id))
    update = result.scalar_one_or_none()
    if not update:
        raise HTTPException(status_code=404, detail="User not found")
    
    if body.username is not None:
        update.username = body.username
    if body.email is not None:
        update.email = body.email
    if body.password is not None:
        update.password = hash_password(body.password)
    if body.name is not None:
        update.name = body.name
    if body.profile_pic is not None:
        update.profile_pic = body.profile_pic
    if body.city is not None:
        update.city = body.city
    if body.active is not None:
        update.active = body.active

    try:
        await db.commit()
        await db.refresh(update)
        return update
    except:
        await db.rollback()
        raise HTTPException(status_code=400, detail="User already exists")

async def delete_user(db: AsyncSession, id: str) -> Users:
    result = await db.execute(select(Users).where(Users.id == id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()
    return user

       
async def uploadImage(db: AsyncSession, id: str, file: UploadFile = File(...)):
    user = await get_user_by_id(db, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    ext = os.path.splitext(file.filename)[1]
    if ext not in ALLOWED_EXTS:
        raise HTTPException(status_code=400, detail="Invalid file extension")
    
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds the limit")
    
    unique_name = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(UPLOAD_DIR, unique_name)

    # Save file
    with open(save_path, "wb") as f:
        f.write(contents)

    user.profile_pic = unique_name
    await db.commit()
    await db.refresh(user)

    return user

