import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, ASGITransport

from app.main import create_app
from app.database.connection import get_db
from app.database.base import Base
from app.models.user import User  # noqa: F401
from app.models.friendship import Friendship  # noqa: F401
from app.models.conversation import Conversation  # noqa: F401
from app.models.message import Message  # noqa: F401
from app.models.unread import ConversationUnread  # noqa: F401
from app.models.conversation_settings import ConversationSettings  # noqa: F401


# In-memory SQLite URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///file::memory:?cache=shared"

test_engine = create_async_engine(
    TEST_DATABASE_URL, echo=False, future=True, connect_args={"uri": True}
)

TestSessionLocal = sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)

app = create_app()


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


@pytest.fixture(autouse=True)
def override_db(db):
    async def override():
        yield db

    app.dependency_overrides[get_db] = override


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")

    yield client

    await client.aclose()


@pytest.fixture(scope="session", autouse=True)
def shutdown_event_loop(request):
    yield
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_engine.dispose())


@pytest.fixture(scope="session", autouse=True)
def fix_asyncio_warnings():
    asyncio.get_event_loop().set_debug(False)


@pytest.fixture(scope="session", autouse=True)
async def cleanup():
    yield
    await test_engine.dispose()
