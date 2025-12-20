from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.conversation import Conversation
from app.models.user import User
from app.websocket.manager import ConnectionManager
from app.services.message_service import MessageService


async def handle_message_delivered(
    data: dict,
    websocket: WebSocket,
    user: User,
    conversation: Conversation,
    conversation_id: str,
    manager: ConnectionManager,
    db: AsyncSession,
):
    message_id = data.get("message_id")

    msg = await MessageService.mark_delivered(
        db, message_id=message_id, user_id=user.id
    )

    await manager.broadcast_to_conversation(
        conversation_id=conversation_id,
        message={
            "event": "message_delivered",
            "data": {"message_id": str(msg.id), "delivered_at": str(msg.delivered_at)},
        },
    )


async def handle_message_read(
    data: dict,
    websocket: WebSocket,
    user: User,
    conversation: Conversation,
    conversation_id: str,
    manager: ConnectionManager,
    db: AsyncSession,
):
    message_id = data.get("message_id")

    msg = await MessageService.mark_read(db, message_id=message_id, user_id=user.id)

    await manager.broadcast_to_conversation(
        conversation_id=conversation_id,
        message={
            "event": "message_read",
            "data": {"message_id": str(msg.id), "read_at": str(msg.read_at)},
        },
    )
