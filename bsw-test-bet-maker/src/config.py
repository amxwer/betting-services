from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    redis_url: str = "redis://redis:6379"
    line_provider_url: str = "http://line-provider:8000"
    cache_duration_seconds: int = 10

settings = Settings()