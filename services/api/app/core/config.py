"""
Configuration settings for the API service
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Configuration
    APP_NAME: str = "AI File Cleanup API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Database Configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "prisma://accelerate.prisma-data.net/?api_key=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGlfa2V5X2lkIjoiN2I5ZGU3YzEtY2M4OC00ZDNmLWFmYjItNzFlOTJjZGZkMDhhIiwidGVuYW50X2lkIjoiZWZkZDQ3MzE1OGYxOTFhYTZiZjUzNGVlZGExNjFjNzc0MzllNGE5ODk5YzcwNzhmYTI1ODJlOTY2ZDY4NzFjMCIsImludGVybmFsX3NlY3JldCI6ImVkYTc3NmNiLTk5NDUtNGI3Zi05NDMzLWJkM2I0NGVlNTJlMiJ9.BaF0Qiq7LhLgFm0r5RJmTHHOLggfaLjtTu0HYtTvkVs"
    )
    PRISMA_ACCELERATE_API_KEY: str = os.getenv(
        "PRISMA_ACCELERATE_API_KEY",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGlfa2V5X2lkIjoiN2I5ZGU3YzEtY2M4OC00ZDNmLWFmYjItNzFlOTJjZGZkMDhhIiwidGVuYW50X2lkIjoiZWZkZDQ3MzE1OGYxOTFhYTZiZjUzNGVlZGExNjFjNzc0MzllNGE5ODk5YzcwNzhmYTI1ODJlOTY2ZDY4NzFjMCIsImludGVybmFsX3NlY3JldCI6ImVkYTc3NmNiLTk5NDUtNGI3Zi05NDMzLWJkM2I0NGVlNTJlMiJ9.BaF0Qiq7LhLgFm0r5RJmTHHOLggfaLjtTu0HYtTvkVs"
    )
    
    # File Upload Configuration
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    MAX_FILES_PER_UPLOAD: int = int(os.getenv("MAX_FILES_PER_UPLOAD", "100"))
    MAX_TOTAL_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_TOTAL_UPLOAD_SIZE_MB", "100"))
    
    # ML Service Configuration
    ML_SERVICE_URL: str = os.getenv("ML_SERVICE_URL", "http://localhost:8001")
    ML_SERVICE_TIMEOUT: int = int(os.getenv("ML_SERVICE_TIMEOUT", "300"))  # 5 minutes
    
    # Security Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    # Redis Configuration (for caching)
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    
    # License Configuration
    LICENSE_KEY: Optional[str] = os.getenv("LICENSE_KEY")
    LICENSE_VALIDATION_URL: Optional[str] = os.getenv("LICENSE_VALIDATION_URL")
    
    # Monitoring
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "false").lower() == "true"
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Ensure upload directory exists
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
