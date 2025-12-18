from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_user
from app.database.connection import get_db
from app.schemas.message import MessageRead, MessageCreate
from app.services.conversation_service import ConversationService
from app.services.message_service import MessageService
from app.core.exceptions import AppException
from app.utils.uuid import to_uuid

router = APIRouter(prefix="/api/v1/messages", tags=["Messages"])


@router.post("/{conversation_id}", response_model=MessageRead)
async def send_message(
    conversation_id: str,
    payload: MessageCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conversation_uuid = await to_uuid(conversation_id)

    conversation = await ConversationService.get_by_id(db, conversation_uuid)

    if not conversation:
        raise AppException("Conversation not found")

    can_access = await MessageService.can_user_access_conversation(
        db, conversation=conversation, user_id=current_user.id
    )

    if not can_access:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    msg = await MessageService.send_message(
        db,
        conversation=conversation,
        sender_id=current_user.id,
        content=payload.content,
    )

    return msg


@router.get("/{conversation_id}", response_model=list[MessageRead])
async def list_messages(
    conversation_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conversation_uuid = await to_uuid(conversation_id)

    conversation = await ConversationService.get_by_id(db, conversation_uuid)

    if not conversation:
        raise AppException("Conversation not found")

    can_access = await MessageService.can_user_access_conversation(
        db, conversation=conversation, user_id=current_user.id
    )

    if not can_access:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    messages = await MessageService.list_messages(db, conv_id=conversation_uuid)

    return messages
