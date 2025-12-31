import asyncio
from app.database.connection import engine
from app.database.base import Base

from app.models.user_model import User  # noqa: F401
from app.models.friendship_model import Friendship  # noqa: F401
from app.models.conversation_model import Conversation  # noqa: F401
from app.models.message_model import Message  # noqa: F401
from app.models.unread_model import ConversationUnread  # noqa: F401
from app.models.conversation_settings_model import ConversationSettings  # noqa: F401


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Database tables created successfully.")


if __name__ == "__main__":
    asyncio.run(init_db())
