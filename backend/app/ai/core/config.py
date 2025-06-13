"""AI configuration settings."""

from pydantic import BaseModel, Field

from app.core.config import settings


class AIConfig(BaseModel):
    """AI configuration settings."""

    # Model settings
    model_name: str = Field(default_factory=lambda: settings.OPENAI_MODEL)
    temperature: float = 0.7

    # API settings
    api_key: str | None = Field(default_factory=lambda: settings.OPENAI_API_KEY)
    api_base: str | None = None

    class Config:
        arbitrary_types_allowed = True
