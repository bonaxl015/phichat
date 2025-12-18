from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.message import Message, MessageStatus
from app.core.exceptions import AppException, DatabaseException
from app.utils.uuid import to_uuid


class MessageService:

    @staticmethod
    async def send_message(
        db: AsyncSession, conv_id: str, sender_id: str, receiver_id: str, content: str
    ):
        try:
            conv_uuid = await to_uuid(conv_id)
            sender_uuid = await to_uuid(sender_id)
            receiver_uuid = await to_uuid(receiver_id)

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
