"""Application configuration settings"""

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # App Info
    APP_NAME: str = "Resource Wise API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = Field(default=False)

    # Database Configuration - Individual Fields
    DB_HOST: str = Field(description="Database host", default="localhost")
    DB_PORT: int = Field(description="Database port", default=5432)
    DB_USER: str = Field(description="Database user", default="admin")
    DB_PASSWORD: str = Field(description="Database password", default="admin")
    DB_NAME: str = Field(description="Database name", default="resourcewise")
    DB_DRIVER: str = Field(description="Database driver", default="postgresql+asyncpg")
    DATABASE_ECHO: bool = Field(description="Database echo", default=False)

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        """Construct DATABASE_URL from individual components"""
        return f"{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(description="OpenAI API key", default="")
    OPENAI_MODEL: str = Field(description="OpenAI model", default="gpt-4")
    OPENAI_EMBEDDING_MODEL: str = Field(
        description="OpenAI embedding model", default="text-embedding-ada-002"
    )

    # CORS - Simple string that will be split on comma
    ALLOWED_ORIGINS: str = Field(
        description="Allowed origins", default="http://localhost:3000,http://localhost:5173,http://localhost:8000"
    )

    @computed_field
    @property
    def CORS_ORIGINS(self) -> list[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    model_config = {"env_file": ".env", "case_sensitive": True, "env_prefix": "", "extra": "ignore"}


# Create settings instance
settings = Settings()
