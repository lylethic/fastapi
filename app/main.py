from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.v1 import api_router
from app.db import models
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    models.Base.metadata.create_all(bind=engine)
    yield
    
    # SHUTDOWN 
    engine.dispose()

app = FastAPI(
    lifespan=lifespan,
    swagger_ui_parameters={
        "syntaxHighlight": {"theme": "obsidian"},
        # "docExpansion": "none"
    }
)

## Defines all routers
app.include_router(api_router)
