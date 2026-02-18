from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base import Base

class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    points = Column(Integer, nullable=False)  # положительное число – проверка на уровне приложения
    # Переводы хранятся в отдельной таблице
    translations = relationship("AchievementTranslation", back_populates="achievement", cascade="all, delete-orphan")
    user_achievements = relationship("UserAchievement", back_populates="achievement")