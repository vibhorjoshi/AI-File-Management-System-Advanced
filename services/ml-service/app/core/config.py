"""
ML Service Configuration
"""
import os
from pydantic_settings import BaseSettings
from typing import List, Optional

class MLSettings(BaseSettings):
    # App Configuration
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Model Configuration
    CLIP_MODEL_NAME: str = os.getenv("CLIP_MODEL_NAME", "openai/clip-vit-base-patch32")
    SENTENCE_MODEL_NAME: str = os.getenv("SENTENCE_MODEL_NAME", "all-MiniLM-L6-v2")
    
    # Processing Configuration
    MAX_BATCH_SIZE: int = int(os.getenv("MAX_BATCH_SIZE", "32"))
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    SUPPORTED_IMAGE_FORMATS: List[str] = ["jpg", "jpeg", "png", "gif", "webp", "bmp"]
    SUPPORTED_TEXT_FORMATS: List[str] = ["txt", "pdf", "doc", "docx"]
    
    # Cache Configuration
    ENABLE_CACHING: bool = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    CACHE_DIR: str = os.getenv("CACHE_DIR", "./cache")
    CACHE_EXPIRY_HOURS: int = int(os.getenv("CACHE_EXPIRY_HOURS", "24"))
    
    # Performance Configuration
    USE_GPU: bool = os.getenv("USE_GPU", "true").lower() == "true"
    NUM_WORKERS: int = int(os.getenv("NUM_WORKERS", "4"))
    SIMILARITY_BATCH_SIZE: int = int(os.getenv("SIMILARITY_BATCH_SIZE", "16"))
    
    # Feature Extraction
    IMAGE_EMBEDDING_SIZE: int = 512
    TEXT_EMBEDDING_SIZE: int = 384
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = MLSettings()
