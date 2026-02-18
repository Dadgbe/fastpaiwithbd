from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models.user import UserLanguage

class AchievementTranslation(Base):
    __tablename__ = "achievement_translations"

    id = Column(Integer, primary_key=True, index=True)
    achievement_id = Column(Integer, ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False)
    language = Column(SQLEnum(UserLanguage), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)

    achievement = relationship("Achievement", back_populates="translations")