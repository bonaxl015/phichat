from fastapi import APIRouter, WebSocket, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.websocket.state import notification_manager
from app.websocket.deps import get_current_user_ws
from app.database.connection import get_db

router = APIRouter()


@router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    user=Depends(get_current_user_ws),
    db: AsyncSession = Depends(get_db),
):
    await notification_manager.connect(websocket=websocket, user_id=str(user.id))

    try:
        while True:
            await websocket.receive_text()
    except Exception:
        pass
    finally:
        notification_manager.disconnect(websocket=websocket, user_id=str(user.id))
