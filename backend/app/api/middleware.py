from __future__ import annotations
import logging
import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

logger = logging.getLogger("chethas.api.middleware")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log request details including method, path, status code, and duration.
    Attaches a unique UUID to each request.
    """
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        start_time = time.perf_counter()
        
        try:
            response = await call_next(request)
            process_time_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                f"request_id={request_id} method={request.method} path={request.url.path} "
                f"status_code={response.status_code} duration_ms={process_time_ms:.2f}"
            )
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as e:
            process_time_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"request_id={request_id} method={request.method} path={request.url.path} "
                f"error={str(e)} duration_ms={process_time_ms:.2f}"
            )
            raise
