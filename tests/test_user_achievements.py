import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.user import UserService
from app.services.achievement import AchievementService
from app.services.user_achievement import UserAchievementService
from app.schemas.user import UserCreate
from app.schemas.achievement import AchievementCreate, AchievementTranslationCreate

@pytest.mark.asyncio
async def test_award_achievement(client: AsyncClient, db_session: AsyncSession):
    # Создаём пользователя и достижение
    user = await UserService(db_session).create_user(UserCreate(username="award_user", language="en"))
    ach = await AchievementService(db_session).create_achievement(AchievementCreate(
        points=5,
        translations=[AchievementTranslationCreate(language="en", name="Test", description="Test")]
    ))
    response = await client.post(f"/api/v1/users/{user.id}/achievements/{ach.id}")
    assert response.status_code == 201
    assert response.json()["message"] == "Achievement awarded"

@pytest.mark.asyncio
async def test_award_achievement_user_not_found(client: AsyncClient, db_session: AsyncSession):
    # Создаём достижение
    ach = await AchievementService(db_session).create_achievement(AchievementCreate(
        points=5,
        translations=[AchievementTranslationCreate(language="en", name="Test", description="Test")]
    ))
    response = await client.post(f"/api/v1/users/999999/achievements/{ach.id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

@pytest.mark.asyncio
async def test_get_user_achievements(client: AsyncClient, db_session: AsyncSession):
    # Создаём пользователя и два достижения, выдаём их
    user = await UserService(db_session).create_user(UserCreate(username="achiever", language="en"))
    ach1 = await AchievementService(db_session).create_achievement(AchievementCreate(
        points=10,
        translations=[AchievementTranslationCreate(language="en", name="One", description="First")]
    ))
    ach2 = await AchievementService(db_session).create_achievement(AchievementCreate(
        points=20,
        translations=[AchievementTranslationCreate(language="en", name="Two", description="Second")]
    ))
    ua_svc = UserAchievementService(db_session)
    await ua_svc.award_achievement(user.id, ach1.id)
    await ua_svc.award_achievement(user.id, ach2.id)

    response = await client.get(f"/api/v1/users/{user.id}/achievements?lang=en")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["achievement"]["name"] in ["One", "Two"]
    assert data[1]["achievement"]["points"] in [10, 20]