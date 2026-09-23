from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api import auth, user, admin
from app.db.session import engine
from app.db.base import Base
import app.models.user
from app.core.redis import redis_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Auto-create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: Close connections
    await engine.dispose()

app = FastAPI(
    title="High-Throughput Distributed Backend Service",
    description="Scalable distributed backend architecture with FastAPI, PostgreSQL, Redis rate limiting, JWT auth, and RBAC.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for cross-origin client integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(user.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin (RBAC)"])

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Comprehensive system health check inspecting Database and Redis connectivity.
    """
    db_status = "ok"
    redis_status = "ok"

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    try:
        await redis_client.ping()
    except Exception as e:
        redis_status = f"error: {str(e)}"

    overall_status = "healthy" if db_status == "ok" and redis_status == "ok" else "degraded"

    return {
        "status": overall_status,
        "database": db_status,
        "redis": redis_status,
        "service": "high-throughput-backend"
    }