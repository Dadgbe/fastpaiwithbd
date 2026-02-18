from pydantic import BaseModel, ConfigDict
from datetime import datetime

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
    achievement: "app.schemas.achievement.AchievementLocalized"