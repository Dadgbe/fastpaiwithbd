from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, ConfigDict
# Добавляем прямой импорт нужного класса
from app.schemas.achievement import AchievementLocalized

class UserAchievementBase(BaseModel):
    user_id: int
    achievement_id: int

class UserAchievementCreate(UserAchievementBase):
    pass

class UserAchievement(UserAchievementBase):
    id: int
    awarded_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Расширенный ответ с локализованным достижением
class UserAchievementWithDetails(BaseModel):
    awarded_at: datetime
    achievement: AchievementLocalized  # теперь тип определён