from fastapi import APIRouter, WebSocket
from app.websocket.manager import ConnectionManager
from app.websocket.deps import get_current_user_ws
from app.websocket.events import dispatch_event
from app.services.conversation_service import ConversationService
from app.services.message_service import MessageService
from app.database.connection import AsyncSessionLocal
from app.utils.uuid import to_uuid

router = APIRouter()
manager = ConnectionManager()


@router.websocket("/ws/chat/{conversation_id}")
async def websocket_chat(websocket: WebSocket, conversation_id: str):
    try:
        user = await get_current_user_ws(websocket=websocket)
    except Exception:
        await websocket.close()
        return

    conversation_uuid = await to_uuid(conversation_id)

    async with AsyncSessionLocal() as db:
        conversation = await ConversationService.get_by_id(
            db, conversation_id=conversation_uuid
        )

        if not conversation:
            await websocket.close()
            return

        can_access = await MessageService.can_user_access_conversation(
            db, conversation=conversation, user_id=user.id
        )

        if not can_access:
            await websocket.close()
            return

    await manager.connect(websocket=websocket, user_id=str(user.id))
    manager.join_conversation(websocket=websocket, conversation_id=conversation_id)

    try:
        while True:
            data = await websocket.receive_json()
            event_name = data.get("event")

            await dispatch_event(
                event_name=event_name,
                data=data,
                websocket=websocket,
                user=user,
                conversation=conversation,
                conversation_id=conversation_id,
                manager=manager,
            )
    except Exception:
        pass
    finally:
        manager.disconnect(websocket=websocket, user_id=user.id)
        manager.leave_conversation(websocket=websocket, conversation_id=conversation_id)
