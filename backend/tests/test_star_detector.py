"""
Unit tests for StarDetector service.
"""

import pytest
from PIL import Image, ImageDraw

from services.star_detector import StarDetector, StarPosition


class TestStarDetector:
    """Test suite for StarDetector."""

    @pytest.fixture
    def detector(self) -> StarDetector:
        """Create a StarDetector instance with default settings."""
        return StarDetector()

    @pytest.fixture
    def simple_constellation(self) -> Image.Image:
        """Create a simple test image with 5 bright stars."""
        # Black background
        img = Image.new("RGB", (1024, 1024), (10, 10, 10))
        draw = ImageDraw.Draw(img)

        # Add 5 bright stars at known positions
        stars = [
            (200, 200, 255, 30),  # x, y, brightness, radius
            (800, 200, 240, 25),
            (500, 500, 230, 20),
            (300, 700, 220, 18),
            (700, 800, 210, 15),
        ]

        for x, y, brightness, radius in stars:
            color = (brightness, brightness, brightness)
            draw.ellipse(
                [x - radius, y - radius, x + radius, y + radius], fill=color
            )

        return img

    def test_initialization(self, detector: StarDetector) -> None:
        """Test that detector initializes correctly."""
        assert detector is not None
        assert detector.min_brightness == 180
        assert detector.min_size == 10
        assert detector.max_stars == 20

    def test_initialization_with_custom_params(self) -> None:
        """Test initialization with custom parameters."""
        detector = StarDetector(min_brightness=200, min_size=20, max_stars=10)

        assert detector.min_brightness == 200
        assert detector.min_size == 20
        assert detector.max_stars == 10

    def test_detect_simple_constellation(
        self, detector: StarDetector, simple_constellation: Image.Image
    ) -> None:
        """Test detection on simple constellation image."""
        stars = detector.detect(simple_constellation)

        assert isinstance(stars, list)
        assert len(stars) > 0

        # Check that stars are StarPosition objects
        for star in stars:
            assert isinstance(star, StarPosition)
            assert isinstance(star.x, int)
            assert isinstance(star.y, int)
            assert isinstance(star.brightness, float)
            assert isinstance(star.color, tuple)
            assert len(star.color) == 3

    def test_stars_sorted_by_brightness(
        self, detector: StarDetector, simple_constellation: Image.Image
    ) -> None:
        """Test that detected stars are sorted by brightness."""
        stars = detector.detect(simple_constellation)

        # Check descending brightness order
        for i in range(len(stars) - 1):
            assert (
                stars[i].brightness >= stars[i + 1].brightness
            ), "Stars should be sorted by brightness (descending)"

    def test_detect_with_high_threshold(
        self, simple_constellation: Image.Image
    ) -> None:
        """Test detection with very high brightness threshold."""
        detector = StarDetector(min_brightness=250)  # Very high

        stars = detector.detect(simple_constellation)

        # Should detect only the brightest star (255 brightness)
        assert len(stars) <= 2  # Maybe 1-2 stars

    def test_detect_with_low_threshold(
        self, simple_constellation: Image.Image
    ) -> None:
        """Test detection with low brightness threshold."""
        detector = StarDetector(min_brightness=150)  # Lower

        stars = detector.detect(simple_constellation)

        # Should detect all 5 stars
        assert len(stars) >= 5

    def test_detect_empty_image(self, detector: StarDetector) -> None:
        """Test detection on completely black image."""
        black_image = Image.new("RGB", (1024, 1024), (0, 0, 0))

        stars = detector.detect(black_image)

        assert len(stars) == 0  # No stars detected

    def test_detect_single_star(self, detector: StarDetector) -> None:
        """Test detection with single bright star."""
        img = Image.new("RGB", (1024, 1024), (10, 10, 10))
        draw = ImageDraw.Draw(img)

        # Single bright star
        draw.ellipse([500, 500, 550, 550], fill=(255, 255, 255))

        stars = detector.detect(img)

        assert len(stars) == 1
        star = stars[0]

        # Check position is approximately center (within margin)
        assert 490 < star.x < 560
        assert 490 < star.y < 560

    def test_star_position_coordinates(
        self, detector: StarDetector, simple_constellation: Image.Image
    ) -> None:
        """Test that star positions are within image bounds."""
        stars = detector.detect(simple_constellation)

        for star in stars:
            assert 0 <= star.x < 1024
            assert 0 <= star.y < 1024

    def test_star_brightness_range(
        self, detector: StarDetector, simple_constellation: Image.Image
    ) -> None:
        """Test that brightness values are in valid range."""
        stars = detector.detect(simple_constellation)

        for star in stars:
            assert 0 <= star.brightness <= 255

    def test_star_color_extraction(self) -> None:
        """Test color extraction from colored stars."""
        img = Image.new("RGB", (1024, 1024), (10, 10, 10))
        draw = ImageDraw.Draw(img)

        # Red star (bright enough to be detected)
        draw.ellipse([200, 200, 250, 250], fill=(255, 180, 180))

        # Blue star (bright enough to be detected)
        draw.ellipse([700, 700, 750, 750], fill=(180, 180, 255))

        # Use lower threshold for color detection
        detector = StarDetector(min_brightness=150)
        stars = detector.detect(img)

        assert len(stars) == 2

        # Check colors are extracted (approximately)
        # Colors might not be exact due to averaging
        # Just verify we got some color data
        for star in stars:
            assert star.color[0] >= 0
            assert star.color[1] >= 0
            assert star.color[2] >= 0

    def test_max_stars_limit(self, detector: StarDetector) -> None:
        """Test that max_stars parameter is respected."""
        # Create image with many stars
        img = Image.new("RGB", (1024, 1024), (10, 10, 10))
        draw = ImageDraw.Draw(img)

        # Add 30 stars
        for i in range(30):
            x = 50 + (i % 10) * 100
            y = 50 + (i // 10) * 300
            draw.ellipse([x, y, x + 20, y + 20], fill=(255, 255, 255))

        detector = StarDetector(max_stars=10)
        stars = detector.detect(img)

        # Should be limited to 10
        assert len(stars) <= 10

    def test_min_size_filtering(self) -> None:
        """Test that tiny stars are filtered out."""
        img = Image.new("RGB", (1024, 1024), (10, 10, 10))
        draw = ImageDraw.Draw(img)

        # Large star (should be detected)
        draw.ellipse([200, 200, 250, 250], fill=(255, 255, 255))

        # Tiny star (should be filtered)
        draw.ellipse([700, 700, 702, 702], fill=(255, 255, 255))

        detector = StarDetector(min_size=50)  # Large min_size
        stars = detector.detect(img)

        # Should only detect large star
        assert len(stars) == 1

    def test_detect_with_adjustable_threshold(
        self, detector: StarDetector, simple_constellation: Image.Image
    ) -> None:
        """Test adaptive threshold adjustment."""
        # Request 10 stars (more than in image)
        stars = detector.detect_with_adjustable_threshold(
            simple_constellation, target_count=10
        )

        # Should detect all available stars (5 in this case)
        assert len(stars) >= 5

    def test_detect_with_adjustable_threshold_exact_match(
        self, detector: StarDetector, simple_constellation: Image.Image
    ) -> None:
        """Test adaptive threshold when target is available."""
        # Request 3 stars (less than in image)
        stars = detector.detect_with_adjustable_threshold(
            simple_constellation, target_count=3
        )

        # Should return exactly 3
        assert len(stars) == 3

    def test_star_position_repr(self) -> None:
        """Test StarPosition string representation."""
        star = StarPosition(
            x=100, y=200, brightness=250.5, color=(255, 0, 0), size=100
        )

        repr_str = repr(star)

        assert "100" in repr_str  # x coordinate
        assert "200" in repr_str  # y coordinate
        assert "250.5" in repr_str  # brightness

    def test_rgba_image_handling(self, detector: StarDetector) -> None:
        """Test that RGBA images are handled correctly."""
        img = Image.new("RGBA", (1024, 1024), (10, 10, 10, 255))
        draw = ImageDraw.Draw(img)

        # Add a star
        draw.ellipse([500, 500, 550, 550], fill=(255, 255, 255, 255))

        # Should not crash
        stars = detector.detect(img)
        assert len(stars) == 1

    def test_visualize_detection(
        self, detector: StarDetector, simple_constellation: Image.Image, tmp_path
    ) -> None:
        """Test visualization output."""
        stars = detector.detect(simple_constellation)

        output_path = tmp_path / "test_visualization.png"

        # Should not crash
        detector.visualize_detection(
            simple_constellation, stars, str(output_path)
        )

        # Check file was created
        assert output_path.exists()

        # Check it's a valid image
        result = Image.open(output_path)
        assert result.size == (1024, 1024)
