from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.jwt_util import decode_access_token
from app.database.connection import get_db
from app.services.user_service import UserService
from app.core.exceptions import UnauthorizedException

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload or "sub" not in payload:
        raise UnauthorizedException("Invalid or expired token")

    user_id = payload["sub"]

    user = await UserService.get_user_by_id(db, user_id)

    if not user:
        raise UnauthorizedException("User not found")

    return user
