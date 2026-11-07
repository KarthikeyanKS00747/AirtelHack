from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://udyam:udyam_secret@localhost:5432/udyam_digital"

    # Security
    SECRET_KEY: str = "dev-secret-change-in-production-abc123xyz"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # File Upload
    UPLOAD_DIR: str = "../uploads/kyc"
    MAX_FILE_SIZE_MB: int = 10

    # AI Providers (optional)
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    # OCR
    TESSERACT_CMD: Optional[str] = None

    # App
    APP_ENV: str = "development"
    APP_VERSION: str = "1.0.0"
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Dataset reference date (spec: 2026-07-15)
    DATASET_REFERENCE_DATE: str = "2026-07-15"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    @property
    def dataset_reference_date(self):
        from datetime import date
        return date.fromisoformat(self.DATASET_REFERENCE_DATE)


settings = Settings()
