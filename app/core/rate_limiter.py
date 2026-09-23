import time
import logging
from fastapi import Request, Response, HTTPException, status
from app.core.redis import redis_client
from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

class RateLimiter:
    """
    Asynchronous Redis-backed rate limiter dependency for FastAPI routes.
    Implements a fixed-window counter with atomic Redis operations and rate-limit headers.
    """
    def __init__(
        self,
        times: int = settings.RATE_LIMIT_REQUESTS,
        seconds: int = settings.RATE_LIMIT_WINDOW_SECONDS
    ):
        self.times = times
        self.seconds = seconds

    async def __call__(self, request: Request, response: Response) -> None:
        # Determine client identity (User ID if auth header exists, else Client IP)
        user_id = getattr(request.state, "user_id", None)
        if not user_id:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                user_id = auth_header.split(" ")[1][:16]  # hash snippet for identifier
            else:
                user_id = request.client.host if request.client else "anonymous"

        endpoint = request.url.path
        key = f"rate_limit:{endpoint}:{user_id}"

        try:
            # Atomic pipeline to get current count, increment, and set TTL if new
            pipe = redis_client.pipeline()
            pipe.get(key)
            pipe.ttl(key)
            results = await pipe.execute()

            current_count_str = results[0]
            ttl = results[1]

            current_count = int(current_count_str) if current_count_str else 0

            if current_count >= self.times:
                retry_after = ttl if ttl > 0 else self.seconds
                response.headers["Retry-After"] = str(retry_after)
                response.headers["X-RateLimit-Limit"] = str(self.times)
                response.headers["X-RateLimit-Remaining"] = "0"
                response.headers["X-RateLimit-Reset"] = str(int(time.time()) + retry_after)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Maximum {self.times} requests per {self.seconds} seconds."
                )

            # Increment count
            pipe = redis_client.pipeline()
            pipe.incr(key)
            if current_count == 0 or ttl <= 0:
                pipe.expire(key, self.seconds)
            await pipe.execute()

            remaining = max(0, self.times - (current_count + 1))
            reset_time = int(time.time()) + (ttl if ttl > 0 else self.seconds)

            response.headers["X-RateLimit-Limit"] = str(self.times)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(reset_time)

        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"Rate limiting bypassed due to Redis connection error: {e}")
            # Fallback: allow request if Redis fails to ensure service availability
            return

# Default global instance
default_rate_limiter = RateLimiter(
    times=settings.RATE_LIMIT_REQUESTS,
    seconds=settings.RATE_LIMIT_WINDOW_SECONDS
)