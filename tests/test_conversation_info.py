import pytest
from fastapi import status
from app.services.user_service import UserService
from app.utils.jwt import create_access_token


@pytest.mark.asyncio
async def test_conversation_info(client, db):
    # Create two users
    user1 = await UserService.create_user(
        db, username="alice", email="alice@example.com", password="password"
    )
    user2 = await UserService.create_user(
        db, username="bob", email="bob@example.com", password="password"
    )

    token = create_access_token(str(user1.id))

    conv = await client.post(
        f"/api/v1/conversations/start?other_user_id={user2.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    conv_data = conv.json()

    res = await client.get(
        f"/api/v1/conversations/{conv_data["id"]}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == status.HTTP_200_OK
    data = res.json()

    assert data["conversation_id"] == str(conv_data["id"])
    assert data["other_user"]["id"] == str(user2.id)
    assert data["unread_count"] == 0
    assert not data["is_muted"]
    assert not data["is_pinned"]
