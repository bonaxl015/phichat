from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.utils.hashing import hash_password, verify_password


class UserService:
    @staticmethod
    async def create_user(db: AsyncSession, username: str, email: str, password: str):
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

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str):
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str):
        query = select(User).where(User.username == username)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def authenticate(db: AsyncSession, username_or_email: str, password: str):
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
