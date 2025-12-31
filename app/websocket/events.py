from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.conversation import Conversation
from app.models.user import User
from app.websocket.manager import ConnectionManager
from app.websocket.handlers.typing_handler import handle_typing_start, handle_typing_stop
from app.websocket.handlers.messaging_handler import handle_send_message
from app.websocket.handlers.receipts_handler import (
    handle_message_delivered,
    handle_message_read,
)
from app.websocket.handlers.editing_handler import handle_delete_message, handle_edit_message


event_handlers = {
    "typing_start": handle_typing_start,
    "typing_stop": handle_typing_stop,
    "send_message": handle_send_message,
    "message_delivered": handle_message_delivered,
    "message_read": handle_message_read,
    "message_edit": handle_delete_message,
    "message_delete": handle_edit_message,
}


async def dispatch_event(
    event_name: str,
    data: dict,
    websocket: WebSocket,
    user: User,
    conversation: Conversation,
    conversation_id: str,
    manager: ConnectionManager,
    db: AsyncSession,
):
    handler = event_handlers.get(event_name)

    if not handler:
        await websocket.send_json(
            {"event": "error", "message": f"Unknown event: {event_name}"}
        )

        return

    await handler(
        data=data,
        websocket=websocket,
        user=user,
        conversation=conversation,
        conversation_id=conversation_id,
        manager=manager,
        db=db,
    )
