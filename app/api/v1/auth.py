from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate, UserRead
from app.services.user_service import UserService
from app.database.connection import get_db

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        user = await UserService.create_user(
            db,
            username=payload.username,
            email=payload.email,
            password=payload.password
        )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
