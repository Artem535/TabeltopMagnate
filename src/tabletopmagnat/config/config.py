"""
Application Configuration Module.

This module provides the main configuration class for the TabletopMagnat application.
It uses `pydantic_settings` to load configuration values from environment variables
and a `.env` file, allowing for structured and type-safe access to configuration data.

Key Features:
- Automatic loading of environment variables from `.env`.
- Support for nested configuration via `env_nested_delimiter`.
- Integration with service-specific configurations (e.g., OpenAI).

Classes:
    Config: Main configuration class that includes service-specific configurations.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore

from tabletopmagnat.config.langfuse import LangfuseSettings
from tabletopmagnat.config.models import Models
from tabletopmagnat.config.openai_config import OpenAIConfig


class Config(BaseSettings):
    """
    Main application configuration class.

    Uses `pydantic_settings.BaseSettings` to automatically load settings from
    environment variables and the `.env` file.

    Attributes:
        model_config (SettingsConfigDict): Pydantic configuration specifying
            the `.env` file path, encoding, and nested parameter delimiter.
        openai (OpenAIConfig): Nested configuration for OpenAI services.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__"
    )
    models: Models = Models()
    openai: OpenAIConfig = OpenAIConfig()
    langfuse: LangfuseSettings = LangfuseSettings()