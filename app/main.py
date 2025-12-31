from typing import Callable, cast
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import Response
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.friends import router as friends_router
from app.api.v1.conversations import router as conversations_router
from app.api.v1.messages import router as messages_router
from app.api.v1.ws import router as websocket_router
from app.api.v1.ws_notifications import router as ws_notifications_router
from app.core.exceptions import AppException, DatabaseException, UnauthorizedException
from app.core.error_handlers import (
    app_exception_handler,
    unauthorized_exception_handler,
    database_exception_handler,
    sqlalchemy_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    unexpected_exception_handler,
)


def create_app():
    app = FastAPI(title=settings.app_name)

    # Route handlers
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(friends_router)
    app.include_router(conversations_router)
    app.include_router(messages_router)
    app.include_router(websocket_router)
    app.include_router(ws_notifications_router)

    # Custom exception handlers
    app.add_exception_handler(
        AppException,
        cast(Callable[[Request, Exception], Response], app_exception_handler),
    )
    app.add_exception_handler(
        UnauthorizedException,
        cast(Callable[[Request, Exception], Response], unauthorized_exception_handler),
    )
    app.add_exception_handler(
        DatabaseException,
        cast(Callable[[Request, Exception], Response], database_exception_handler),
    )
    app.add_exception_handler(
        SQLAlchemyError,
        cast(Callable[[Request, Exception], Response], sqlalchemy_exception_handler),
    )
    app.add_exception_handler(
        RequestValidationError,
        cast(Callable[[Request, Exception], Response], validation_exception_handler),
    )
    app.add_exception_handler(
        HTTPException,
        cast(Callable[[Request, Exception], Response], http_exception_handler),
    )
    app.add_exception_handler(
        Exception,
        cast(Callable[[Request, Exception], Response], unexpected_exception_handler),
    )

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    return app


app = create_app()
