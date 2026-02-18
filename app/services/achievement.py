from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.achievement import Achievement
from app.models.achievement_translation import AchievementTranslation
from app.schemas.achievement import AchievementCreate, AchievementLocalized
from app.models.user import UserLanguage
from typing import List, Optional

class AchievementService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_achievement(self, achievement_id: int) -> Achievement | None:
        return await self.db.get(Achievement, achievement_id)

    async def create_achievement(self, ach_data: AchievementCreate) -> Achievement:
        # Создаём достижение
        achievement = Achievement(points=ach_data.points)
        self.db.add(achievement)
        await self.db.flush()  # чтобы получить id

        # Добавляем переводы
        for tr in ach_data.translations:
            translation = AchievementTranslation(
                achievement_id=achievement.id,
                language=tr.language,
                name=tr.name,
                description=tr.description
            )
            self.db.add(translation)
        await self.db.commit()
        await self.db.refresh(achievement)
        return achievement

    async def get_all_achievements(self, lang: UserLanguage = UserLanguage.en) -> List[AchievementLocalized]:
        stmt = select(Achievement).options(selectinload(Achievement.translations))
        result = await self.db.execute(stmt)
        achievements = result.scalars().all()

        # Для каждого достижения находим перевод на нужный язык (или первый попавшийся)
        localized_list = []
        for ach in achievements:
            translation = next((t for t in ach.translations if t.language == lang), ach.translations[0] if ach.translations else None)
            if translation:
                localized_list.append(AchievementLocalized(
                    id=ach.id,
                    points=ach.points,
                    name=translation.name,
                    description=translation.description
                ))
        return localized_list

    async def get_achievement_localized(self, achievement_id: int, lang: UserLanguage) -> Optional[AchievementLocalized]:
        stmt = select(Achievement).where(Achievement.id == achievement_id).options(selectinload(Achievement.translations))
        result = await self.db.execute(stmt)
        ach = result.scalar_one_or_none()
        if not ach:
            return None
        translation = next((t for t in ach.translations if t.language == lang), ach.translations[0] if ach.translations else None)
        if not translation:
            return None
        return AchievementLocalized(
            id=ach.id,
            points=ach.points,
            name=translation.name,
            description=translation.description
        )