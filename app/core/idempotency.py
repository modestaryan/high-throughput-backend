import json
import logging
from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from app.core.redis import redis_client
from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

IDEMPOTENCY_HEADER = "X-Idempotency-Key"

async def check_idempotency(request: Request) -> Optional[JSONResponse]:
    """
    Dependency/Helper to verify if a request carrying X-Idempotency-Key has already been processed.
    Returns cached JSONResponse if hit, raises 409 if currently in flight, or returns None if new.
    """
    idempotency_key = request.headers.get(IDEMPOTENCY_HEADER)
    if not idempotency_key:
        return None

    redis_key = f"idempotency:{idempotency_key}"

    try:
        cached_data = await redis_client.get(redis_key)
        if cached_data:
            if cached_data == "PROCESSING":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A request with this Idempotency-Key is currently being processed."
                )

            payload = json.loads(cached_data)
            logger.info(f"Idempotency hit for key {idempotency_key}")
            return JSONResponse(
                status_code=payload.get("status_code", 200),
                content=payload.get("content"),
                headers={"X-Cache": "Idempotency-Hit"}
            )

        # Mark request as processing with short lock TTL (30s) to handle crashes
        await redis_client.setex(redis_key, 30, "PROCESSING")
        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Idempotency check bypassed due to Redis error: {e}")
        return None

async def save_idempotent_response(
    request: Request,
    response_content: dict,
    status_code: int = 200,
    expire_seconds: int = settings.IDEMPOTENCY_EXPIRE_SECONDS
) -> None:
    """
    Save execution result in Redis for a given X-Idempotency-Key.
    """
    idempotency_key = request.headers.get(IDEMPOTENCY_HEADER)
    if not idempotency_key:
        return

    redis_key = f"idempotency:{idempotency_key}"
    try:
        payload = {
            "status_code": status_code,
            "content": response_content
        }
        await redis_client.setex(redis_key, expire_seconds, json.dumps(payload))
    except Exception as e:
        logger.warning(f"Failed to save idempotency response to Redis: {e}")
