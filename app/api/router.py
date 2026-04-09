from fastapi import APIRouter, Depends

from app.api.v1.permission import router as permission_router
from app.api.v1.role_permission import router as role_permission_router
from app.api.v1.role import router as role_router
from app.api.v1.user import router as user_router
from app.api.v1.user_role import router as user_role_router
from app.api.v1.auth import router as auth_router
from app.api.v1.chat import router as chat_router
from app.api.v1.message import router as message_router
from app.api.v1.merchant_profile import router as merchant_profile_router
from app.api.v1.affiliate_profile import router as affiliate_profile_router
from app.api.v1.affiliate_campaign import router as affiliate_campaign_router

# Websocket router
from app.services.websocket.router import websocket_router

from app.services.assistant_service import authorize

api_router = APIRouter(prefix="/api/v1")
protected_route_dependencies = [Depends(authorize)]

# Affiliate
api_router.include_router(
    merchant_profile_router, dependencies=protected_route_dependencies
)

api_router.include_router(
    affiliate_profile_router, dependencies=protected_route_dependencies
)

api_router.include_router(
    affiliate_campaign_router, dependencies=protected_route_dependencies
)

# Auth
api_router.include_router(auth_router)

# Permission
api_router.include_router(permission_router, dependencies=protected_route_dependencies)
api_router.include_router(role_router, dependencies=protected_route_dependencies)
api_router.include_router(
    role_permission_router, dependencies=protected_route_dependencies
)
api_router.include_router(user_role_router, dependencies=protected_route_dependencies)

# User
api_router.include_router(user_router, dependencies=protected_route_dependencies)

# Chat
api_router.include_router(chat_router, dependencies=protected_route_dependencies)
api_router.include_router(message_router, dependencies=protected_route_dependencies)


# Websocker Router
api_router.include_router(websocket_router)
