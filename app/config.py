import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def get_env(
    name: str, default: str | None = None, *, required: bool = False
) -> str | None:
    value = os.getenv(name, default)
    if isinstance(value, str):
        value = value.split("#", 1)[0].strip()
    if required and (value is None or value == ""):
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_env_int(
    name: str, default: int | None = None, *, required: bool = False
) -> int | None:
    value = get_env(name, None, required=required)
    if value is None or value == "":
        return default

    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(f"Environment variable {name} must be an integer") from exc


def get_env_bool(name: str, default: bool = False) -> bool:
    value = get_env(name)
    if value is None or value == "":
        return default

    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False

    raise RuntimeError(f"Environment variable {name} must be a boolean")


APP_HOST = get_env("APP_HOST", "127.0.0.1")
APP_PORT = get_env_int("APP_PORT", 8000)
UPLOAD_DIR = get_env("UPLOAD_DIR", "uploads")

JWT_SECRET_KEY = get_env("JWT_SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = get_env_int("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
ALGORITHM = get_env("ALGORITHM", "HS256")

MYSQL_USER = get_env("MYSQL_USER", "root")
MYSQL_PASSWORD = get_env("MYSQL_PASSWORD", "111111")
MYSQL_HOST = get_env("MYSQL_HOST", "0.0.0.0")
MYSQL_PORT = get_env_int("MYSQL_PORT", 3306)
MYSQL_DATABASE = get_env("MYSQL_DATABASE", "fastapi")
ENVIRONMENT = get_env("ENVIRONMENT", "development")

REDIS_HOST = get_env("REDIS_HOST", "127.0.0.1")
REDIS_PORT = get_env_int("REDIS_PORT", 6379)
REDIS_DB = get_env_int("REDIS_DB", 0)
REDIS_PASSWORD = get_env("REDIS_PASSWORD", "")
REDIS_CACHE_EXPIRATION_SECONDS = get_env_int("REDIS_CACHE_EXPIRATION_SECONDS", 300)
CACHE_ENABLED = get_env_bool("CACHE_ENABLED", True)

SECONDS_TO_SEND_USER_STATUS: int = 60


class Settings:
    REDIS_HOST = REDIS_HOST
    REDIS_PORT = REDIS_PORT
    REDIS_DB = REDIS_DB
    REDIS_PASSWORD = REDIS_PASSWORD
    REDIS_CACHE_EXPIRATION_SECONDS = REDIS_CACHE_EXPIRATION_SECONDS
    CACHE_ENABLED = CACHE_ENABLED
    SECONDS_TO_SEND_USER_STATUS = SECONDS_TO_SEND_USER_STATUS


settings = Settings()
