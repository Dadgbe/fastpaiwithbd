from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.achievement import AchievementService
from app.schemas.achievement import Achievement, AchievementCreate, AchievementLocalized
from app.models.user import UserLanguage
from typing import List

router = APIRouter(prefix="/achievements", tags=["achievements"])

@router.get("", response_model=List[AchievementLocalized])
async def get_achievements(
    lang: UserLanguage = UserLanguage.en,
    db: AsyncSession = Depends(get_db)
):
    return await AchievementService(db).get_all_achievements(lang)

@router.get("/all", response_model=List[Achievement])
async def get_all_achievements_full(db: AsyncSession = Depends(get_db)):
    return await AchievementService(db).get_all_achievements_full()

@router.post("", response_model=Achievement, status_code=status.HTTP_201_CREATED)
async def create_achievement(
    achievement_data: AchievementCreate,
    db: AsyncSession = Depends(get_db)
):
    return await AchievementService(db).create_achievement(achievement_data)