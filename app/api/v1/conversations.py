from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.conversation import ConversationRead
from app.services.conversation_service import ConversationService
from app.api.deps.auth import get_current_user
from app.database.connection import get_db
from app.core.exceptions import AppException

router = APIRouter(prefix="/api/v1/conversations", tags=["Conversations"])


@router.get("", response_model=list[ConversationRead])
async def list_my_conversations(
    current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    conversations = await ConversationService.list_conversations(
        db, user_id=current_user.id
    )
    return conversations


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
