from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, UUID

from app.models.conversation_model import Conversation
from app.models.unread_model import ConversationUnread
from app.utils.uuid_util import to_uuid


class UnreadService:

    @staticmethod
    async def ensure_entry(db: AsyncSession, conversation_id: str, user_id: str):
        conversation_uuid = await to_uuid(conversation_id)
        user_uuid = await to_uuid(user_id)

        stmt = select(ConversationUnread).where(
            ConversationUnread.conversation_id == conversation_uuid,
            ConversationUnread.user_id == user_uuid,
        )
        result = await db.execute(stmt)
        entry = result.scalar_one_or_none()

        if entry:
            return entry

        entry = ConversationUnread(
            conversation_id=conversation_uuid, user_id=user_uuid, unread_count=0
        )

        db.add(entry)
        await db.commit()
        await db.refresh(entry)
        return entry

    @staticmethod
    async def increment(
        db: AsyncSession, conversation: Conversation, receiver_id: UUID
    ):
        receiver_uuid = await to_uuid(receiver_id)
        entry = await UnreadService.ensure_entry(
            db=db, conversation_id=conversation.id, user_id=receiver_uuid
        )

        entry.unread_count += 1
        await db.commit()
        await db.refresh(entry)
        return entry

    @staticmethod
    async def reset(db: AsyncSession, conversation_id: str, user_id: str):
        conversation_uuid = await to_uuid(conversation_id)
        user_uuid = await to_uuid(user_id)

        entry = await UnreadService.ensure_entry(
            db=db, conversation_id=conversation_uuid, user_id=user_uuid
        )

        entry.unread_count = 0
        await db.commit()
        await db.refresh(entry)
        return entry

    @staticmethod
    async def get_unread(db: AsyncSession, conversation_id: str, user_id: str):
        conversation_uuid = await to_uuid(conversation_id)
        user_uuid = await to_uuid(user_id)

        entry = await UnreadService.ensure_entry(
            db=db, conversation_id=conversation_uuid, user_id=user_uuid
        )

        return entry.unread_count
