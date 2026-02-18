from pydantic import BaseModel, ConfigDict
from app.models.user import UserLanguage

class UserBase(BaseModel):
    username: str
    language: UserLanguage = UserLanguage.en

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)