from pydantic import Field
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with proper validation"""
    
    # Database configuration
    DATABASE_HOSTNAME: str = Field(..., description="PostgreSQL hostname")
    DATABASE_PORT: int = Field(5432, description="PostgreSQL port")
    DATABASE_USERNAME: str = Field(..., description="PostgreSQL username") 
    DATABASE_PASSWORD: str = Field(..., description="PostgreSQL password")
    DATABASE_NAME: str = Field(..., description="PostgreSQL database name")
    
    # Application configuration
    DEBUG: bool = Field(False, description="Debug mode")
    
    # CORS configuration
    BACKEND_CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="List of allowed CORS origins"
    )
    
    @property
    def DATABASE_URL(self) -> str:
        """Build database URL from components"""
        return (
            f"postgresql+asyncpg://{self.DATABASE_USERNAME}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOSTNAME}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

settings = get_settings()