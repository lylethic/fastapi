import logging
import os

from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.config import APP_HOST, APP_PORT, UPLOAD_DIR
from app.core.swagger import CustomSwaggerUI
from app.core.tags_metadata import tags_metadata
from app.db.session import close_redis, engine, get_redis_client, init_models
from app.middlewares.auth import AuthMiddleware
from app.middlewares.global_logging import GlobalLoggingMiddleware

logger = logging.getLogger("app.main")
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
connected_clients: List[WebSocket] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = None

    try:
        await init_models()
    except Exception as exc:
        logger.warning("Database startup check failed: %s", exc)

    try:
        app.state.redis = get_redis_client()
        await app.state.redis.ping()
    except Exception as exc:
        logger.warning("Redis startup check failed: %s", exc)
        app.state.redis = None

    logger.info("API is running at http://%s:%s", APP_HOST, APP_PORT)
    logger.info("Swagger docs: http://%s:%s/swagger/index.html", APP_HOST, APP_PORT)
    yield

    if app.state.redis is not None:
        await app.state.redis.close()
        await close_redis()
    await engine.dispose()


def build_openapi_schema(app: FastAPI):
    if app.openapi_schema is not None:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
        servers=app.servers,
    )
    openapi_schema["openapi"] = "3.0.3"
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.warning(
            "HTTP error on %s %s: %s", request.method, request.url.path, exc.detail
        )
        return JSONResponse(
            status_code=200,
            content={
                "is_success": False,
                "status_code": exc.status_code,
                "data": None,
                "message": str(exc.detail),
                "message_en": str(exc.detail),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=200,
            content={
                "is_success": False,
                "status_code": 500,
                "data": None,
                "message": "Loi he thong",
                "message_en": "Internal server error",
            },
        )


def register_static_files(app: FastAPI) -> None:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def register_routes(app: FastAPI) -> None:
    app.include_router(api_router)

    @app.get("/chat-test", response_class=HTMLResponse, include_in_schema=False)
    async def chat_test_page():
        with open(
            os.path.join(STATIC_DIR, "chat-test.html"), "r", encoding="utf-8"
        ) as file:
            return HTMLResponse(file.read())

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        connected_clients.append(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                for client in connected_clients:
                    await client.send_text(data)
        except WebSocketDisconnect:
            connected_clients.remove(websocket)
            print("Client disconnected")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Affiliate Service APIs",
        openapi_tags=tags_metadata,
        openapi_url="/openapi.json",
        version="1.0.0",
        description="Backend for Affiliate Service API",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        swagger_ui_parameters={
            "syntaxHighlight": {"theme": "obsidian"},
        },
        servers=[
            {"url": "http://127.0.0.1:8000", "description": "HTTP local"},
            {"url": "https://127.0.0.1:8000", "description": "HTTPS local"},
        ],
    )

    app.openapi = lambda: build_openapi_schema(app)
    app.add_middleware(AuthMiddleware)
    app.add_middleware(GlobalLoggingMiddleware)

    register_static_files(app)
    CustomSwaggerUI(app, title="Affiliate Service API").setup()
    register_exception_handlers(app)
    register_routes(app)
    return app
