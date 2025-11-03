"""
Configuration settings for Risk Copilot API
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from pathlib import Path

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # API Configuration
    APP_NAME: str = "Risk Copilot API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "https://risk-copilot.netlify.app"
    ]
    
    # LLM Configuration
    USE_MOCK_LLM: bool = False
    OPENAI_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Model Settings
    DEFAULT_MODEL: str = "gpt-3.5-turbo"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 2000
    
    # Vector Store Configuration
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    FAISS_INDEX_PATH: str = "data/index"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    
    # Guardrails Configuration
    ENABLE_GUARDRAILS: bool = True
    BLOCK_PII: bool = True
    BLOCK_TOXIC: bool = True
    BANNED_TOPICS: List[str] = [
        "violence",
        "illegal",
        "harmful",
        "discriminatory"
    ]
    
    # Audit & Logging
    AUDIT_LOG_PATH: str = "data/audit"
    KEEP_AUDIT_DAYS: int = 30
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Database (for future use)
    DATABASE_URL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Create necessary directories
Path(settings.FAISS_INDEX_PATH).mkdir(parents=True, exist_ok=True)
Path(settings.AUDIT_LOG_PATH).mkdir(parents=True, exist_ok=True)
Path("data/policies").mkdir(parents=True, exist_ok=True)
