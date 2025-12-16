from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate, UserRead
from app.services.user_service import UserService
from app.database.connection import get_db
from app.schemas.auth import TokenResponse, LoginRequest
from app.utils.jwt import create_access_token

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        user = await UserService.create_user(
            db,
            username=payload.username,
            email=payload.email,
            password=payload.password,
        )
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await UserService.authenticate(
        db, username_or_email=payload.username_or_email, password=payload.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password",
        )

    token = create_access_token(str(user.id))

    return TokenResponse(access_token=token)
