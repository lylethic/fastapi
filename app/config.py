import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def get_env(name: str, default: str | None = None, *, required: bool = False) -> str | None:
    value = os.getenv(name, default)
    if required and (value is None or value == ""):
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_env_int(name: str, default: int | None = None, *, required: bool = False) -> int | None:
    value = get_env(name, None, required=required)
    if value is None or value == "":
        return default

    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(f"Environment variable {name} must be an integer") from exc


APP_HOST = get_env("APP_HOST", "127.0.0.1")
APP_PORT = get_env_int("APP_PORT", 8000)
UPLOAD_DIR = get_env("UPLOAD_DIR", "uploads")

JWT_SECRET_KEY = get_env("JWT_SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = get_env_int("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
ALGORITHM = get_env("ALGORITHM", "HS256")

MYSQL_USER = get_env("MYSQL_USER", "root")
MYSQL_PASSWORD = get_env("MYSQL_PASSWORD", "111111")
MYSQL_HOST = get_env("MYSQL_HOST", "localhost")
MYSQL_PORT = get_env_int("MYSQL_PORT", 3306)
MYSQL_DATABASE = get_env("MYSQL_DATABASE", "fastapi")
