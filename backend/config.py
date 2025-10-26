"""
Central configuration management using Pydantic Settings.

This module provides type-safe configuration loading from environment variables
with validation and default values.
"""

from pathlib import Path
from typing import List

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings are validated at startup to ensure proper configuration.
    Sensitive values (like API keys) use SecretStr to prevent accidental logging.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # GCP Configuration
    gcp_project_id: str = Field(
        default="constellation-tech",
        description="Google Cloud Platform project ID",
    )
    gcp_region: str = Field(
        default="europe-west1",
        description="GCP region for services",
    )
    gcs_bucket_name: str = Field(
        default="constellation-tech-images",
        description="Cloud Storage bucket for generated images",
    )
    google_application_credentials: str = Field(
        default="../secrets/gcp-service-account.json",
        description="Path to GCP service account JSON file",
    )

    # Application Configuration
    daily_quota: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="Maximum number of generations per day (global)",
    )
    environment: str = Field(
        default="development",
        pattern="^(development|staging|production)$",
        description="Application environment",
    )
    log_level: str = Field(
        default="INFO",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Logging level",
    )

    # API Configuration
    api_title: str = Field(
        default="Constellation Tech API",
        description="API title for documentation",
    )
    api_version: str = Field(
        default="1.0.0",
        description="API version",
    )
    api_description: str = Field(
        default="Generate beautiful constellation visualizations from CVs",
        description="API description for documentation",
    )

    # CORS Configuration
    cors_origins: str = Field(
        default="*",
        description="Allowed CORS origins (comma-separated)",
    )

    @field_validator("cors_origins")
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        if v == "*":
            return ["*"]
        return [origin.strip() for origin in v.split(",") if origin.strip()]

    # Image Generation Settings
    canvas_size: int = Field(
        default=1024,
        ge=512,
        le=2048,
        description="Canvas size in pixels (square)",
    )
    min_star_distance: int = Field(
        default=120,
        ge=50,
        le=300,
        description="Minimum distance between stars in pixels",
    )
    random_noise: int = Field(
        default=30,
        ge=0,
        le=100,
        description="Random noise applied to star positions (±pixels)",
    )
    max_connections_per_star: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum number of connections per star",
    )

    # Storage Settings
    signed_url_expiration_days: int = Field(
        default=7,
        ge=1,
        le=365,
        description="Expiration time for signed URLs in days",
    )

    # Asset Paths
    @property
    def assets_dir(self) -> Path:
        """Base directory for static assets."""
        return Path(__file__).parent / "assets"

    @property
    def backgrounds_dir(self) -> Path:
        """Directory for pre-generated backgrounds."""
        return self.assets_dir / "backgrounds"

    @property
    def fonts_dir(self) -> Path:
        """Directory for fonts."""
        return self.assets_dir / "fonts"

    def ensure_directories(self) -> None:
        """Create required asset directories if they don't exist."""
        self.backgrounds_dir.mkdir(parents=True, exist_ok=True)
        self.fonts_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance (loaded once at startup)
settings = Settings()

# Ensure directories exist
settings.ensure_directories()
