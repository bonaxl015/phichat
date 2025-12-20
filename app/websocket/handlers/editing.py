from sqlalchemy.ext.asyncio import AsyncSession
from app.services.message_service import MessageService
from fastapi import WebSocket
from app.models.conversation import Conversation
from app.models.user import User
from app.websocket.manager import ConnectionManager


async def handle_edit_message(
    data: dict,
    websocket: WebSocket,
    user: User,
    conversation: Conversation,
    conversation_id: str,
    manager: ConnectionManager,
    db: AsyncSession,
):
    message_id = data.get("message_id")
    content = data.get("content")

    msg = await MessageService.edit_message(
        db=db, message_id=message_id, user_id=user.id, new_content=content
    )

    await manager.broadcast_to_conversation(
        conversation_id=conversation_id,
        message={
            "event": "message_updated",
            "data": {
                "id": str(msg.id),
                "content": msg.content,
                "edited_at": msg.edited_at.isoformat(),
            },
        },
    )


async def handle_delete_message(
    data: dict,
    websocket: WebSocket,
    user: User,
    conversation: Conversation,
    conversation_id: str,
    manager: ConnectionManager,
    db: AsyncSession,
):
    message_id = data.get("message_id")

    msg = await MessageService.delete_message(
        db=db, message_id=message_id, user_id=user.id
    )

    await manager.broadcast_to_conversation(
        conversation_id=conversation_id,
        message={"event": "message_deleted", "data": {"id": str(msg.id)}},
    )
