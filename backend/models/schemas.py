"""
API request/response schemas.
"""

from typing import Any, Dict

from pydantic import BaseModel, Field


class TechnologySchema(BaseModel):
    """Technology detected in CV."""

    name: str = Field(..., description="Technology name")
    category: str = Field(..., description="Technology category")
    score: int = Field(..., ge=0, le=100, description="Relevance score (0-100)")
    color: str = Field(..., description="Category color (hex)")
    size: str = Field(..., description="Visualization size (large/medium/small)")


class StatsSchema(BaseModel):
    """Technology statistics."""

    total_techs_found: int = Field(..., ge=0)
    dominant_category: str
    level: str = Field(..., description="Skill level: Junior/Intermediate/Senior/Expert")
    categories_count: Dict[str, int]


class ConstellationResponse(BaseModel):
    """Response for constellation generation."""

    image_url: str = Field(..., description="Public URL to generated image")
    title: str = Field(..., description="Generated poetic title")
    technologies: list[Dict[str, Any]] = Field(..., description="Detected technologies")
    stats: Dict[str, Any] = Field(..., description="Technology statistics")
    generation_time: float = Field(..., description="Generation time in seconds")
    stars_detected: int = Field(..., description="Number of stars detected")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(default="healthy")
    version: str = Field(default="1.0.0")


class QuotaResponse(BaseModel):
    """Quota status response."""

    current_count: int
    max_quota: int
    remaining: int
    reset_date: str


class ErrorResponse(BaseModel):
    """Error response."""

    error: str
    detail: str | None = None
