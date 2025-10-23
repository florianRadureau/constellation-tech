"""
Health check endpoints.
"""

from fastapi import APIRouter

from models.schemas import HealthResponse

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns API status and version.
    """
    return HealthResponse(status="healthy", version="1.0.0")
