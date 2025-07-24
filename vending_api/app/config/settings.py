from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://username:password@localhost:5432/uharvest_vending")
    database_url_sync: str = os.getenv("DATABASE_URL_SYNC", "postgresql://username:password@localhost:5432/uharvest_vending")
    
    # Server
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    reload: bool = os.getenv("RELOAD", "True").lower() == "true"
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # CORS
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ]
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Database Pool
    db_pool_size: int = int(os.getenv("DB_POOL_SIZE", "5"))
    db_max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    db_pool_timeout: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    db_pool_recycle: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    
    # Machine Configuration
    multi_machine_mode: bool = os.getenv("MULTI_MACHINE_MODE", "false").lower() == "true"
    auto_register_machine: bool = os.getenv("AUTO_REGISTER_MACHINE", "false").lower() == "true"
    default_cups_qty: int = int(os.getenv("DEFAULT_CUPS_QTY", "100"))
    default_bowls_qty: int = int(os.getenv("DEFAULT_BOWLS_QTY", "50"))
    default_napkins_qty: int = int(os.getenv("DEFAULT_NAPKINS_QTY", "200"))
    default_utensils_qty: int = int(os.getenv("DEFAULT_UTENSILS_QTY", "100"))
    machine_uuid: str = os.getenv("MACHINE_UUID", "")
    machine_name: str = os.getenv("MACHINE_NAME", "Urban Harvest VM")
    machine_location: str = os.getenv("MACHINE_LOCATION", "Default Location")
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Allow extra fields from .env without validation errors

settings = Settings()
