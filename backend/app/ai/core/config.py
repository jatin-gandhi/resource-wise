"""AI configuration settings."""

from pydantic import BaseModel


class AIConfig(BaseModel):
    """AI configuration settings."""

    # Model settings
    model_name: str = "gpt-4-turbo-preview"
    temperature: float = 0.7

    # API settings
    api_key: str | None = None
    api_base: str | None = None

    class Config:
        arbitrary_types_allowed = True
