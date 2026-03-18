from fastapi import APIRouter

from app.api.v1.routers.permission import router as permission_router


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(permission_router)

