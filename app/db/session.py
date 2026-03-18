from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.orm import declarative_base

MYSQL_USER = "root"
MYSQL_PASSWORD = "111111"
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_DATABASE = "fastapi"

SQLALCHEMY_DATABASE_URL = (
    f"mysql+asyncmy://{MYSQL_USER}:{MYSQL_PASSWORD}@"
    f"{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as db:
        yield db


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
