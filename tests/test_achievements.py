import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.achievement import AchievementService
from app.schemas.achievement import AchievementCreate, AchievementTranslationCreate

@pytest.mark.asyncio
async def test_create_achievement(client: AsyncClient):
    payload = {
        "points": 10,
        "translations": [
            {"language": "ru", "name": "Тест", "description": "Описание"},
            {"language": "en", "name": "Test", "description": "Description"}
        ]
    }
    response = await client.post("/api/v1/achievements", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["points"] == 10
    assert len(data["translations"]) == 2
    assert data["translations"][0]["language"] in ["ru", "en"]

@pytest.mark.asyncio
async def test_create_achievement_invalid_points(client: AsyncClient):
    payload = {
        "points": -5,
        "translations": [{"language": "ru", "name": "Bad", "description": "Bad"}]
    }
    response = await client.post("/api/v1/achievements", json=payload)
    assert response.status_code == 422  # validation error

@pytest.mark.asyncio
async def test_get_all_achievements(client: AsyncClient, db_session: AsyncSession):
    # Создаём два достижения
    svc = AchievementService(db_session)
    await svc.create_achievement(AchievementCreate(
        points=5,
        translations=[AchievementTranslationCreate(language="ru", name="Ach1", description="Desc1")]
    ))
    await svc.create_achievement(AchievementCreate(
        points=10,
        translations=[AchievementTranslationCreate(language="en", name="Ach2", description="Desc2")]
    ))
    response = await client.get("/api/v1/achievements")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2