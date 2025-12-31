import pytest
from fastapi import status
from app.services.user_service import UserService
from app.services.conversation_service import ConversationService
from app.utils.jwt_util import create_access_token


@pytest.mark.asyncio
async def test_start_conversation(client, db):
    # Create two users
    user1 = await UserService.create_user(
        db, username="alice", email="alice@example.com", password="password"
    )
    user2 = await UserService.create_user(
        db, username="bob", email="bob@example.com", password="password"
    )

    token = create_access_token(str(user1.id))

    res = await client.post(
        f"/api/v1/conversations/start?other_user_id={user2.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == status.HTTP_200_OK
    data = res.json()

    assert data["user1_id"] == str(user1.id) or data["user2_id"] == str(user1.id)
    assert data["user1_id"] == str(user2.id) or data["user2_id"] == str(user2.id)


@pytest.mark.asyncio
async def test_list_conversation(client, db):
    # Create two users
    user1 = await UserService.create_user(
        db, username="john", email="john@example.com", password="password"
    )
    user2 = await UserService.create_user(
        db, username="mark", email="mark@example.com", password="password"
    )

    # Create conversation manually
    await ConversationService.get_or_create_conversation(
        db, user1_id=user1.id, user2_id=user2.id
    )

    token = create_access_token(str(user1.id))

    res = await client.get(
        "/api/v1/conversations", headers={"Authorization": f"Bearer {token}"}
    )

    assert res.status_code == status.HTTP_200_OK
    assert len(res.json()) == 1
