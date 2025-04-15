from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BET_MAKER_URL: str = "http://bet-maker:8000"
    CALLBACK_RETRIES: int = 3
    CALLBACK_TIMEOUT: int = 5

settings = Settings()