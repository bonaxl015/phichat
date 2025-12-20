from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.message import Message, MessageStatus
from app.models.conversation import Conversation
from app.core.exceptions import AppException, DatabaseException
from app.utils.uuid import to_uuid


class MessageService:

    @staticmethod
    async def can_user_access_conversation(
        db: AsyncSession, conversation: Conversation, user_id: str
    ):
        user_uuid = await to_uuid(user_id)
        return conversation.user1_id == user_uuid or conversation.user2_id == user_uuid

    @staticmethod
    async def send_message(
        db: AsyncSession, conversation: Conversation, sender_id: str, content: str
    ):
        try:
            conv_uuid = await to_uuid(conversation.id)
            conv_user1_uuid = await to_uuid(conversation.user1_id)
            conv_user2_uuid = await to_uuid(conversation.user2_id)
            sender_uuid = await to_uuid(sender_id)
            receiver_uuid = (
                conv_user1_uuid if conv_user2_uuid == sender_uuid else conv_user2_uuid
            )

            if not content or content.strip() == "":
                raise AppException("Message content cannot be empty")

            msg = Message(
                conversation_id=conv_uuid,
                sender_id=sender_uuid,
                receiver_id=receiver_uuid,
                content=content,
                status=MessageStatus.sent,
            )

            db.add(msg)
            await db.commit()
            await db.refresh(msg)
            return msg
        except AppException:
            raise
        except Exception as e:
            raise DatabaseException(str(e))

    @staticmethod
    async def list_messages(db: AsyncSession, conv_id: str, limit: int = 50):
        conv_uuid = await to_uuid(conv_id)

        stmt = (
            select(Message)
            .where(Message.conversation_id == conv_uuid)
            .order_by(Message.sent_at)
            .limit(limit)
        )

        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def mark_delivered(db: AsyncSession, message_id: str, user_id: str):
        try:
            message_uuid = await to_uuid(message_id)
            user_uuid = await to_uuid(user_id)

            stmt = select(Message).where(Message.id == message_uuid)
            result = await db.execute(stmt)
            msg = result.scalar_one_or_none()

            if not msg:
                raise AppException("Message not found")

            if msg.receiver_id != user_uuid:
                raise AppException("Not allowed")

            msg.status = MessageStatus.delivered
            msg.delivered_at = datetime.now(UTC)

            await db.commit()
            await db.refresh(msg)
            return msg
        except AppException:
            raise
        except Exception as e:
            raise DatabaseException(str(e))

    @staticmethod
    async def mark_read(db: AsyncSession, message_id: str, user_id: str):
        try:
            message_uuid = await to_uuid(message_id)
            user_uuid = await to_uuid(user_id)

            stmt = select(Message).where(Message.id == message_uuid)
            result = await db.execute(stmt)
            msg = result.scalar_one_or_none()

            if not msg:
                raise AppException("Message not found")

            if msg.receiver_id != user_uuid:
                raise AppException("Not allowed")

            msg.status = MessageStatus.read
            msg.read_at = datetime.now(UTC)

            await db.commit()
            await db.refresh(msg)
            return msg
        except AppException:
            raise
        except Exception as e:
            raise DatabaseException(str(e))
