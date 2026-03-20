import logging
import os

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, HTMLResponse


from fastapi.staticfiles import StaticFiles
from typing import List

from app.api.v1.router import api_router
from app.config import APP_HOST, APP_PORT, UPLOAD_DIR
from app.db.session import engine, init_models
from app.middlewares.auth import AuthMiddleware
from app.middlewares.global_logging import GlobalLoggingMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("app.main")
sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
sqlalchemy_logger.setLevel(logging.INFO)
os.makedirs(UPLOAD_DIR, exist_ok=True)

connected_clients: List[WebSocket] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    await init_models()
    logger.info("API is running at http://%s:%s", APP_HOST, APP_PORT)
    logger.info("Swagger docs: http://%s:%s/docs", APP_HOST, APP_PORT)
    yield

    # SHUTDOWN
    await engine.dispose()


# Start program
app = FastAPI(
    title="Auth API",
    version="1.0.0",
    description="Auth API",
    lifespan=lifespan,
    swagger_ui_parameters={
        "syntaxHighlight": {"theme": "obsidian"},
        # "docExpansion": "none"
    },
)

# Middlewares
app.add_middleware(AuthMiddleware)
app.add_middleware(GlobalLoggingMiddleware)

# Export StaticFile
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

## Defines all routers
app.include_router(api_router)


# Nomarlize handling global exception (response json)
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(
        "HTTP error on %s %s: %s", request.method, request.url.path, exc.detail
    )
    return JSONResponse(
        status_code=200,
        content={
            "isSuccess": False,
            "statusCode": exc.status_code,
            "data": None,
            "message": str(exc.detail),
            "messageEn": str(exc.detail),
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=200,
        content={
            "isSuccess": False,
            "statusCode": 500,
            "data": None,
            "message": "Loi he thong",
            "messageEn": "Internal server error",
        },
    )


#


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Broadcast the message to all connected clients
            for client in connected_clients:
                await client.send_text(data)
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        print("Client disconnected")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=APP_HOST, port=APP_PORT, reload=True)
