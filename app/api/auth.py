from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import UserCreate, UserLogin
from app.services.auth_service import register_user, authenticate_user, generate_token

router = APIRouter()

@router.post("/register")
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await register_user(db, data.email, data.password)
    return {
        "id": str(user.id),
        "email": user.email
    }

@router.post("/login")
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, data.email, data.password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = generate_token(user)

    return {
        "access_token": token,
        "token_type": "bearer"
    }