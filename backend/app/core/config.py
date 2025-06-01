from pydantic_settings import BaseSettings
from typing import Optional, Dict, List, Union, Any
from functools import lru_cache
import os

class Settings(BaseSettings):
    """Application settings
    
    This class manages all configuration for the application, using environment variables
    with sensible defaults.
    """
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "BioSemanticViz API"
    VERSION: str = "0.2.0"
    DESCRIPTION: str = "API for biological data visualization and semantic reasoning"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["*"]  # In production, replace with specific origins
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "development_secret_key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database settings
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL", "sqlite:///./biosemantic.db")
    
    # File storage settings
    UPLOAD_FOLDER: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    ALLOWED_EXTENSIONS: List[str] = ["ttl", "rdf", "owl", "json", "csv", "tsv", "txt"]
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16 MB
    
    # Cache settings
    CACHE_ENABLED: bool = True
    CACHE_EXPIRATION: int = 3600  # 1 hour
    
    # Data paths
    DATA_DIR: str = os.getenv("DATA_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data"))
    
    # Add the missing BASE_DATA_DIR field (aliased to DATA_DIR for compatibility)
    BASE_DATA_DIR: str = os.getenv("BASE_DATA_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data"))
    
    ORTHOGROUPS_FILE: str = os.path.join(DATA_DIR, "orthofinder", "Orthogroups_clean_121124.txt")
    SPECIES_MAPPING_FILE: str = os.path.join(DATA_DIR, "orthofinder", "Table_S1_Metadata_angiosperm_species.csv")
    TREE_FILE: str = os.path.join(DATA_DIR, "orthofinder", "SpeciesTree_nameSp_completeGenome110124.tree")
    
    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT: int = 100  # requests per minute
    
    # ETE toolkit availability
    ETE_AVAILABLE: bool = True  # This will be updated at runtime
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"  # 🔥 This allows extra env vars without breaking!

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()