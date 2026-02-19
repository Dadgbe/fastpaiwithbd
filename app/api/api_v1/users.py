from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.user import UserService
from app.services.achievement import AchievementService
from app.services.user_achievement import UserAchievementService
from app.schemas.user import User, UserCreate
from app.schemas.user_achievement import UserAchievementWithDetails
from app.models.user import UserLanguage
from typing import List

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await UserService(db).get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("", response_model=List[User])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    users = await UserService(db).get_all_users()
    return users


@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await UserService(db).create_user(user_data)

@router.post("/{user_id}/achievements/{achievement_id}", status_code=status.HTTP_201_CREATED)
async def award_achievement(user_id: int, achievement_id: int, db: AsyncSession = Depends(get_db)):
    # Проверка существования пользователя и достижения
    user = await UserService(db).get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    ach = await AchievementService(db).get_achievement(achievement_id)
    if not ach:
        raise HTTPException(status_code=404, detail="Achievement not found")
    await UserAchievementService(db).award_achievement(user_id, achievement_id)
    return {"message": "Achievement awarded"}

@router.get("/{user_id}/achievements", response_model=List[UserAchievementWithDetails])
async def get_user_achievements(
    user_id: int,
    lang: UserLanguage = None,
    db: AsyncSession = Depends(get_db)
):
    user = await UserService(db).get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Если язык не передан, используем язык пользователя
    target_lang = lang or user.language
    user_achievements = await UserAchievementService(db).get_user_achievements(user_id)
    result = []
    for ua in user_achievements:
        loc_ach = await AchievementService(db).get_achievement_localized(ua.achievement_id, target_lang)
        if loc_ach:
            result.append(UserAchievementWithDetails(
                awarded_at=ua.awarded_at,
                achievement=loc_ach
            ))
    return result