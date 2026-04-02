from fastapi import APIRouter, Depends

from app.api.v1.routers.permission import router as permission_router
from app.api.v1.routers.role_permission import router as role_permission_router
from app.api.v1.routers.role import router as role_router
from app.api.v1.routers.user import router as user_router
from app.api.v1.routers.user_role import router as user_role_router
from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.chat import router as chat_router
from app.api.v1.routers.message import router as message_router
from app.websocket.router import websocket_router

from app.services.assistant_service import authorize


api_router = APIRouter(prefix="/api/v1")
protected_route_dependencies = [Depends(authorize)]

api_router.include_router(auth_router)
api_router.include_router(permission_router, dependencies=protected_route_dependencies)
api_router.include_router(role_router, dependencies=protected_route_dependencies)
api_router.include_router(
    role_permission_router, dependencies=protected_route_dependencies
)
api_router.include_router(user_router, dependencies=protected_route_dependencies)
api_router.include_router(user_role_router, dependencies=protected_route_dependencies)
api_router.include_router(chat_router, dependencies=protected_route_dependencies)
api_router.include_router(message_router, dependencies=protected_route_dependencies)
api_router.include_router(websocket_router)
