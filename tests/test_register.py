import pytest
from httpx import AsyncClient, ASGITransport

from app.main import create_app
from app.database.connection import get_db
from tests.conftest import TestSessionLocal

app = create_app()

async def override_get_db():
    async with TestSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.mark.asyncio
async def test_register_user(db):
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "tester",
                "email": "tester@example.com",
                "password": "password123"
            }
        )
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "tester"
    assert data["email"] == "tester@example.com"
