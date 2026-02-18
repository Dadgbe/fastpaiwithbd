from sqlalchemy import Column, Integer, String, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.models.base import Base 

class UserLanguage(str, enum.Enum):
    ru = "ru"
    en = "en"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    language = Column(SQLEnum(UserLanguage), default=UserLanguage.en, nullable=False)

    achievements = relationship("UserAchievement", back_populates="user")