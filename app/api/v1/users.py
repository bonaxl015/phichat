from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_user
from app.database.connection import get_db
from app.schemas.user import UserRead
from app.services.user_service import UserService

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get("/me", response_model=UserRead)
async def get_me(current_user=Depends(get_current_user)):
    return current_user


@router.get("/search", response_model=list[UserRead])
async def search_users(
    q: str = Query(..., description="Search term for username or email"),
    limit: int = Query(20, ge=1, le=50),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    users = await UserService.search_users(
        db, q, exclude_user_id=current_user.id, limit=limit
    )

    return users
