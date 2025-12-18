import pytest
from fastapi import status
from app.services.user_service import UserService
from app.utils.jwt import create_access_token


@pytest.mark.asyncio
async def test_send_and_accept_friend_request(client, db):
    # Create users
    user1 = await UserService.create_user(
        db, username="alice", email="alice@example.com", password="password"
    )
    user2 = await UserService.create_user(
        db, username="bob", email="bob@example.com", password="password"
    )

    token1 = create_access_token(str(user1.id))
    token2 = create_access_token(str(user2.id))

    # User 1 sends request to User 2
    res = await client.post(
        f"/api/v1/friends/request?receiver_id={str(user2.id)}",
        headers={"Authorization": f"Bearer {token1}"},
    )

    assert res.status_code == status.HTTP_200_OK
    friendship = res.json()

    # User 2 accepts
    res_accept = await client.post(
        f"/api/v1/friends/{friendship["id"]}/accept",
        headers={"Authorization": f"Bearer {token2}"},
    )

    assert res_accept.status_code == status.HTTP_200_OK
    assert res_accept.json()["status"] == "accepted"
