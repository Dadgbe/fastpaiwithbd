from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.stats import StatsService
from app.schemas.stats import UserStats, UserPair
from typing import List

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/users/max-achievements-count", response_model=UserStats)
async def max_achievements_count(db: AsyncSession = Depends(get_db)):
    return await StatsService(db).get_user_with_max_achievements_count()

@router.get("/users/max-points", response_model=UserStats)
async def max_points(db: AsyncSession = Depends(get_db)):
    return await StatsService(db).get_user_with_max_points()

@router.get("/users/max-points-difference", response_model=UserPair)
async def max_points_difference(db: AsyncSession = Depends(get_db)):
    return await StatsService(db).get_users_with_max_points_difference()

@router.get("/users/min-points-difference", response_model=UserPair)
async def min_points_difference(db: AsyncSession = Depends(get_db)):
    return await StatsService(db).get_users_with_min_points_difference()

@router.get("/users/7-days-streak", response_model=List[int])
async def seven_days_streak(db: AsyncSession = Depends(get_db)):
    return await StatsService(db).get_users_with_7day_streak()