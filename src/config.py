"""
Application configuration management for multiple environments
Supports: local, docker, minikube
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache
import os

# Determine which .env file to load based on APP_ENV
app_env = os.getenv("APP_ENV", "local")
env_file_map = {
    "local": ".env.local",
    "docker": ".env.docker",
    "minikube": ".env.minikube"
}
env_file = env_file_map.get(app_env, ".env.local")


class Settings(BaseSettings):
    """Configuration settings for the application"""

    # Application
    APP_NAME: str = "Habit Tracker"
    APP_ENV: str = app_env
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
    API_INTERNAL_URL: str = "http://localhost:8000"
    API_EXTERNAL_URL: str = "http://localhost:8001"

    # Frontend access to API (for nginx proxy)
    API_URL: str = "http://localhost:8000"

    # Monitoring
    JAEGER_HOST: str
    JAEGER_PORT: int = 6831
    ENABLE_TRACING: bool = True

    # Frontend URLs (for CORS, redirects, etc.)
    FRONTEND_URL: str = "http://localhost:8001"

    # Service URLs for monitoring dashboard
    PROMETHEUS_URL: str = "http://prometheus:9090"
    GRAFANA_URL: str = "http://grafana:3000"
    JAEGER_URL: str = "http://jaeger:16686"
    S3_URL: str = "http://localstack:4566"
    ARGOCD_URL: str = "http://argocd:8080"

    @field_validator('API_RELOAD', 'ENABLE_TRACING', mode='before')
    @classmethod
    def parse_bool_string(cls, v):
        """Convert string boolean values to bool-compatible"""
        if isinstance(v, str):
            return v.lower() in ('true', '1', 'yes', 'on')
        return v

    class Config:
        env_file = env_file
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Load settings
settings = get_settings()

print(f"[CONFIG] Loaded settings from: {env_file} (APP_ENV={app_env})", flush=True)
