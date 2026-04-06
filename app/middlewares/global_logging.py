import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


logger = logging.getLogger("app.middleware.global_logging")


class GlobalLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        started_at = time.perf_counter()
        client_host = request.client.host if request.client else "-"

        logger.info(
            "Started request %s %s from %s",
            request.method,
            request.url.path,
            client_host,
        )

        response = await call_next(request)
        duration_ms = (time.perf_counter() - started_at) * 1000

        logger.info(
            "Completed request %s %s with status %s in %.2fms",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        return response
