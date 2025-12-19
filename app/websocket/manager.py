from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    def __init__(self):
        self.active_users: Dict[str, Set[WebSocket]] = {}
        self.conversations: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()

        if user_id not in self.active_users:
            self.active_users[user_id] = set()

        self.active_users[user_id].add(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_users:
            self.active_users[user_id].discard(websocket)

            if not self.active_users[user_id]:
                del self.active_users[user_id]

    def join_conversation(self, websocket: WebSocket, conversation_id: str):
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = set()

        self.conversations[conversation_id].add(websocket)

    def leave_conversation(self, websocket: WebSocket, conversation_id: str):
        if conversation_id in self.conversations:
            self.conversations[conversation_id].discard(websocket)

            if not self.conversations[conversation_id]:
                del self.conversations[conversation_id]

    async def broadcast_to_conversation(self, conversation_id: str, message: dict):
        if conversation_id not in self.conversations:
            return

        for ws in self.conversations[conversation_id]:
            try:
                await ws.send_json(message)
            except WebSocketDisconnect:
                self.conversations[conversation_id].discard(ws)
            except RuntimeError:
                self.conversations[conversation_id].discard(ws)
            except Exception:
                self.conversations[conversation_id].discard(ws)
