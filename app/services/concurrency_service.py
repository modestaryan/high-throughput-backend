from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.user import User

async def safe_update_user_role_concurrently(
    db: AsyncSession,
    user_id: UUID,
    new_role: str
) -> User:
    """
    Demonstrates pessimistic locking (SELECT FOR UPDATE) to safely prevent race conditions
    and lost updates under high concurrency.
    """
    # Execute query with FOR UPDATE lock on target row
    query = select(User).where(User.id == user_id).with_for_update()
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.role = new_role
    await db.commit()
    await db.refresh(user)

    return user
