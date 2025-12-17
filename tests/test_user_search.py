import pytest
from app.services.user_service import UserService
from app.utils.jwt import create_access_token


@pytest.mark.asyncio
async def test_user_search(client, db):
    # Create requesting user
    user1 = await UserService.create_user(
        db, username="john", email="john@example.com", password="johnpassword"
    )

    # Create another user
    user2 = await UserService.create_user(
        db, username="jane", email="jane@example.com", password="janepassword"
    )

    token = create_access_token(str(user1.id))

    response = await client.get(
        "/api/v1/users/search?q=ja", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["username"] == user2.username
    assert data[0]["email"] == user2.email


@pytest.mark.asyncio
async def test_user_search_empty_query(client, db):
    user = await UserService.create_user(
        db, username="tester", email="tester@example.com", password="testerpassword"
    )

    token = create_access_token(str(user.id))

    response = await client.get(
        "/api/v1/users/search?q=", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400
    assert "error" in response.json()
