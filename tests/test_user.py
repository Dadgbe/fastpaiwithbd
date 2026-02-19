import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.user import UserService
from app.schemas.user import UserCreate

@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    response = await client.post("/api/v1/users", json={"username": "testuser", "language": "en"})
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["language"] == "en"
    assert "id" in data

@pytest.mark.asyncio
async def test_create_duplicate_user(client: AsyncClient, db_session: AsyncSession):
    # Создаём первого пользователя
    user_data = UserCreate(username="duplicate", language="en")
    await UserService(db_session).create_user(user_data)
    # Пытаемся создать с тем же username
    response = await client.post("/api/v1/users", json={"username": "duplicate", "language": "en"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"

@pytest.mark.asyncio
async def test_get_user(client: AsyncClient, db_session: AsyncSession):
    # Создаём пользователя через сервис
    user = await UserService(db_session).create_user(UserCreate(username="getme", language="ru"))
    response = await client.get(f"/api/v1/users/{user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "getme"
    assert data["language"] == "ru"

@pytest.mark.asyncio
async def test_get_user_not_found(client: AsyncClient):
    response = await client.get("/api/v1/users/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

@pytest.mark.asyncio
async def test_get_all_users(client: AsyncClient, db_session: AsyncSession):
    # Создаём двух пользователей
    await UserService(db_session).create_user(UserCreate(username="user1", language="en"))
    await UserService(db_session).create_user(UserCreate(username="user2", language="ru"))
    response = await client.get("/api/v1/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    usernames = [u["username"] for u in data]
    assert "user1" in usernames
    assert "user2" in usernames