"""
Constellation generation endpoints.
"""

import logging

from fastapi import APIRouter, File, HTTPException, UploadFile

from exceptions.cv_exceptions import CVParserError
from exceptions.image_exceptions import QuotaExceededError
from models.schemas import ConstellationResponse, ErrorResponse, QuotaResponse
from services.constellation_orchestrator import ConstellationOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["constellation"])

# Global orchestrator instance
orchestrator = ConstellationOrchestrator()


@router.post(
    "/generate-constellation",
    response_model=ConstellationResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file"},
        429: {"model": ErrorResponse, "description": "Quota exceeded"},
        500: {"model": ErrorResponse, "description": "Generation failed"},
    },
)
async def generate_constellation(file: UploadFile = File(...)) -> ConstellationResponse:
    """
    Generate constellation from CV.

    Upload a CV (PDF or DOCX) and receive a beautiful constellation visualization.

    **Limitations:**
    - Max file size: 5MB
    - Supported formats: PDF, DOCX
    - Daily quota: 100 generations (global)

    **Response includes:**
    - Public image URL (valid 7 days)
    - Detected technologies with scores
    - Generated poetic title
    - Statistics and insights
    """
    logger.info(f"Received constellation generation request: {file.filename}")

    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # Check file size (5MB limit)
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset

    if file_size > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(
            status_code=400, detail=f"File too large: {file_size / 1024 / 1024:.1f}MB (max 5MB)"
        )

    # Read file
    try:
        content = await file.read()
    except Exception as e:
        logger.error(f"Failed to read file: {e}")
        raise HTTPException(status_code=400, detail="Failed to read uploaded file")

    # Generate constellation
    try:
        result = await orchestrator.generate(content, file.filename)

        return ConstellationResponse(
            image_url=result.image_url,
            title=result.title,
            technologies=result.technologies,
            stats=result.stats,
            generation_time=result.generation_time,
            stars_detected=result.stars_detected,
        )

    except CVParserError as e:
        logger.error(f"CV parsing error: {e}")
        raise HTTPException(
            status_code=400, detail=f"Failed to parse CV: {str(e)}"
        )

    except QuotaExceededError as e:
        logger.warning(f"Quota exceeded: {e}")
        raise HTTPException(
            status_code=429,
            detail=f"Daily quota exceeded: {e.current_count}/{e.max_quota} generations used",
        )

    except Exception as e:
        logger.error(f"Generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Generation failed: {str(e)}"
        )


@router.get("/quota", response_model=QuotaResponse)
async def get_quota_status() -> QuotaResponse:
    """
    Get current quota status.

    Returns information about daily generation quota:
    - Current usage count
    - Maximum quota
    - Remaining generations
    - Reset date (daily at midnight UTC)
    """
    status = orchestrator.get_quota_status()

    return QuotaResponse(
        current_count=status["current_count"],
        max_quota=status["max_quota"],
        remaining=status["remaining"],
        reset_date=status["reset_date"],
    )
