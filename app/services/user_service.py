from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, or_

from app.models.user_model import User
from app.utils.hashing_util import hash_password, verify_password
from app.core.exceptions import DatabaseException, AppException
from app.utils.uuid_util import to_uuid


class UserService:

    @staticmethod
    async def create_user(db: AsyncSession, username: str, email: str, password: str):
        try:
            # Check if email is taken
            existing_email = await UserService.get_user_by_email(db, email=email)
            if existing_email:
                raise ValueError("Email already registered")

            # Check if username is taken
            existing_username = await UserService.get_user_by_username(
                db, username=username
            )
            if existing_username:
                raise ValueError("Username already taken")

            hashed = hash_password(password)
            user = User(username=username, email=email, hashed_password=hashed)

            db.add(user)
            await db.commit()
            await db.refresh(user)
            return user
        except SQLAlchemyError as e:
            DatabaseException(str(e))

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str):
        try:
            query = select(User).where(User.email == email)
            result = await db.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            DatabaseException(str(e))

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str):
        try:
            query = select(User).where(User.username == username)
            result = await db.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            DatabaseException(str(e))

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str):
        user_uuid = await to_uuid(user_id)

        try:
            query = select(User).where(User.id == user_uuid)
            result = await db.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            DatabaseException(str(e))

    @staticmethod
    async def authenticate(db: AsyncSession, username_or_email: str, password: str):
        try:
            query = select(User).where(
                (User.username == username_or_email) | (User.email == username_or_email)
            )
            result = await db.execute(query)
            user = result.scalar_one_or_none()

            if not user:
                return None

            if not verify_password(password, user.hashed_password):
                return None

            return user
        except SQLAlchemyError as e:
            DatabaseException(str(e))

    @staticmethod
    async def search_users(
        db: AsyncSession, query: str, exclude_user_id: str, limit: int = 20
    ):
        try:
            if not query or len(query.strip()) == 0:
                raise AppException("Search query cannot be empty")

            stmt = (
                select(User)
                .where(
                    or_(
                        User.username.ilike(f"%{query}%"),
                        User.email.ilike(f"%{query}%"),
                    ),
                    User.id != exclude_user_id,
                )
                .limit(limit)
            )

            result = await db.execute(stmt)
            return result.scalars().all()
        except SQLAlchemyError as e:
            DatabaseException(str(e))
