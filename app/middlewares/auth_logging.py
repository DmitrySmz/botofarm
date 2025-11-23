from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.logger import get_logger

logger = get_logger("http")


class AuthLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(
            {
                "event": "request_received",
                "method": request.method,
                "url": str(request.url),
            }
        )
        try:
            response = await call_next(request)
            log_data = {
                "event": "response_sent",
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
            }
            if response.status_code == 401:
                logger.warning(log_data)
            elif response.status_code == 422:
                logger.warning(log_data)
            elif response.status_code >= 500:
                logger.error(log_data)
            else:
                logger.info(log_data)
            return response
        except Exception as e:
            logger.exception(
                {
                    "event": "unhandled_exception",
                    "method": request.method,
                    "url": str(request.url),
                    "error": str(e),
                }
            )
            raise
