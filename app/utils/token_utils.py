import hashlib
import hmac
import secrets

from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, JWT_SECRET_KEY

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
PBKDF2_ITERATIONS = 600000


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


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


def password_needs_rehash(hashed_password: str) -> bool:
    return hashed_password.startswith("pbkdf2_sha256$")


def create_access_token(
    data: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES
) -> str:
    now = datetime.now(timezone.utc)
    to_encode = data.copy()
    expire = now + timedelta(minutes=expires_minutes)
    to_encode.update({"iat": now, "exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
