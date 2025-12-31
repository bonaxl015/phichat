from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.conversation import Conversation
from app.models.user import User
from app.websocket.manager import ConnectionManager


async def handle_typing_start(
    data: dict,
    websocket: WebSocket,
    user: User,
    conversation: Conversation,
    conversation_id: str,
    manager: ConnectionManager,
    db: AsyncSession,
):
    await manager.broadcast_typing(str(conversation_id), str(user.id), True)


async def handle_typing_stop(
    data: dict,
    websocket: WebSocket,
    user: User,
    conversation: Conversation,
    conversation_id: str,
    manager: ConnectionManager,
    db: AsyncSession,
):
    await manager.broadcast_typing(str(conversation_id), str(user.id), False)
