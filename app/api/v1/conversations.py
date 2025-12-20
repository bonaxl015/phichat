from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.conversation import ConversationRead
from app.services.conversation_service import ConversationService
from app.api.deps.auth import get_current_user
from app.database.connection import get_db
from app.core.exceptions import AppException

router = APIRouter(prefix="/api/v1/conversations", tags=["Conversations"])


@router.get("")
async def list_my_conversations(
    current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    rows = await ConversationService.list_conversations_with_unread(
        db=db, user_id=current_user.id
    )

    response = []

    for conv, unread_count in rows:
        other_user = (
            conv.user2_id if conv.user1_id == current_user.id else conv.user1_id
        )

        response.append(
            {
                "id": str(conv.id),
                "user1_id": str(conv.user1_id),
                "user2_id": str(conv.user2_id),
                "other_user_id": str(other_user),
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
                "unread_count": unread_count or 0,
            }
        )

    print("1111111111111", response)
    return response


@router.post("/start", response_model=ConversationRead)
async def start_conversations(
    other_user_id: str = Query(...),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.id == other_user_id:
        raise AppException("You cannot start a conversation with yourself")

    conversation = await ConversationService.get_or_create_conversation(
        db, user1_id=current_user.id, user2_id=other_user_id
    )

    return conversation
