from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    def __init__(self):
        self.active_users: Dict[str, Set[WebSocket]] = {}
        self.conversations: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()

        self.active_users.setdefault(user_id, set()).add(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_users:
            self.active_users[user_id].discard(websocket)

            if not self.active_users[user_id]:
                del self.active_users[user_id]

    def join_conversation(self, websocket: WebSocket, conversation_id: str):
        self.conversations.setdefault(conversation_id, set()).add(websocket)

    def leave_conversation(self, websocket: WebSocket, conversation_id: str):
        if conversation_id in self.conversations:
            self.conversations[conversation_id].discard(websocket)

            if not self.conversations[conversation_id]:
                del self.conversations[conversation_id]

    async def broadcast_to_conversation(self, conversation_id: str, message: dict):
        if conversation_id not in self.conversations:
            return

        websockets = list(self.conversations[conversation_id])
        for ws in websockets:
            try:
                await ws.send_json(message)
            except WebSocketDisconnect:
                self.conversations[conversation_id].discard(ws)
            except Exception:
                self.conversations[conversation_id].discard(ws)

    async def broadcast_typing(
        self, conversation_id: str, user_id: str, is_typing: bool
    ):
        await self.broadcast_to_conversation(
            conversation_id=conversation_id,
            message={"event": "typing", "user_id": user_id, "is_typing": is_typing},
        )
