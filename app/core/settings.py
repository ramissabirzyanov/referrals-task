from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """
    Класс для хранения настроек приложения, загружаемых из переменных окружения.
    """
    DATABASE_URL: str
    PRIVATE_KEY_PATH: Path
    PUBLIC_KEY_PATH: Path
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
