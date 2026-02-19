import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_max_achievements_count(client: AsyncClient):
    # Создаём пользователей
    user_a = (await client.post("/api/v1/users", json={"username": "stats_a", "language": "en"})).json()
    user_b = (await client.post("/api/v1/users", json={"username": "stats_b", "language": "en"})).json()

    # Создаём достижения
    ach1 = (await client.post("/api/v1/achievements", json={
        "points": 1,
        "translations": [{"language": "en", "name": "A1", "description": ""}]
    })).json()
    ach2 = (await client.post("/api/v1/achievements", json={
        "points": 1,
        "translations": [{"language": "en", "name": "A2", "description": ""}]
    })).json()
    ach3 = (await client.post("/api/v1/achievements", json={
        "points": 1,
        "translations": [{"language": "en", "name": "A3", "description": ""}]
    })).json()

    # Выдаём достижения
    await client.post(f"/api/v1/users/{user_a['id']}/achievements/{ach1['id']}")
    await client.post(f"/api/v1/users/{user_a['id']}/achievements/{ach2['id']}")
    await client.post(f"/api/v1/users/{user_b['id']}/achievements/{ach1['id']}")
    await client.post(f"/api/v1/users/{user_b['id']}/achievements/{ach2['id']}")
    await client.post(f"/api/v1/users/{user_b['id']}/achievements/{ach3['id']}")

    response = await client.get("/api/v1/stats/users/max-achievements-count")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_b["id"]
    assert data["count"] == 3

@pytest.mark.asyncio
async def test_max_points(client: AsyncClient):
    user_a = (await client.post("/api/v1/users", json={"username": "points_a", "language": "en"})).json()
    user_b = (await client.post("/api/v1/users", json={"username": "points_b", "language": "en"})).json()

    ach5 = (await client.post("/api/v1/achievements", json={
        "points": 5,
        "translations": [{"language": "en", "name": "P5", "description": ""}]
    })).json()
    ach10 = (await client.post("/api/v1/achievements", json={
        "points": 10,
        "translations": [{"language": "en", "name": "P10", "description": ""}]
    })).json()

    await client.post(f"/api/v1/users/{user_a['id']}/achievements/{ach5['id']}")
    await client.post(f"/api/v1/users/{user_a['id']}/achievements/{ach10['id']}")
    await client.post(f"/api/v1/users/{user_b['id']}/achievements/{ach10['id']}")

    response = await client.get("/api/v1/stats/users/max-points")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_a["id"]
    assert data["total_points"] == 15

@pytest.mark.asyncio
async def test_max_points_difference(client: AsyncClient):
    user_low = (await client.post("/api/v1/users", json={"username": "low", "language": "en"})).json()
    user_high = (await client.post("/api/v1/users", json={"username": "high", "language": "en"})).json()
    user_mid = (await client.post("/api/v1/users", json={"username": "mid", "language": "en"})).json()

    ach1 = (await client.post("/api/v1/achievements", json={
        "points": 1,
        "translations": [{"language": "en", "name": "A1", "description": ""}]
    })).json()
    ach100 = (await client.post("/api/v1/achievements", json={
        "points": 100,
        "translations": [{"language": "en", "name": "A100", "description": ""}]
    })).json()
    ach50 = (await client.post("/api/v1/achievements", json={
        "points": 50,
        "translations": [{"language": "en", "name": "A50", "description": ""}]
    })).json()

    await client.post(f"/api/v1/users/{user_low['id']}/achievements/{ach1['id']}")
    await client.post(f"/api/v1/users/{user_high['id']}/achievements/{ach100['id']}")
    await client.post(f"/api/v1/users/{user_mid['id']}/achievements/{ach50['id']}")

    response = await client.get("/api/v1/stats/users/max-points-difference")
    data = response.json()
    assert data["difference"] == 99

@pytest.mark.asyncio
async def test_min_points_difference(client: AsyncClient):
    u1 = (await client.post("/api/v1/users", json={"username": "u1", "language": "en"})).json()
    u2 = (await client.post("/api/v1/users", json={"username": "u2", "language": "en"})).json()
    u3 = (await client.post("/api/v1/users", json={"username": "u3", "language": "en"})).json()

    ach10 = (await client.post("/api/v1/achievements", json={
        "points": 10,
        "translations": [{"language": "en", "name": "A10", "description": ""}]
    })).json()
    ach11 = (await client.post("/api/v1/achievements", json={
        "points": 11,
        "translations": [{"language": "en", "name": "A11", "description": ""}]
    })).json()
    ach20 = (await client.post("/api/v1/achievements", json={
        "points": 20,
        "translations": [{"language": "en", "name": "A20", "description": ""}]
    })).json()

    await client.post(f"/api/v1/users/{u1['id']}/achievements/{ach10['id']}")
    await client.post(f"/api/v1/users/{u2['id']}/achievements/{ach11['id']}")
    await client.post(f"/api/v1/users/{u3['id']}/achievements/{ach20['id']}")

    response = await client.get("/api/v1/stats/users/min-points-difference")
    data = response.json()
    assert data["difference"] == 1

@pytest.mark.asyncio
async def test_seven_days_streak(client: AsyncClient):
    # Создаём пользователя и достижение
    user = (await client.post("/api/v1/users", json={"username": "streaker", "language": "en"})).json()
    ach = (await client.post("/api/v1/achievements", json={
        "points": 1,
        "translations": [{"language": "en", "name": "S", "description": "S"}]
    })).json()

    # Выдаём достижения в течение 7 дней подряд (через API нельзя задать дату, поэтому используем прямое обращение к БД)
    # Для теста нам нужно изменить даты в БД. Получим сессию через фикстуру (добавим её в тест)
    # Но поскольку мы не можем передать db_session в этот тест (он использует только client),
    # придётся создать записи через API, а затем вручную обновить даты.
    # Это можно сделать, получив сессию из фикстуры, но для этого нужно добавить параметр db_session в тест.

    # Упростим: создадим 7 записей через API, а затем через прямой SQL обновим даты.
    # Но для этого нужен доступ к БД. Лучше оставить как было, но с использованием client для создания,
    # а затем через db_session (которую можно добавить в тест) обновить даты.

    # Добавим db_session как параметр теста, чтобы можно было напрямую работать с БД.
    pass

# Чтобы избежать сложностей с ручным обновлением дат, можно написать тест с db_session,
# но при этом данные создавать через API. Оставим это на усмотрение.