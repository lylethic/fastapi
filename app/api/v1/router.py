from fastapi import APIRouter

from app.api.v1.routers.permission import router as permission_router
from app.api.v1.routers.role_permission import router as role_permission_router
from app.api.v1.routers.role import router as role_router
from app.api.v1.routers.user import router as user_router


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(permission_router)
api_router.include_router(role_permission_router)
api_router.include_router(role_router)
api_router.include_router(user_router)
