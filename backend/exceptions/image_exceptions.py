"""
Custom exceptions for image generation operations.

These exceptions provide detailed error information for Vertex AI Imagen failures.
"""


class ImageGenerationError(Exception):
    """Base exception for image generation errors."""

    def __init__(self, message: str, prompt: str | None = None) -> None:
        """
        Initialize image generation error.

        Args:
            message: Error description
            prompt: Prompt that caused the error (optional)
        """
        self.prompt = prompt
        super().__init__(message)


class QuotaExceededError(ImageGenerationError):
    """Raised when daily image generation quota is exceeded."""

    def __init__(self, current_count: int, max_quota: int) -> None:
        """
        Initialize quota exceeded error.

        Args:
            current_count: Current generation count
            max_quota: Maximum allowed generations
        """
        self.current_count = current_count
        self.max_quota = max_quota
        super().__init__(
            f"Daily quota exceeded: {current_count}/{max_quota} generations used"
        )


class VertexAIError(ImageGenerationError):
    """Raised when Vertex AI API returns an error."""

    def __init__(
        self, message: str, status_code: int | None = None, prompt: str | None = None
    ) -> None:
        """
        Initialize Vertex AI error.

        Args:
            message: Error description
            status_code: HTTP status code (optional)
            prompt: Prompt that caused the error (optional)
        """
        self.status_code = status_code
        super().__init__(message, prompt=prompt)


class ImageValidationError(ImageGenerationError):
    """Raised when generated image fails validation."""

    def __init__(self, reason: str) -> None:
        """
        Initialize image validation error.

        Args:
            reason: Validation failure reason
        """
        super().__init__(f"Image validation failed: {reason}")
