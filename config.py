from pydantic import BaseModel
from pydantic_settings import BaseSettings


class DbSettings(BaseModel):
    url: str = "[ДАННЫЕ УДАЛЕНЫ]"
    echo: bool = False


class Settings(BaseSettings):
    db: DbSettings = DbSettings()


settings = Settings()
