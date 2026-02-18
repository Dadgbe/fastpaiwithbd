from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    APP_NAME: str = "Achievement API"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    model_config = ConfigDict(env_file=".env", extra="ignore")

settings = Settings()