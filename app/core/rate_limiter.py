from fastapi import HTTPException
from app.core.redis import redis_client

RATE_LIMIT = 10000     # max requests
TIME_WINDOW = 10      # seconds

def rate_limit(user_id: str):
    key = f"rate_limit:{user_id}"

    current = redis_client.get(key)

    if current and int(current) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Too many requests")

    pipe = redis_client.pipeline()

    pipe.incr(key, 1)

    if not current:
        pipe.expire(key, TIME_WINDOW)

    pipe.execute()