from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # Database
    database_url: str
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"

    # AI APIs
    openai_api_key: Optional[str] = None
    novita_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    default_model: str = "gpt-4"
    image_model: str = "gemini-2.5-flash-image"
    max_tokens: int = 2000

    # n8n
    n8n_webhook_url: Optional[str] = None
    n8n_api_key: Optional[str] = None

    # Environment
    environment: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # 允许额外的环境变量


settings = Settings()
