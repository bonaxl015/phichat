from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.conversation_model import Conversation
from app.models.user_model import User
from app.websocket.manager import ConnectionManager
from app.services.message_service import MessageService
from app.services.unread_service import UnreadService
from app.websocket.state import notification_manager


async def handle_send_message(
    data: dict,
    websocket: WebSocket,
    user: User,
    conversation: Conversation,
    conversation_id: str,
    manager: ConnectionManager,
    db: AsyncSession,
):
    content: str = data.get("content")

    msg = await MessageService.send_message(
        db,
        conversation=conversation,
        sender_id=user.id,
        content=content,
    )

    unread = await UnreadService.get_unread(
        db=db, conversation_id=conversation_id, user_id=msg.receiver_id
    )

    receiver_id_str = str(msg.receiver_id)

    await manager.broadcast_to_conversation(
        conversation_id,
        {
            "event": "new_message",
            "data": {
                "id": str(msg.id),
                "sender_id": str(msg.sender_id),
                "receiver_id": receiver_id_str,
                "content": msg.content,
                "sent_at": str(msg.sent_at),
            },
        },
    )

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
                "type": "message",
                "conversation_id": conversation_id,
                "from_user_id": str(user.id),
                "preview": msg.content,
                "sent_at": msg.sent_at.isoformat(),
            },
        )

    await manager.broadcast_to_conversation(
        conversation_id,
        {
            "event": "unread_update",
            "conversation_id": conversation_id,
            "unread": unread,
        },
    )
