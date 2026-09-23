from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.models.user import User
from app.api.deps import require_role
from app.core.redis import redis_client

router = APIRouter()

class UserRoleUpdate(BaseModel):
    role: str

class UserAdminResponse(BaseModel):
    id: str
    email: str
    role: str

@router.get("/users", response_model=List[UserAdminResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_role("admin"))
):
    """
    [Admin Only] List all registered users.
    """
    result = await db.execute(select(User))
    users = result.scalars().all()
    return [
        UserAdminResponse(id=str(u.id), email=u.email, role=u.role)
        for u in users
    ]

@router.patch("/users/{user_id}/role", response_model=UserAdminResponse)
async def update_user_role(
    user_id: UUID,
    payload: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_role("admin"))
):
    """
    [Admin Only] Modify a user's access role (e.g. 'user', 'manager', 'admin').
    """
    if payload.role not in ["user", "manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role specified. Must be 'user', 'manager', or 'admin'."
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.role = payload.role
    await db.commit()
    await db.refresh(user)

    # Invalidate cached user profile if exists
    cache_key = f"user:{user.id}"
    try:
        await redis_client.delete(cache_key)
    except Exception:
        pass

    return UserAdminResponse(id=str(user.id), email=user.email, role=user.role)

@router.get("/stats")
async def get_system_stats(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_role("admin"))
):
    """
    [Admin Only] High-level metrics on users and Redis infrastructure.
    """
    user_count_res = await db.execute(select(func.count(User.id)))
    total_users = user_count_res.scalar() or 0

    redis_keys_count = 0
    try:
        info = await redis_client.info("db0")
        redis_keys_count = info.get("db0", {}).get("keys", 0) if isinstance(info, dict) else 0
    except Exception:
        pass

    return {
        "total_users": total_users,
        "redis_cached_keys": redis_keys_count,
        "status": "healthy"
    }
