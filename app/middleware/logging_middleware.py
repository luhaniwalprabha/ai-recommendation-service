import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from app.core.logging import get_logger

logger = get_logger("request")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()

        logger.info(f"START request_id={request_id} path={request.url.path}")

        try:
            response = await call_next(request)
        except Exception as e:
            logger.exception(f"ERROR request_id={request_id} error={str(e)}")
            raise

        duration = round((time.time() - start_time) * 1000, 2)

        logger.info(
            f"END request_id={request_id} status={response.status_code} duration_ms={duration}"
        )

        response.headers["X-Request-ID"] = request_id
        return response