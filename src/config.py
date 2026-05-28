"""
Application configuration management for multiple environments
Supports: local, docker, minikube
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Configuration settings for the application"""

    # Application
    APP_NAME: str = "Habit Tracker"
    APP_ENV: str = os.getenv("APP_ENV", "local")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Database
    DATABASE_URL: str
    DB_HOST: str
    DB_USER: str = "user"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "habits"
    DB_PORT: int = 5432

    # AWS/S3
    AWS_ENDPOINT_URL: str
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = "test"
    AWS_SECRET_ACCESS_KEY: str = "test"
    AWS_S3_BUCKET: str = "habit-tracker"

    # JWT/Auth
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 24 * 60

    # API Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = False

    # Monitoring
    JAEGER_HOST: str
    JAEGER_PORT: int = 6831
    ENABLE_TRACING: bool = True

    # Frontend URLs (for CORS, redirects, etc.)
    FRONTEND_URL: str = "http://localhost:8001"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


def get_config_file() -> str:
    """Get the appropriate .env file based on APP_ENV"""
    app_env = os.getenv("APP_ENV", "local")

    env_files = {
        "local": ".env.local",
        "docker": ".env.docker",
        "minikube": ".env.minikube"
    }

    return env_files.get(app_env, ".env")


# Load settings
settings = get_settings()
