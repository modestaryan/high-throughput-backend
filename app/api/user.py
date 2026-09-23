import json
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse
from app.core.redis import redis_client
from app.core.rate_limiter import default_rate_limiter

router = APIRouter()

@router.get("/me", response_model=UserResponse, dependencies=[Depends(default_rate_limiter)])
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Retrieve current authenticated user profile with 60-second Redis caching.
    """
    cache_key = f"user:{current_user.id}"

    try:
        # 1. Check Redis cache
        cached_user = await redis_client.get(cache_key)
        if cached_user:
            return json.loads(cached_user)
    except Exception:
        pass

    # 2. Build profile dictionary
    user_data = {
        "id": str(current_user.id),
        "email": current_user.email,
        "role": current_user.role
    }

    try:
        # 3. Cache profile in Redis
        await redis_client.setex(cache_key, 60, json.dumps(user_data))
    except Exception:
        pass

    return user_data