from pydantic_settings import BaseSettings
from typing import Optional
from enum import Enum


class Environment(str, Enum):
    """Valid deployment environments."""

    SBX = "sbx"
    DEV = "dev"
    TEST = "test"
    QA = "qa"
    PROD = "prod"


class Settings(BaseSettings):
    # Environment
    environment: Environment = Environment.DEV

    # OpenAI settings
    openai_api_key: str
    openai_model: str
    max_tokens: int = 500

    # PostgreSQL settings
    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str

    # RAG settings
    max_context_documents: int = 3

    # Langfuse settings
    langfuse_public_key: str
    langfuse_secret_key: str
    langfuse_host: str
    langfuse_release: Optional[str]
    langfuse_debug: bool

    # AWS CDK settings
    cdk_default_account: Optional[str] = None
    cdk_default_region: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False  # Allow both uppercase and lowercase env vars
