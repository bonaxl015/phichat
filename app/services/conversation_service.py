from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, func

from app.models.conversation import Conversation
from app.models.unread import ConversationUnread
from app.models.message import Message
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
    async def list_conversation_full(db: AsyncSession, user_id: str):
        user_uuid = await to_uuid(user_id)

        last_msg_subq = (
            select(
                Message.conversation_id, func.max(Message.sent_at).label("last_time")
            )
            .group_by(Message.conversation_id)
            .subquery()
        )

        stmt = (
            select(
                Conversation,
                ConversationUnread.unread_count,
                Message.id,
                Message.sender_id,
                Message.content,
                Message.sent_at,
            )
            .outerjoin(
                ConversationUnread,
                and_(
                    ConversationUnread.conversation_id == Conversation.id,
                    ConversationUnread.user_id == user_uuid,
                ),
            )
            .outerjoin(
                last_msg_subq, last_msg_subq.c.conversation_id == Conversation.id
            )
            .outerjoin(
                Message,
                and_(
                    Message.conversation_id == Conversation.id,
                    Message.sent_at == last_msg_subq.c.last_time,
                ),
            )
            .where(
                or_(
                    Conversation.user1_id == user_uuid,
                    Conversation.user2_id == user_uuid,
                )
            )
            .order_by(last_msg_subq.c.last_time.desc().nullslast())
        )

        result = await db.execute(stmt)
        return result.all()

    @staticmethod
    async def get_by_id(db: AsyncSession, conversation_id):
        conversation_uuid = await to_uuid(conversation_id)

        stmt = select(Conversation).where(Conversation.id == conversation_uuid)

        result = await db.execute(stmt)
        return result.scalar_one_or_none()
