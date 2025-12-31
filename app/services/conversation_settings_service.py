from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.conversation_settings_model import ConversationSettings
from app.utils.uuid_util import to_uuid


class ConversationSettingsService:

    @staticmethod
    async def get_or_create(db: AsyncSession, conversation_id: str, user_id: str):
        conversation_uuid = await to_uuid(conversation_id)
        user_uuid = await to_uuid(user_id)

        stmt = select(ConversationSettings).where(
            ConversationSettings.conversation_id == conversation_uuid,
            ConversationSettings.user_id == user_uuid,
        )

        result = await db.execute(stmt)
        settings = result.scalar_one_or_none()

        if settings:
            return settings

        settings = ConversationSettings(
            conversation_id=conversation_uuid,
            user_id=user_uuid,
            is_muted=False,
            is_pinned=False,
        )

        db.add(settings)
        await db.commit()
        await db.refresh(settings)

        return settings

    @staticmethod
    async def toggle_mute(
        db: AsyncSession, conversation_id: str, user_id: str, mute: bool
    ):
        settings = await ConversationSettingsService.get_or_create(
            db=db, conversation_id=conversation_id, user_id=user_id
        )
        settings.is_muted = mute

        await db.commit()
        await db.refresh(settings)

        return settings

    @staticmethod
    async def toggle_pin(
        db: AsyncSession, conversation_id: str, user_id: str, pin: bool
    ):
        settings = await ConversationSettingsService.get_or_create(
            db=db, conversation_id=conversation_id, user_id=user_id
        )
        settings.is_pinned = pin

        await db.commit()
        await db.refresh(settings)

        return settings
