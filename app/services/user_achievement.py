
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, and_
from app.models.user_achievement import UserAchievement
from app.schemas.user_achievement import UserAchievementCreate

class UserAchievementService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def award_achievement(self, user_id: int, achievement_id: int) -> UserAchievement:
        # Проверка на уже существующее? По заданию не запрещено выдавать повторно.
        # Будем выдавать, создавая новую запись.
        ua = UserAchievement(user_id=user_id, achievement_id=achievement_id)
        self.db.add(ua)
        await self.db.commit()
        await self.db.refresh(ua)
        return ua

    async def get_user_achievements(self, user_id: int) -> list[UserAchievement]:
        stmt = select(UserAchievement).where(UserAchievement.user_id == user_id).order_by(UserAchievement.awarded_at)
        result = await self.db.execute(stmt)
        return result.scalars().all()