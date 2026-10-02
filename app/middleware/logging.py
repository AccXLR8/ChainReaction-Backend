import logging
from time import perf_counter
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = perf_counter()
        response: Response = await call_next(request)
        duration_ms = (perf_counter() - start) * 1000
        logger.info(
            "request completed",
            extra={
                "path": request.url.path,
                "method": request.method,
                "status": response.status_code,
                "duration_ms": round(duration_ms, 2),
                "request_id": getattr(request.state, "request_id", None),
            },
        )
        return response
