"""
Image generation service using Vertex AI Imagen.

Generates beautiful constellation images from simple text prompts.
"""

import io
import logging
import os
from datetime import date, datetime
from typing import ClassVar

from google.cloud import aiplatform
from google.oauth2 import service_account
from PIL import Image
from vertexai.preview.vision_models import ImageGenerationModel

from config import settings
from exceptions.image_exceptions import (
    ImageGenerationError,
    ImageValidationError,
    QuotaExceededError,
    VertexAIError,
)

logger = logging.getLogger(__name__)


class ImageGenerator:
    """
    Generate constellation images using Vertex AI Imagen.

    Manages quota, authentication, and image generation with simple prompts.

    Example:
        >>> generator = ImageGenerator()
        >>> image = await generator.generate("Beautiful constellation with 7 stars")
        >>> image.save("constellation.png")
    """

    # Class-level quota tracking (shared across instances)
    _generation_count: ClassVar[int] = 0
    _quota_reset_date: ClassVar[date] = date.today()

    def __init__(self) -> None:
        """
        Initialize image generator with Vertex AI credentials.

        Raises:
            FileNotFoundError: If credentials file not found
            ValueError: If credentials are invalid
        """
        self._initialize_vertex_ai()
        self.model = self._load_model()

        logger.info("ImageGenerator initialized successfully")

    def _initialize_vertex_ai(self) -> None:
        """
        Initialize Vertex AI with credentials from settings.

        Raises:
            FileNotFoundError: If credentials file doesn't exist
        """
        credentials_path = settings.google_application_credentials

        if not os.path.exists(credentials_path):
            raise FileNotFoundError(
                f"GCP credentials not found at: {credentials_path}. "
                f"Please ensure the service account JSON file exists."
            )

        # Load credentials
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

        # Initialize Vertex AI
        aiplatform.init(
            project=settings.gcp_project_id,
            location=settings.gcp_region,
            credentials=credentials,
        )

        logger.info(
            f"Vertex AI initialized (project={settings.gcp_project_id}, "
            f"region={settings.gcp_region})"
        )

    def _load_model(self) -> ImageGenerationModel:
        """
        Load Vertex AI Imagen model.

        Returns:
            ImageGenerationModel instance

        Raises:
            VertexAIError: If model loading fails
        """
        try:
            model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
            logger.info("Imagen model loaded successfully")
            return model
        except Exception as e:
            raise VertexAIError(f"Failed to load Imagen model: {e}") from e

    def _check_and_update_quota(self) -> None:
        """
        Check if quota is available and update counters.

        Quota resets daily at midnight UTC.

        Raises:
            QuotaExceededError: If daily quota is exceeded
        """
        today = date.today()

        # Reset quota if new day
        if today > self._quota_reset_date:
            logger.info(
                f"Quota reset: {self._generation_count} generations on "
                f"{self._quota_reset_date}"
            )
            self._generation_count = 0
            self._quota_reset_date = today

        # Check quota
        if self._generation_count >= settings.daily_quota:
            raise QuotaExceededError(self._generation_count, settings.daily_quota)

        # Increment counter
        self._generation_count += 1
        logger.info(
            f"Generation {self._generation_count}/{settings.daily_quota} "
            f"(date: {self._quota_reset_date})"
        )

    async def generate(self, prompt: str, size: int = 1024) -> Image.Image:
        """
        Generate constellation image from prompt.

        Args:
            prompt: Text description of desired constellation
            size: Image size in pixels (must be 1024)

        Returns:
            PIL Image object (RGBA format, 1024x1024)

        Raises:
            QuotaExceededError: If daily quota exceeded
            VertexAIError: If API call fails
            ImageValidationError: If generated image is invalid

        Example:
            >>> generator = ImageGenerator()
            >>> prompt = "Beautiful constellation with 8 bright stars"
            >>> image = await generator.generate(prompt)
            >>> image.size  # (1024, 1024)
        """
        # Check quota before generation
        self._check_and_update_quota()

        # Validate size
        if size != 1024:
            logger.warning(f"Size {size} not supported, using 1024")
            size = 1024

        logger.info(f"Generating image with prompt: {prompt[:100]}...")

        try:
            # Call Imagen API
            start_time = datetime.now()

            response = self.model.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio="1:1",
                safety_filter_level="block_some",
                person_generation="allow_adult",
            )

            generation_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Image generated in {generation_time:.2f}s")

            # Extract image from response
            imagen_image = response.images[0]

            # Convert to PIL Image
            image = self._convert_to_pil(imagen_image)

            # Validate image
            self._validate_image(image)

            logger.info("Image generation successful")
            return image

        except Exception as e:
            if "quota" in str(e).lower() or "429" in str(e):
                raise VertexAIError(
                    f"Vertex AI quota exceeded: {e}", status_code=429, prompt=prompt
                ) from e
            elif "safety" in str(e).lower():
                raise VertexAIError(
                    f"Safety filter triggered: {e}", status_code=400, prompt=prompt
                ) from e
            else:
                raise VertexAIError(
                    f"Image generation failed: {e}", prompt=prompt
                ) from e

    def _convert_to_pil(self, imagen_image: any) -> Image.Image:
        """
        Convert Imagen image object to PIL Image.

        Args:
            imagen_image: Imagen response image object

        Returns:
            PIL Image in RGBA format

        Raises:
            ImageGenerationError: If conversion fails
        """
        try:
            # Imagen images have a _pil_image attribute
            if hasattr(imagen_image, "_pil_image"):
                pil_image = imagen_image._pil_image
            else:
                # Fallback: save to bytes and reload
                image_bytes = imagen_image._image_bytes
                pil_image = Image.open(io.BytesIO(image_bytes))

            # Ensure RGBA format
            if pil_image.mode != "RGBA":
                pil_image = pil_image.convert("RGBA")

            logger.debug(
                f"Converted to PIL Image: size={pil_image.size}, mode={pil_image.mode}"
            )
            return pil_image

        except Exception as e:
            raise ImageGenerationError(f"Failed to convert image: {e}") from e

    def _validate_image(self, image: Image.Image) -> None:
        """
        Validate generated image meets requirements.

        Args:
            image: PIL Image to validate

        Raises:
            ImageValidationError: If image is invalid
        """
        # Check format
        if image.mode not in ["RGB", "RGBA"]:
            raise ImageValidationError(f"Invalid image mode: {image.mode}")

        # Check size
        if image.size != (1024, 1024):
            raise ImageValidationError(
                f"Invalid image size: {image.size}, expected (1024, 1024)"
            )

        # Check if image is not blank
        extrema = image.getextrema()
        if extrema == ((0, 0), (0, 0), (0, 0), (0, 0)):
            raise ImageValidationError("Image is completely black")

        logger.debug("Image validation passed")

    def get_quota_status(self) -> dict[str, any]:
        """
        Get current quota status.

        Returns:
            Dictionary with quota information

        Example:
            >>> status = generator.get_quota_status()
            >>> print(status)
            {
                'current_count': 5,
                'max_quota': 100,
                'remaining': 95,
                'reset_date': '2025-10-24'
            }
        """
        # Check if quota should be reset
        today = date.today()
        if today > self._quota_reset_date:
            self._generation_count = 0
            self._quota_reset_date = today

        return {
            "current_count": self._generation_count,
            "max_quota": settings.daily_quota,
            "remaining": settings.daily_quota - self._generation_count,
            "reset_date": self._quota_reset_date.isoformat(),
        }

    def reset_quota(self) -> None:
        """
        Manually reset quota counter.

        Useful for testing or administrative purposes.
        """
        self._generation_count = 0
        self._quota_reset_date = date.today()
        logger.warning("Quota manually reset")
