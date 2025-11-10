"""
Ethio Bingo - Configuration Management
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Telegram Bot
    telegram_bot_token: str
    telegram_webhook_url: Optional[str] = None
    
    # Database
    database_url: str
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # Application
    secret_key: str
    app_env: str = "development"
    debug: bool = False
    
    # Game Configuration
    max_players_per_room: int = 100
    default_draw_interval: int = 5
    auto_mark_enabled: bool = True
    
    # Security
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
