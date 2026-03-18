from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.v1.router import api_router
from app.db.session import engine, init_models


@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    await init_models()
    yield

    # SHUTDOWN
    await engine.dispose()

app = FastAPI(
    lifespan=lifespan,
    swagger_ui_parameters={
        "syntaxHighlight": {"theme": "obsidian"},
        # "docExpansion": "none"
    }
)

## Defines all routers
app.include_router(api_router)
