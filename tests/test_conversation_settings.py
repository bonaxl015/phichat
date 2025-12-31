import pytest
from fastapi import status
from app.services.user_service import UserService
from app.utils.jwt_util import create_access_token


@pytest.mark.asyncio
async def test_pin_conversation(client, db):
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

    res = await client.post(
        f"/api/v1/conversations/{conv_data["id"]}/pin",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == status.HTTP_200_OK
    data = res.json()

    assert data["pinned"]


@pytest.mark.asyncio
async def test_unpin_conversation(client, db):
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

    res = await client.post(
        f"/api/v1/conversations/{conv_data["id"]}/unpin",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == status.HTTP_200_OK
    data = res.json()

    assert not data["pinned"]


@pytest.mark.asyncio
async def test_mute_conversation(client, db):
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

    res = await client.post(
        f"/api/v1/conversations/{conv_data["id"]}/mute",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == status.HTTP_200_OK
    data = res.json()

    assert data["muted"]


@pytest.mark.asyncio
async def test_unmute_conversation(client, db):
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

    res = await client.post(
        f"/api/v1/conversations/{conv_data["id"]}/unmute",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == status.HTTP_200_OK
    data = res.json()

    assert not data["muted"]
