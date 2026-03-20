from collections.abc import Callable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.user_service import get_role_permission

security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user from middleware state and load current permissions from DB.
    """
    auth_error = getattr(request.state, "auth_error", None)
    user = getattr(request.state, "user", None)

    if auth_error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=auth_error,
        )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    user_id = user["id"]
    role_permission = await get_role_permission(db=db, user_id=user_id)
    permissions = {
        permission.strip().upper()
        for permission in role_permission.get("permissions", [])
        if isinstance(permission, str) and permission.strip()
    }

    return {
        "id": user_id,
        "email": user.get("email"),
        "name": user.get("name"),
        "roles": role_permission.get("roles", []),
        "permissions": permissions,
    }


async def authorize(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
):
    """
    Authorize user
    """
    auth_error = getattr(request.state, "auth_error", None)
    user = getattr(request.state, "user", None)

    if auth_error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=auth_error,
        )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )


def require_permissions(*required_permissions: str) -> Callable:
    normalized_permissions = {
        permission.strip().upper()
        for permission in required_permissions
        if permission and permission.strip()
    }

    async def permission_checker(
        current_user: dict = Depends(get_current_user),
    ):
        missing_permissions = sorted(
            permission
            for permission in normalized_permissions
            if permission not in current_user["permissions"]
        )
        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You do not have permission to this action. Missing permissions: {', '.join(missing_permissions)}",
            )
        return current_user

    return permission_checker
