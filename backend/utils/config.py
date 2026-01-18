"""
Utility configuration management
"""

import os
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings

# Get backend directory for absolute paths
BACKEND_DIR = Path(__file__).parent.parent.absolute()


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # File Upload Configuration
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", 500000000))  # 500MB
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", str(BACKEND_DIR / "uploads"))
    TEMP_DIR: str = os.getenv("TEMP_DIR", str(BACKEND_DIR / "temp"))
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", str(BACKEND_DIR / "output"))

    # Model Configuration
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")
    SUMMARIZATION_MODEL: str = os.getenv("SUMMARIZATION_MODEL", "facebook/bart-large-cnn")
    MAX_SUMMARY_LENGTH: int = int(os.getenv("MAX_SUMMARY_LENGTH", 500))
    MIN_SUMMARY_LENGTH: int = int(os.getenv("MIN_SUMMARY_LENGTH", 100))

    # Processing Configuration
    NUM_WORKERS: int = int(os.getenv("NUM_WORKERS", 4))
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", 16))
    DEVICE: str = os.getenv("DEVICE", "cpu")

    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./autonotes.db")

    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "./logs/autonotes.log")

    # CORS Configuration
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:5174,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:5174")

    class Config:
        env_file = ".env"
        case_sensitive = True

    def get_allowed_origins(self) -> list:
        """Get list of allowed origins"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
