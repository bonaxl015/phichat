from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.conversation import Conversation
from app.models.user import User
from app.websocket.manager import ConnectionManager
from app.services.message_service import MessageService


async def handle_send_message(
    data: dict,
    websocket: WebSocket,
    user: User,
    conversation: Conversation,
    conversation_id: str,
    manager: ConnectionManager,
    db: AsyncSession,
):
    content = data.get("content")

    msg = await MessageService.send_message(
        db,
        conversation=conversation,
        sender_id=user.id,
        content=content,
    )

    await manager.broadcast_to_conversation(
        conversation_id,
        {
            "event": "new_message",
            "data": {
                "id": str(msg.id),
                "sender_id": str(msg.sender_id),
                "receiver_id": str(msg.receiver_id),
                "content": msg.content,
                "sent_at": str(msg.sent_at),
            },
        },
    )
