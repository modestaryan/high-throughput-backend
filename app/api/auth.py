from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.services.auth_service import register_user, authenticate_user, generate_token
from app.core.rate_limiter import RateLimiter
from app.core.idempotency import check_idempotency, save_idempotent_response

router = APIRouter()

# Rate limiters for auth endpoints
auth_limiter = RateLimiter(times=20, seconds=60)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(auth_limiter)])
async def register(request: Request, data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    User Registration endpoint with Idempotency Key support and Rate Limiting.
    """
    # 1. Idempotency Check
    cached_response = await check_idempotency(request)
    if cached_response:
        return cached_response

    # 2. Service Execution
    user = await register_user(db, data.email, data.password, role=data.role or "user")

    response_payload = {
        "id": str(user.id),
        "email": user.email,
        "role": user.role
    }

    # 3. Store Idempotency Cache
    await save_idempotent_response(request, response_payload, status_code=201)

    return response_payload

@router.post("/login", response_model=TokenResponse, dependencies=[Depends(auth_limiter)])
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user credentials and issue a signed JWT access token.
    """
    user = await authenticate_user(db, data.email, data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password credentials"
        )

    token = generate_token(user)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "role": user.role
        }
    }