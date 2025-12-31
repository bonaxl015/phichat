from fastapi import APIRouter, WebSocket, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.websocket.state import connection_manager
from app.websocket.deps import get_current_user_ws
from app.websocket.events import dispatch_event
from app.services.conversation_service import ConversationService
from app.services.message_service import MessageService
from app.database.connection import get_db
from app.utils.uuid_util import to_uuid

router = APIRouter()


@router.websocket("/ws/chat/{conversation_id}")
async def websocket_chat(
    websocket: WebSocket,
    conversation_id: str,
    user=Depends(get_current_user_ws),
    db: AsyncSession = Depends(get_db),
):
    conversation_uuid = await to_uuid(conversation_id)

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

    status = await connection_manager.connect(websocket=websocket, user_id=str(user.id))
    connection_manager.join_conversation(
        websocket=websocket, conversation_id=conversation_id
    )

    if status == "online":
        await connection_manager.broadcast_presence(str(user.id), "online")

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
                manager=connection_manager,
                db=db,
            )
    except Exception:
        pass
    finally:
        status = connection_manager.disconnect(websocket=websocket, user_id=user.id)
        connection_manager.leave_conversation(
            websocket=websocket, conversation_id=conversation_id
        )

        if status == "offline":
            result = await connection_manager.delayed_presence_check(str(user.id))
            if result == "offline":
                from datetime import datetime, UTC

                user.last_seen = datetime.now(UTC)
                await db.commit()

                await connection_manager.broadcast_presence(str(user.id), "offline")
