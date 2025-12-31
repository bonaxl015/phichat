from sqlalchemy.ext.asyncio import AsyncSession
from app.services.message_service import MessageService
from fastapi import WebSocket
from app.models.conversation import Conversation
from app.models.user import User
from app.websocket.manager import ConnectionManager
from app.websocket.state import notification_manager


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
                "type": "message_edit",
                "conversation_id": conversation_id,
                "from_user_id": str(user.id),
                "preview": msg.content,
                "sent_at": msg.sent_at.isoformat(),
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
                "type": "message_delete",
                "conversation_id": conversation_id,
                "from_user_id": str(user.id),
                "preview": msg.content,
                "sent_at": msg.sent_at.isoformat(),
            },
        )
