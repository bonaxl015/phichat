import pytest
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings


@pytest.mark.asyncio
async def test_database_connection():
    engine = create_async_engine(settings.database_url, echo=False)
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            assert result.scalar() == 1
    finally:
        await engine.dispose()
