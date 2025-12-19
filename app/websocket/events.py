from fastapi import WebSocket
from app.models.conversation import Conversation
from app.models.user import User
from app.websocket.manager import ConnectionManager
from app.websocket.handlers.typing import handle_typing_start, handle_typing_stop
from app.websocket.handlers.messaging import handle_send_message

event_handlers = {
    "typing_start": handle_typing_start,
    "typing_stop": handle_typing_stop,
    "send_message": handle_send_message,
}


async def dispatch_event(
    event_name: str,
    data: dict,
    websocket: WebSocket,
    user: User,
    conversation: Conversation,
    conversation_id: str,
    manager: ConnectionManager,
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
    )
