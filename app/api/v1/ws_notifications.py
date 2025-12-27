from fastapi import APIRouter, WebSocket, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.websocket.notification_manager import NotificationManager
from app.websocket.deps import get_current_user_ws
from app.database.connection import get_db

router = APIRouter()
notifications = NotificationManager()


@router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    user=Depends(get_current_user_ws),
    db: AsyncSession = Depends(get_db),
):
    await notifications.connect(websocket=websocket, user_id=str(user.id))

    try:
        while True:
            await websocket.receive_text()
    except Exception:
        pass
    finally:
        notifications.disconnect(websocket=websocket, user_id=str(user.id))
