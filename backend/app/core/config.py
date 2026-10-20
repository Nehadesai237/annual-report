"""
Application configuration settings
"""

from pydantic_settings import BaseSettings
from pydantic import validator
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Annual Report Portal"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "annual_report"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: str = "*"  # Allow all origins for development
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse CORS origins from string to list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: str = "image/jpeg,image/png,image/gif,image/webp"
    UPLOAD_DIR: str = "uploads"
    
    # ML Configuration
    ML_MODEL_PATH: str = "./ml/models/model.h5"
    ML_THRESHOLD: float = 0.6
    ML_ENABLED: bool = True
    
    # Email (Optional)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    @validator('SMTP_PORT', pre=True)
    def parse_smtp_port(cls, v):
        if v == '' or v is None:
            return None
        return int(v)
    
    # Redis (for background tasks)
    REDIS_URL: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

# Create settings instance
settings = Settings()
