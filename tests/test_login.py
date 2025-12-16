import pytest
from app.services.user_service import UserService


@pytest.mark.asyncio
async def test_login_success(client, db):
    await UserService.create_user(
        db, username="tester", email="tester@example.com", password="password123"
    )

    response = await client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "tester", "password": "password123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_invalid_creadentials(client, db):
    response = await client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "unknown", "password": "wrongpassword"},
    )

    assert response.status_code == 401
