from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).parent
GUARDIAN_PATH = BASE_DIR / "guardian" / "ruBERT_1.0acc"


class DbSettings(BaseModel):
    url: str = "[ДАННЫЕ УДАЛЕНЫ]"
    echo: bool = False


class GuardianSettings(BaseModel):
    path: str = str(GUARDIAN_PATH)


class Settings(BaseSettings):
    db: DbSettings = DbSettings()
    guardian: GuardianSettings = GuardianSettings()


settings = Settings()
