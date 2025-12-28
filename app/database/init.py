import asyncio
from app.database.connection import engine
from app.database.base import Base

from app.models.user import User  # noqa: F401
from app.models.friendship import Friendship  # noqa: F401
from app.models.conversation import Conversation  # noqa: F401
from app.models.message import Message  # noqa: F401
from app.models.unread import ConversationUnread  # noqa: F401
from app.models.conversation_settings import ConversationSettings  # noqa: F401


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Database tables created successfully.")


if __name__ == "__main__":
    asyncio.run(init_db())
