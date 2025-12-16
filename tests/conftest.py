import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.models.user import User  # noqa: F401

# In-memory SQLite URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///file:memdb1?mode=memory&cache=shared"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True, connect_args={"uri": True})

TestSessionLocal = sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="function")
async def db():
    #  Fresh database for every test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    # Drop all tables after test session
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
