from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_

from app.models.friendship import Friendship, FriendshipStatus
from app.core.exceptions import AppException, DatabaseException
from app.utils.uuid import to_uuid


class FriendService:

    @staticmethod
    async def send_request(db: AsyncSession, requester_id: str, receiver_id: str):
        try:
            requester_uuid = await to_uuid(requester_id)
            receiver_uuid = await to_uuid(receiver_id)

            if requester_uuid == receiver_uuid:
                raise AppException("You cannot add yourself as a friend")

            # Check for existing relations
            stmt = select(Friendship).where(
                or_(
                    and_(
                        Friendship.requester_id == requester_uuid,
                        Friendship.receiver_id == receiver_uuid,
                    ),
                    and_(
                        Friendship.requester_id == receiver_uuid,
                        Friendship.receiver_id == requester_uuid,
                    ),
                )
            )

            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                raise AppException("Friend requested or you are already friends")

            friendship = Friendship(
                requester_id=requester_uuid,
                receiver_id=receiver_uuid,
                status=FriendshipStatus.pending,
            )

            db.add(friendship)
            await db.commit()
            await db.refresh(friendship)
            return friendship
        except AppException:
            raise
        except Exception as e:
            raise DatabaseException(str(e))

    @staticmethod
    async def accept_request(db: AsyncSession, friendship_id: str, user_id: str):
        try:
            friendship_uuid = await to_uuid(friendship_id)
            user_uuid = await to_uuid(user_id)

            stmt = select(Friendship).where(Friendship.id == friendship_uuid)
            result = await db.execute(stmt)
            friendship = result.scalar_one_or_none()

            if not friendship:
                raise AppException("Friend request not found")

            if friendship.receiver_id != user_uuid:
                raise AppException("You cannot accept this friend request")

            friendship.status = FriendshipStatus.accepted
            await db.commit()
            await db.refresh(friendship)

            return friendship
        except AppException:
            raise
        except Exception as e:
            raise DatabaseException(str(e))

    @staticmethod
    async def reject_request(db: AsyncSession, friendship_id: str, user_id: str):
        try:
            friendship_uuid = await to_uuid(friendship_id)
            user_uuid = await to_uuid(user_id)

            stmt = select(Friendship).where(Friendship.id == friendship_uuid)
            result = await db.execute(stmt)
            friendship = result.scalar_one_or_none()

            if not friendship:
                raise AppException("Friend request not found")

            if friendship.receiver_id != user_uuid:
                raise AppException("You cannot reject this friend request")

            friendship.status = FriendshipStatus.rejected
            await db.commit()
            await db.refresh(friendship)

            return friendship
        except AppException:
            raise
        except Exception as e:
            raise DatabaseException(str(e))

    @staticmethod
    async def list_friends(db: AsyncSession, user_id: str):
        user_uuid = await to_uuid(user_id)

        stmt = select(Friendship).where(
            and_(
                Friendship.status == FriendshipStatus.accepted,
                or_(
                    Friendship.requester_id == user_uuid,
                    Friendship.receiver_id == user_uuid,
                ),
            )
        )

        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def list_pending(db: AsyncSession, user_id: str):
        user_uuid = await to_uuid(user_id)

        stmt = select(Friendship).where(
            and_(
                Friendship.status == FriendshipStatus.pending,
                Friendship.receiver_id == user_uuid,
            )
        )

        result = await db.execute(stmt)
        return result.scalars().all()
