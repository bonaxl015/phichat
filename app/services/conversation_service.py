import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, func

from app.models.conversation_model import Conversation
from app.models.unread_model import ConversationUnread
from app.models.conversation_settings_model import ConversationSettings
from app.models.message_model import Message
from app.core.exceptions import AppException, DatabaseException
from app.services.conversation_settings_service import ConversationSettingsService
from app.services.unread_service import UnreadService
from app.services.user_service import UserService
from app.websocket.state import connection_manager
from app.utils.uuid_util import to_uuid


class ConversationService:

    @staticmethod
    async def get_or_create_conversation(
        db: AsyncSession, user1_id: str | uuid.UUID, user2_id: str | uuid.UUID
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
    async def list_conversation_full(db: AsyncSession, user_id: str | uuid.UUID):
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
                ConversationSettings.is_muted,
                ConversationSettings.is_pinned,
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
            .outerjoin(
                ConversationSettings,
                and_(
                    ConversationSettings.conversation_id == Conversation.id,
                    ConversationSettings.user_id == user_uuid,
                ),
            )
            .where(
                or_(
                    Conversation.user1_id == user_uuid,
                    Conversation.user2_id == user_uuid,
                )
            )
            .order_by(
                ConversationSettings.is_pinned.desc().nullslast(),
                last_msg_subq.c.last_time.desc().nullslast(),
            )
        )

        result = await db.execute(stmt)
        return result.all()

    @staticmethod
    async def get_by_id(db: AsyncSession, conversation_id: str | uuid.UUID):
        conversation_uuid = await to_uuid(conversation_id)

        stmt = select(Conversation).where(Conversation.id == conversation_uuid)

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_conversation_info(
        db: AsyncSession, conversation_id: str | uuid.UUID, user_id: str | uuid.UUID
    ):
        user_uuid = await to_uuid(user_id)
        conversation_uuid = await to_uuid(conversation_id)

        conversation = await ConversationService.get_by_id(
            db=db, conversation_id=conversation_id
        )
        if not conversation:
            raise AppException("Conversation not found")

        if conversation.user1_id != user_uuid and conversation.user2_id != user_uuid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed"
            )

        other_user_id = (
            conversation.user2_id
            if conversation.user1_id == user_uuid
            else conversation.user1_id
        )
        other_user = await UserService.get_user_by_id(db=db, user_id=other_user_id)

        unread = await UnreadService.get_unread(
            db=db, conversation_id=conversation_id, user_id=user_uuid
        )

        settings = await ConversationSettingsService.get_or_create(
            db=db, conversation_id=conversation_id, user_id=user_uuid
        )

        query = (
            select(Message)
            .where(Message.conversation_id == conversation_uuid)
            .order_by(Message.sent_at.desc())
            .limit(1)
        )
        result = await db.execute(query)
        last_message = result.scalar_one_or_none()

        return {
            "conversation_id": str(conversation.id),
            "other_user": {
                "id": str(other_user.id),
                "username": other_user.username,
                "email": other_user.email,
                "is_online": str(other_user.id) in connection_manager.active_users,
                "last_seen": (
                    other_user.last_seen.isoformat() if other_user.last_seen else None
                ),
            },
            "unread_count": unread or 0,
            "is_muted": settings.is_muted,
            "is_pinned": settings.is_pinned,
            "last_message": (
                None
                if not last_message
                else {
                    "id": str(last_message.id),
                    "sender_id": str(last_message.sender_id),
                    "content": last_message.content,
                    "sent_at": last_message.sent_at.isoformat(),
                }
            ),
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
        }
