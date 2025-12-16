from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router


def create_app():
    app = FastAPI(title=settings.app_name)

    app.include_router(auth_router)
    app.include_router(users_router)

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    return app


app = create_app()
