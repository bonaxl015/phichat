import pytest
from app.services.user_service import UserService


@pytest.mark.asyncio
async def test_create_user(db):
    user = await UserService.create_user(
        db, username="testuser", email="test@example.com", password="password123"
    )

    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
