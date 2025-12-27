import asyncio
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    DISCONNECT_GRACE_SECONDS = 4

    def __init__(self):
        # user_id -> set of websocket connections
        self.active_users: Dict[str, Set[WebSocket]] = {}

        # conversation_id -> set of websocket connections
        self.conversations: Dict[str, Set[WebSocket]] = {}

        # user_id -> connection count
        self.presence: Dict[str, int] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()

        self.active_users.setdefault(user_id, set()).add(websocket)

        previous_count = self.presence.get(user_id, 0)
        new_count = previous_count + 1
        self.presence[user_id] = new_count

        if previous_count == 0:
            return "online"

        return None

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_users:
            self.active_users[user_id].discard(websocket)

            if not self.active_users[user_id]:
                del self.active_users[user_id]

        count = self.presence.get(user_id, 0) - 1

        if count <= 0:
            self.presence.pop(user_id, None)
            return "offline"

        self.presence[user_id] = count
        return None

    async def delayed_presence_check(self, user_id: str):
        await asyncio.sleep(self.DISCONNECT_GRACE_SECONDS)

        if user_id not in self.active_users:
            return "offline"

        return None

    def join_conversation(self, websocket: WebSocket, conversation_id: str):
        self.conversations.setdefault(conversation_id, set()).add(websocket)

    def leave_conversation(self, websocket: WebSocket, conversation_id: str):
        if conversation_id in self.conversations:
            self.conversations[conversation_id].discard(websocket)

            if not self.conversations[conversation_id]:
                del self.conversations[conversation_id]

    async def _safe_broadcast(self, sockets: Set, message: dict):
        for ws in list(sockets):
            try:
                await ws.send_json(message)
            except (WebSocketDisconnect, Exception):
                self._remove_dead_socket(ws)

    async def broadcast_to_conversation(self, conversation_id: str, message: dict):
        sockets = self.conversations.get(conversation_id, set())
        await self._safe_broadcast(sockets, message)

    async def broadcast_typing(
        self, conversation_id: str, user_id: str, is_typing: bool
    ):
        message = {"event": "typing", "user_id": user_id, "is_typing": is_typing}
        sockets = self.conversations.get(conversation_id, set())
        await self._safe_broadcast(sockets, message)

    async def broadcast_presence(self, user_id: str, status: str):
        message = {"event": "presence", "user_id": user_id, "status": status}

        for uid, sockets in self.active_users.items():
            if uid != user_id:
                await self._safe_broadcast(sockets, message)

    def _remove_dead_socket(self, websocket):
        # Remove from active users
        for user_id, sockets in list(self.active_users.items()):
            if websocket in sockets:
                sockets.remove(websocket)
                if not sockets:
                    del self.active_users[user_id]

        # Remove from conversation room
        for conv_id, sockets in list(self.conversations.items()):
            if websocket in sockets:
                sockets.remove(websocket)
                if not sockets:
                    del self.conversations[conv_id]
