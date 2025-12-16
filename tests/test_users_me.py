import pytest
from app.services.user_service import UserService
from app.utils.jwt import create_access_token


@pytest.mark.asyncio
async def test_get_me(client, db):
    # Create a test user
    user = await UserService.create_user(
        db, username="meuser", email="me@example.com", password="password"
    )

    token = create_access_token(str(user.id))

    response = await client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == str(user.id)
    assert data["username"] == "meuser"
    assert data["email"] == "me@example.com"


@pytest.mark.asyncio
async def test_get_me_unauthorized(client):
    response = await client.get("/api/v1/users/me")

    assert response.status_code == 401
