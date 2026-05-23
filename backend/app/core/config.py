from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Uygulama
    APP_NAME: str = "Tarım Yönetim Sistemi"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Veritabanı
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    # Hava durumu
    OPENWEATHERMAP_API_KEY: str = ""

    # AI servisi
    AI_SERVICE_URL: str = "http://ai-service:8001"

    # Depolama
    STORAGE_BACKEND: str = "local"
    MEDIA_ROOT: str = "./media"


settings = Settings()
