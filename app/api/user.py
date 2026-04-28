from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.models.user import User

from app.core.redis import redis_client
import json

router = APIRouter()

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):

    cache_key = f"user:{current_user.id}"

    # 🔥 1. CHECK CACHE (ASYNC)
    cached_user = await redis_client.get(cache_key)
    if cached_user:
        return json.loads(cached_user)

    # 🔥 2. PREPARE RESPONSE
    user_data = {
        "id": str(current_user.id),
        "email": current_user.email
    }

    # 🔥 3. STORE IN REDIS (ASYNC)
    await redis_client.setex(cache_key, 60, json.dumps(user_data))

    return user_data