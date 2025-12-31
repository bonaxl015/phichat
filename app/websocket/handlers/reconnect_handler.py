from datetime import datetime
from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.conversation_model import Conversation
from app.models.user_model import User
from app.websocket.manager import ConnectionManager
from app.services.message_service import MessageService
from app.services.unread_service import UnreadService
from app.utils.uuid_util import to_uuid


async def handle_reconnect(
    data: dict,
    websocket: WebSocket,
    user: User,
    conversation: Conversation,
    conversation_id: str,
    manager: ConnectionManager,
    db: AsyncSession,
):
    last_ts = datetime.strptime(str(data.get("last_message_at")), "%Y-%m-%d %H:%M:%S")

    missed = await MessageService.list_messages_since(
        db, user_id=user.id, timestamp=last_ts
    )

    await websocket.send_json(
        {
            "event": "reconnect_success",
            "missed_messages": [
                {
                    "id": str(m.id),
                    "content": m.content,
                    "sender_id": str(m.sender_id),
                    "sent_at": m.sent_at.isoformat(),
                }
                for m in missed
            ],
        }
    )


async def handle_resume_conversation(
    data: dict,
    websocket: WebSocket,
    user: User,
    conversation: Conversation,
    conversation_id: str,
    manager: ConnectionManager,
    db: AsyncSession,
):
    new_conv_id: str = await to_uuid(data.get("conversation_id"))

    manager.join_conversation(websocket=websocket, conversation_id=str(new_conv_id))

    await UnreadService.reset(db, conversation_id=new_conv_id, user_id=user.id)

    await manager.broadcast_to_conversation(
        conversation_id=new_conv_id,
        message={
            "event": "unread_update",
            "conversation_id": str(new_conv_id),
            "unread": 0,
        },
    )

    await websocket.send_json(
        {"event": "resume_success", "conversation_id": str(new_conv_id)}
    )
