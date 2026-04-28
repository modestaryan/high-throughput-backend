from fastapi import FastAPI

from app.api import auth, user
from app.db.session import engine
from app.db.base import Base

import app.models.user

app = FastAPI(title="High-Throughput Backend")

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(user.router, prefix="/api/v1/users", tags=["Users"])

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)