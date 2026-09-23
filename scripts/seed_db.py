import asyncio
import logging
from sqlalchemy import select
from app.db.session import AsyncSessionLocal, engine
from app.db.base import Base
from app.models.user import User
from app.core.security import hash_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

INITIAL_USERS = [
    {
        "email": "admin@example.com",
        "password": "AdminPassword123!",
        "role": "admin"
    },
    {
        "email": "manager@example.com",
        "password": "ManagerPassword123!",
        "role": "manager"
    },
    {
        "email": "test1@gmail.com",
        "password": "123456",
        "role": "user"
    }
]

async def seed_database():
    logger.info("Initializing database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        for user_data in INITIAL_USERS:
            res = await session.execute(select(User).where(User.email == user_data["email"]))
            existing = res.scalars().first()
            if not existing:
                user = User(
                    email=user_data["email"],
                    password_hash=hash_password(user_data["password"]),
                    role=user_data["role"]
                )
                session.add(user)
                logger.info(f"Seeded user: {user_data['email']} (Role: {user_data['role']})")
            else:
                logger.info(f"User already exists: {user_data['email']}")

        await session.commit()
    logger.info("Database seeding completed successfully.")

if __name__ == "__main__":
    asyncio.run(seed_database())
