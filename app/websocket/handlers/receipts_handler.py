from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.conversation_model import Conversation
from app.models.user_model import User
from app.websocket.manager import ConnectionManager
from app.services.message_service import MessageService
from app.services.unread_service import UnreadService
from app.websocket.state import notification_manager


async def handle_message_delivered(
    data: dict,
    websocket: WebSocket,
    user: User,
    conversation: Conversation,
    conversation_id: str,
    manager: ConnectionManager,
    db: AsyncSession,
):
    message_id: str = data.get("message_id")

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
    message_id: str = data.get("message_id")

    msg = await MessageService.mark_read(db, message_id=message_id, user_id=user.id)

    await UnreadService.reset(db=db, conversation_id=conversation_id, user_id=user.id)

    await manager.broadcast_to_conversation(
        conversation_id=conversation_id,
        message={
            "event": "message_read",
            "data": {"message_id": str(msg.id), "read_at": str(msg.read_at)},
        },
    )

    await manager.broadcast_to_conversation(
        conversation_id=conversation_id,
        message={
            "event": "unread_update",
            "conversation_id": conversation_id,
            "unread": 0,
        },
    )

    receiver_id_str = str(msg.receiver_id)
    conversation_room = manager.conversations.get(conversation_id, set())
    receiver_is_in_room = any(
        ws in conversation_room
        for ws in manager.active_users.get(receiver_id_str, set())
    )

    if not receiver_is_in_room:
        await notification_manager.send_notifications(
            receiver_id_str,
            {
                "event": "notification",
                "type": "message_read",
                "conversation_id": conversation_id,
                "from_user_id": str(user.id),
                "preview": msg.content,
                "sent_at": msg.sent_at.isoformat(),
            },
        )
