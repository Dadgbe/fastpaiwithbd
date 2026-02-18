from pydantic import BaseModel, ConfigDict, field_validator
from typing import List, Optional
from app.models.user import UserLanguage

class AchievementTranslationBase(BaseModel):
    language: UserLanguage
    name: str
    description: str

class AchievementTranslationCreate(AchievementTranslationBase):
    pass

class AchievementTranslation(AchievementTranslationBase):
    id: int
    achievement_id: int
    model_config = ConfigDict(from_attributes=True)

class AchievementBase(BaseModel):
    points: int

    @field_validator('points')
    def points_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('points must be positive')
        return v

class AchievementCreate(AchievementBase):
    translations: List[AchievementTranslationCreate]  # минимум один перевод

class Achievement(AchievementBase):
    id: int
    translations: List[AchievementTranslation] = []
    model_config = ConfigDict(from_attributes=True)

# Для ответа на конкретном языке
class AchievementLocalized(BaseModel):
    id: int
    points: int
    name: str
    description: str