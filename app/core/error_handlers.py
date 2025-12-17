from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import AppException, DatabaseException, UnauthorizedException


async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=400, content={"error": exc.message, "details": exc.message}
    )


async def unauthorized_exception_handler(request: Request, exc: UnauthorizedException):
    return JSONResponse(
        status_code=401, content={"error": "Unauthorized", "details": exc.message}
    )


async def database_exception_handler(request: Request, exc: DatabaseException):
    return JSONResponse(
        status_code=500, content={"error": "Database error", "details": exc.message}
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500,
        content={"error": "Database error", "details": "Database operation failed"},
    )


async def validation_exception_handler(request: Request, exc: ValidationError):
    details = list(map(lambda err: err["msg"], exc.errors()))
    return JSONResponse(
        status_code=422, content={"error": "Validation error", "details": details}
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "HTTP exception error", "details": exc.detail},
    )


async def unexpected_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Error", "details": "An unexpected error occurred"},
    )
