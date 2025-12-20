from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_

from app.models.conversation import Conversation
from app.models.unread import ConversationUnread
from app.core.exceptions import AppException, DatabaseException
from app.utils.uuid import to_uuid


class ConversationService:

    @staticmethod
    async def get_or_create_conversation(
        db: AsyncSession, user1_id: str, user2_id: str
    ):
        try:
            user1_uuid = await to_uuid(user1_id)
            user2_uuid = await to_uuid(user2_id)

            stmt = select(Conversation).where(
                or_(
                    and_(
                        Conversation.user1_id == user1_uuid,
                        Conversation.user2_id == user2_uuid,
                    ),
                    and_(
                        Conversation.user1_id == user2_uuid,
                        Conversation.user2_id == user1_uuid,
                    ),
                )
            )

            result = await db.execute(stmt)
            conversation = result.scalar_one_or_none()

            if conversation:
                return conversation

            conversation = Conversation(user1_id=user1_uuid, user2_id=user2_uuid)
            db.add(conversation)
            await db.commit()
            await db.refresh(conversation)

            return conversation
        except AppException:
            raise
        except Exception as e:
            raise DatabaseException(str(e))

    @staticmethod
    async def list_conversations(db: AsyncSession, user_id: str):
        user_uuid = await to_uuid(user_id)

        stmt = (
            select(Conversation)
            .where(
                or_(
                    Conversation.user1_id == user_uuid,
                    Conversation.user2_id == user_uuid,
                )
            )
            .order_by(Conversation.created_at.desc())
        )

        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def list_conversations_with_unread(db: AsyncSession, user_id: str):
        user_uuid = await to_uuid(user_id)

        stmt = (
            select(Conversation, ConversationUnread.unread_count)
            .outerjoin(
                ConversationUnread,
                and_(
                    (ConversationUnread.conversation_id == Conversation.id),
                    (ConversationUnread.user_id == user_uuid),
                ),
            )
            .where(
                or_(
                    Conversation.user1_id == user_uuid,
                    Conversation.user2_id == user_uuid,
                )
            )
            .order_by(Conversation.created_at.desc())
        )

        result = await db.execute(stmt)
        return result.all()

    @staticmethod
    async def get_by_id(db: AsyncSession, conversation_id):
        conversation_uuid = await to_uuid(conversation_id)

        stmt = select(Conversation).where(Conversation.id == conversation_uuid)

        result = await db.execute(stmt)
        return result.scalar_one_or_none()
