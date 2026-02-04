from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from app.core.config import RATE_LIMIT_ENABLED
from app.core.logging import request_logger

limiter = Limiter(key_func=get_remote_address)

async def rate_limit_error_handler(request: Request, exc: RateLimitExceeded) -> dict:
    """Handle rate limit exceeded errors"""
    request_logger.warning(
        "rate_limit_exceeded",
        extra={
            "client_ip": get_remote_address(request),
            "endpoint": request.url.path,
            "limit": exc.detail
        }
    )
    return {
        "error": "Rate limit exceeded",
        "detail": exc.detail
    }

def get_limiter():
    """Get rate limiter instance (disabled in testing)"""
    return limiter if RATE_LIMIT_ENABLED else None
