from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.friendship import FriendshipRead
from app.services.friend_service import FriendService
from app.api.deps.authentication import get_current_user
from app.database.connection import get_db

router = APIRouter(prefix="/api/v1/friends", tags=["Friends"])


@router.post("/request", response_model=FriendshipRead)
async def send_friend_request(
    receiver_id: str = Query(...),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    friendship = await FriendService.send_request(
        db, requester_id=current_user.id, receiver_id=receiver_id
    )
    return friendship


@router.post("/{friendship_id}/accept", response_model=FriendshipRead)
async def accept_friend_request(
    friendship_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await FriendService.accept_request(
        db, friendship_id=friendship_id, user_id=str(current_user.id)
    )


@router.post("/{friendship_id}/reject", response_model=FriendshipRead)
async def reject_friend_request(
    friendship_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await FriendService.reject_request(
        db, friendship_id=friendship_id, user_id=str(current_user.id)
    )


@router.get("", response_model=list[FriendshipRead])
async def list_my_friends(
    current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return await FriendService.list_friends(db, user_id=str(current_user.id))


@router.get("/pending", response_model=list[FriendshipRead])
async def list_pending_requests(
    current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return await FriendService.list_pending(db, user_id=str(current_user.id))
