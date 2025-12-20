from fastapi import WebSocket, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.jwt import decode_access_token
from app.services.user_service import UserService
from app.database.connection import get_db
from app.core.exceptions import UnauthorizedException


async def get_current_user_ws(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    token = websocket.query_params.get("token")

    if not token:
        raise UnauthorizedException("Missing token")

    payload = decode_access_token(token)

    if not payload or "sub" not in payload:
        raise UnauthorizedException("Invalid token")

    user_id = payload["sub"]

    user = await UserService.get_user_by_id(db, user_id=user_id)

    if not user:
        raise UnauthorizedException("User not found")

    return user
