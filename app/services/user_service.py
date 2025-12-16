from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.utils.hashing import hash_password


class UserService:
    @staticmethod
    async def create_user(db: AsyncSession, username: str, email: str, password: str):
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
