"""
Unit tests for ImageGenerator service.

Uses mocking to avoid actual Vertex AI API calls during testing.
"""

from datetime import date
from unittest.mock import MagicMock, Mock, patch

import pytest
from PIL import Image

from exceptions.image_exceptions import (
    ImageValidationError,
    QuotaExceededError,
    VertexAIError,
)
from services.image_generator import ImageGenerator


class TestImageGenerator:
    """Test suite for ImageGenerator."""

    @pytest.fixture(autouse=True)
    def reset_quota(self) -> None:
        """Reset quota before each test."""
        ImageGenerator._generation_count = 0
        ImageGenerator._quota_reset_date = date.today()

    @pytest.fixture
    def mock_vertex_ai(self) -> None:
        """Mock Vertex AI initialization."""
        with patch("services.image_generator.aiplatform.init"):
            with patch("services.image_generator.service_account.Credentials"):
                yield

    @pytest.fixture
    def mock_model(self) -> Mock:
        """Create a mock Imagen model."""
        with patch(
            "services.image_generator.ImageGenerationModel.from_pretrained"
        ) as mock:
            model_mock = Mock()
            mock.return_value = model_mock
            yield model_mock

    @pytest.fixture
    def generator(self, mock_vertex_ai: None, mock_model: Mock) -> ImageGenerator:
        """Create an ImageGenerator instance with mocked dependencies."""
        return ImageGenerator()

    def test_initialization(
        self, mock_vertex_ai: None, mock_model: Mock
    ) -> None:
        """Test that generator initializes correctly."""
        generator = ImageGenerator()
        assert generator is not None
        assert generator.model is not None

    def test_quota_tracking(self, generator: ImageGenerator) -> None:
        """Test that quota is tracked correctly."""
        status = generator.get_quota_status()

        assert status["current_count"] == 0
        assert status["max_quota"] == 100  # From config
        assert status["remaining"] == 100

    @pytest.mark.asyncio
    async def test_generate_success(
        self, generator: ImageGenerator, mock_model: Mock
    ) -> None:
        """Test successful image generation."""
        # Create a mock response with image
        mock_image = Mock()
        mock_image._pil_image = Image.new("RGBA", (1024, 1024), (0, 0, 0, 255))

        mock_response = Mock()
        mock_response.images = [mock_image]

        mock_model.generate_images.return_value = mock_response

        # Generate image
        prompt = "Beautiful constellation with 7 stars"
        image = await generator.generate(prompt)

        # Assertions
        assert isinstance(image, Image.Image)
        assert image.size == (1024, 1024)
        assert image.mode == "RGBA"

        # Check quota updated
        status = generator.get_quota_status()
        assert status["current_count"] == 1

    @pytest.mark.asyncio
    async def test_quota_exceeded(
        self, generator: ImageGenerator, mock_model: Mock
    ) -> None:
        """Test that quota enforcement works."""
        # Set quota to limit
        generator._generation_count = 100  # Max quota from config

        # Try to generate (should fail)
        with pytest.raises(QuotaExceededError) as exc_info:
            await generator.generate("test prompt")

        assert exc_info.value.current_count == 100
        assert exc_info.value.max_quota == 100

    @pytest.mark.asyncio
    async def test_quota_reset_on_new_day(
        self, generator: ImageGenerator, mock_model: Mock
    ) -> None:
        """Test that quota resets on new day."""
        # Set quota to yesterday
        from datetime import timedelta

        generator._generation_count = 50
        generator._quota_reset_date = date.today() - timedelta(days=1)

        # Check status (should trigger reset)
        status = generator.get_quota_status()

        assert status["current_count"] == 0
        assert status["reset_date"] == date.today().isoformat()

    def test_validate_image_success(self, generator: ImageGenerator) -> None:
        """Test image validation passes for valid images."""
        valid_image = Image.new("RGBA", (1024, 1024), (100, 100, 100, 255))

        # Should not raise
        generator._validate_image(valid_image)

    def test_validate_image_wrong_size(self, generator: ImageGenerator) -> None:
        """Test image validation fails for wrong size."""
        invalid_image = Image.new("RGBA", (512, 512), (100, 100, 100, 255))

        with pytest.raises(ImageValidationError) as exc_info:
            generator._validate_image(invalid_image)

        assert "size" in str(exc_info.value).lower()

    def test_validate_image_wrong_mode(self, generator: ImageGenerator) -> None:
        """Test image validation fails for wrong mode."""
        invalid_image = Image.new("L", (1024, 1024), 100)  # Grayscale

        with pytest.raises(ImageValidationError) as exc_info:
            generator._validate_image(invalid_image)

        assert "mode" in str(exc_info.value).lower()

    def test_validate_image_blank(self, generator: ImageGenerator) -> None:
        """Test image validation fails for blank images."""
        blank_image = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))

        with pytest.raises(ImageValidationError) as exc_info:
            generator._validate_image(blank_image)

        assert "black" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_vertex_ai_error_handling(
        self, generator: ImageGenerator, mock_model: Mock
    ) -> None:
        """Test error handling for Vertex AI failures."""
        # Mock API error
        mock_model.generate_images.side_effect = Exception("API Error")

        with pytest.raises(VertexAIError) as exc_info:
            await generator.generate("test prompt")

        assert "API Error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_vertex_ai_quota_error(
        self, generator: ImageGenerator, mock_model: Mock
    ) -> None:
        """Test handling of Vertex AI quota errors."""
        # Mock quota error
        mock_model.generate_images.side_effect = Exception(
            "429 Quota exceeded for aiplatform"
        )

        with pytest.raises(VertexAIError) as exc_info:
            await generator.generate("test prompt")

        assert exc_info.value.status_code == 429
        assert "quota" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_safety_filter_error(
        self, generator: ImageGenerator, mock_model: Mock
    ) -> None:
        """Test handling of safety filter errors."""
        mock_model.generate_images.side_effect = Exception("Safety filter triggered")

        with pytest.raises(VertexAIError) as exc_info:
            await generator.generate("inappropriate prompt")

        assert exc_info.value.status_code == 400
        assert "safety" in str(exc_info.value).lower()

    def test_reset_quota(self, generator: ImageGenerator) -> None:
        """Test manual quota reset."""
        generator._generation_count = 50

        generator.reset_quota()

        status = generator.get_quota_status()
        assert status["current_count"] == 0

    @pytest.mark.asyncio
    async def test_multiple_generations(
        self, generator: ImageGenerator, mock_model: Mock
    ) -> None:
        """Test multiple image generations update quota correctly."""
        # Setup mock
        mock_image = Mock()
        mock_image._pil_image = Image.new("RGBA", (1024, 1024), (50, 50, 50, 255))

        mock_response = Mock()
        mock_response.images = [mock_image]
        mock_model.generate_images.return_value = mock_response

        # Generate 3 images
        for i in range(3):
            await generator.generate(f"prompt {i}")

        # Check quota
        status = generator.get_quota_status()
        assert status["current_count"] == 3
        assert status["remaining"] == 97

    def test_convert_to_pil_with_pil_image(self, generator: ImageGenerator) -> None:
        """Test conversion when Imagen object has _pil_image attribute."""
        mock_imagen = Mock()
        mock_imagen._pil_image = Image.new("RGB", (1024, 1024), (100, 100, 100))

        result = generator._convert_to_pil(mock_imagen)

        assert isinstance(result, Image.Image)
        assert result.mode == "RGBA"  # Converted to RGBA

    def test_convert_to_pil_with_bytes(self, generator: ImageGenerator) -> None:
        """Test conversion when Imagen object has _image_bytes."""
        import io

        # Create image bytes
        test_image = Image.new("RGB", (1024, 1024), (100, 100, 100))
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        mock_imagen = Mock()
        mock_imagen._pil_image = None
        mock_imagen._image_bytes = img_bytes.getvalue()

        # Remove _pil_image attribute
        del mock_imagen._pil_image

        result = generator._convert_to_pil(mock_imagen)

        assert isinstance(result, Image.Image)
        assert result.mode == "RGBA"
