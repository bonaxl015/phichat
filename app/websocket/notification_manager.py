from typing import Dict, Set
from fastapi import WebSocketDisconnect, WebSocket


class NotificationManager:
    def __init__(self):
        self.user_sockets: Dict[str, Set] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()

        self.user_sockets.setdefault(user_id, set()).add(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.user_sockets:
            self.user_sockets[user_id].discard(websocket)

            if not self.user_sockets[user_id]:
                del self.user_sockets[user_id]

    async def send_notifications(self, user_id: str, payload: Dict):
        sockets = self.user_sockets.get(user_id, set())

        for ws in list(sockets):
            try:
                await ws.send_json(payload)
            except WebSocketDisconnect:
                self.disconnect(ws, user_id=user_id)
            except Exception:
                self.disconnect(ws, user_id=user_id)
