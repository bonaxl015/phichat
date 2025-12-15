from fastapi import FastAPI
from app.core.config import settings


def create_app():
    app = FastAPI(title=settings.app_name)

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    return app


app = create_app()
