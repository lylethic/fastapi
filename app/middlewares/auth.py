from fastapi import Request
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import ALGORITHM, JWT_SECRET_KEY


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.user = None
        request.state.auth_error = None

        authorization = request.headers.get("Authorization")
        if authorization:
            scheme, _, token = authorization.partition(" ")
            if scheme.lower() != "bearer" or not token:
                request.state.auth_error = "Invalid authorization header"
            else:
                try:
                    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
                    user_id = payload.get("id")
                    if not user_id:
                        request.state.auth_error = "Invalid token payload"
                    else:
                        request.state.user = {
                            "id": user_id,
                            "email": payload.get("email"),
                            "name": payload.get("name"),
                        }
                except JWTError:
                    request.state.auth_error = "Invalid token or token expired"

        return await call_next(request)
