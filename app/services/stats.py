from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, text, Integer, Float
from sqlalchemy.sql import label
from app.models.user import User
from app.models.user_achievement import UserAchievement
from app.models.achievement import Achievement
from app.schemas.stats import UserStats, UserPair
from typing import List
import logging

logger = logging.getLogger(__name__)

class StatsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_with_max_achievements_count(self) -> UserStats:
        # JOIN user_achievements, group by user, count, order desc, limit 1
        stmt = (
            select(
                User.id,
                User.username,
                func.count(UserAchievement.id).label("count")
            )
            .join(UserAchievement, User.id == UserAchievement.user_id)
            .group_by(User.id)
            .order_by(func.count(UserAchievement.id).desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        row = result.first()
        if not row:
            # Если нет достижений – вернуть пустую статистику или поднять исключение
            return UserStats(user_id=0, username="", count=0, total_points=0)
        return UserStats(user_id=row.id, username=row.username, count=row.count, total_points=0)

    async def get_user_with_max_points(self) -> UserStats:
        # Сумма баллов по пользователю через JOIN с achievements
        stmt = (
            select(
                User.id,
                User.username,
                func.coalesce(func.sum(Achievement.points), 0).label("total_points")
            )
            .outerjoin(UserAchievement, User.id == UserAchievement.user_id)
            .outerjoin(Achievement, UserAchievement.achievement_id == Achievement.id)
            .group_by(User.id)
            .order_by(func.sum(Achievement.points).desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        row = result.first()
        if not row:
            return UserStats(user_id=0, username="", count=0, total_points=0)
        return UserStats(user_id=row.id, username=row.username, count=0, total_points=row.total_points)

    async def get_users_with_max_points_difference(self) -> UserPair:
        # Получаем всех пользователей с суммами баллов
        stmt = (
            select(
                User.id,
                User.username,
                func.coalesce(func.sum(Achievement.points), 0).label("total_points")
            )
            .outerjoin(UserAchievement, User.id == UserAchievement.user_id)
            .outerjoin(Achievement, UserAchievement.achievement_id == Achievement.id)
            .group_by(User.id)
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        if len(rows) < 2:
            # Недостаточно пользователей для разности
            return UserPair(user1_id=0, user1_username="", user2_id=0, user2_username="", difference=0)
        # Сортируем по сумме
        sorted_rows = sorted(rows, key=lambda r: r.total_points)
        min_user = sorted_rows[0]
        max_user = sorted_rows[-1]
        return UserPair(
            user1_id=min_user.id,
            user1_username=min_user.username,
            user2_id=max_user.id,
            user2_username=max_user.username,
            difference=max_user.total_points - min_user.total_points
        )

    async def get_users_with_min_points_difference(self) -> UserPair:
        # Аналогично, ищем минимальную разницу между соседями
        stmt = (
            select(
                User.id,
                User.username,
                func.coalesce(func.sum(Achievement.points), 0).label("total_points")
            )
            .outerjoin(UserAchievement, User.id == UserAchievement.user_id)
            .outerjoin(Achievement, UserAchievement.achievement_id == Achievement.id)
            .group_by(User.id)
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        if len(rows) < 2:
            return UserPair(user1_id=0, user1_username="", user2_id=0, user2_username="", difference=0)
        sorted_rows = sorted(rows, key=lambda r: r.total_points)
        min_diff = float('inf')
        best_pair = None
        for i in range(len(sorted_rows)-1):
            diff = sorted_rows[i+1].total_points - sorted_rows[i].total_points
            if diff < min_diff:
                min_diff = diff
                best_pair = (sorted_rows[i], sorted_rows[i+1])
        if best_pair:
            u1, u2 = best_pair
            return UserPair(
                user1_id=u1.id, user1_username=u1.username,
                user2_id=u2.id, user2_username=u2.username,
                difference=min_diff
            )
        # fallback
        return UserPair(user1_id=0, user1_username="", user2_id=0, user2_username="", difference=0)

    async def get_users_with_7day_streak(self) -> List[int]:
        # Используем оконные функции для поиска непрерывных последовательностей дат
        query = text("""
            WITH daily AS (
                SELECT DISTINCT user_id, DATE(awarded_at) as award_date
                FROM user_achievements
            ),
            numbered AS (
                SELECT user_id, award_date,
                       award_date - (row_number() OVER (PARTITION BY user_id ORDER BY award_date))::int as grp
                FROM daily
            ),
            streaks AS (
                SELECT user_id, grp, COUNT(*) as streak_days
                FROM numbered
                GROUP BY user_id, grp
            )
            SELECT DISTINCT user_id
            FROM streaks
            WHERE streak_days >= 7
        """)
        result = await self.db.execute(query)
        rows = result.all()
        return [row[0] for row in rows]