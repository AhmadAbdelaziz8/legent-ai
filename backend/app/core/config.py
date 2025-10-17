from pydantic_settings import BaseSettings
from app.service.computer_use.loop import APIProvider


class Settings(BaseSettings):
    DATABASE_URL: str
    ANTHROPIC_API_KEY: str = ""

    # AWS Bedrock settings
    AWS_PROFILE: str = ""
    AWS_REGION: str = "us-west-2"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""

    # API Provider selection
    API_PROVIDER: str = "anthropic"  # anthropic, bedrock, vertex

    class Config:
        env_file = '.env'
        extra = 'ignore'


PROVIDER_TO_DEFAULT_MODEL = {
    APIProvider.ANTHROPIC: "claude-sonnet-4-5-20250929",
    APIProvider.BEDROCK: "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    APIProvider.VERTEX: "claude-sonnet-4@20250514",
}

MODEL_TO_CONFIG = {
    # Anthropic models
    "claude-sonnet-4-5-20250929": {"tool_version": "computer_use_20250124", "max_tokens": 128_000, "has_thinking": True},
    "claude-sonnet-4-20250514": {"tool_version": "computer_use_20250124", "max_tokens": 128_000, "has_thinking": True},
    "claude-opus-4-20250514": {"tool_version": "computer_use_20250124", "max_tokens": 128_000, "has_thinking": True},
    "claude-haiku-4-5-20251001": {"tool_version": "computer_use_20250124", "max_tokens": 1024 * 8, "has_thinking": False},
    "claude-3-haiku-20240307": {"tool_version": "computer_use_20241022", "max_tokens": 1024 * 8, "has_thinking": False},
    "claude-3-7-sonnet-20250219": {"tool_version": "computer_use_20250124", "max_tokens": 128_000, "has_thinking": True},

    # AWS Bedrock models
    "us.anthropic.claude-3-7-sonnet-20250219-v1:0": {"tool_version": "computer_use_20250124", "max_tokens": 128_000, "has_thinking": True},
    "anthropic.claude-haiku-4-5-20251001-v1:0": {"tool_version": "computer_use_20250124", "max_tokens": 1024 * 8, "has_thinking": False},
    "anthropic.claude-sonnet-4-5-20250929-v1:0": {"tool_version": "computer_use_20250124", "max_tokens": 128_000, "has_thinking": True},
    "anthropic.claude-opus-4-20250514-v1:0": {"tool_version": "computer_use_20250124", "max_tokens": 128_000, "has_thinking": True},

    # Vertex AI models
    "claude-haiku-4-5@20251001": {"tool_version": "computer_use_20250124", "max_tokens": 1024 * 8, "has_thinking": False},
    "claude-sonnet-4@20250514": {"tool_version": "computer_use_20250124", "max_tokens": 128_000, "has_thinking": True},
    "claude-opus-4@20250508": {"tool_version": "computer_use_20250124", "max_tokens": 128_000, "has_thinking": True},
}

settings = Settings()
