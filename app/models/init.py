from sqlalchemy.orm import declarative_base

Base = declarative_base()

from .user import User
from .achievement import Achievement
from .achievement_translation import AchievementTranslation
from .user_achievement import UserAchievement