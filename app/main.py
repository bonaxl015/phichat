from fastapi import FastAPI


def create_app():
    app = FastAPI(title="PhiChat")

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    return app


app = create_app()
