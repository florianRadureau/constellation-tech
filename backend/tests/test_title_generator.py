"""
Unit tests for TitleGenerator service.
"""

import pytest

from services.title_generator import TitleGenerator


class TestTitleGenerator:
    """Test suite for TitleGenerator."""

    @pytest.fixture
    def generator(self) -> TitleGenerator:
        """Create a TitleGenerator instance with fixed seed for deterministic tests."""
        return TitleGenerator(seed=42)

    def test_initialization(self, generator: TitleGenerator) -> None:
        """Test that generator initializes correctly."""
        assert generator is not None
        assert len(generator.get_categories()) > 0

    def test_generate_frontend_title(self, generator: TitleGenerator) -> None:
        """Test title generation for Frontend category."""
        stats = {"dominant_category": "Frontend", "total_techs_found": 5}
        title = generator.generate(stats)

        assert isinstance(title, str)
        assert len(title) > 0
        # Should be one of the Frontend metaphors
        assert title in generator.METAPHORS["Frontend"]

    def test_generate_backend_title(self, generator: TitleGenerator) -> None:
        """Test title generation for Backend category."""
        stats = {"dominant_category": "Backend"}
        title = generator.generate(stats)

        assert isinstance(title, str)
        assert title in generator.METAPHORS["Backend"]

    def test_generate_ai_ml_title(self, generator: TitleGenerator) -> None:
        """Test title generation for AI_ML category."""
        stats = {"dominant_category": "AI_ML"}
        title = generator.generate(stats)

        assert isinstance(title, str)
        assert title in generator.METAPHORS["AI_ML"]

    def test_generate_devops_title(self, generator: TitleGenerator) -> None:
        """Test title generation for DevOps category."""
        stats = {"dominant_category": "DevOps"}
        title = generator.generate(stats)

        assert isinstance(title, str)
        assert title in generator.METAPHORS["DevOps"]

    def test_fallback_for_missing_category(self, generator: TitleGenerator) -> None:
        """Test fallback title when dominant_category is missing."""
        stats = {"total_techs_found": 5}  # No dominant_category
        title = generator.generate(stats)

        assert title == generator.FALLBACK_TITLE

    def test_fallback_for_unknown_category(self, generator: TitleGenerator) -> None:
        """Test fallback title for unknown category."""
        stats = {"dominant_category": "UnknownCategory"}
        title = generator.generate(stats)

        assert title == generator.FALLBACK_TITLE

    def test_fallback_for_empty_stats(self, generator: TitleGenerator) -> None:
        """Test fallback title with empty stats."""
        title = generator.generate({})

        assert title == generator.FALLBACK_TITLE

    def test_generate_with_context_high_count(self, generator: TitleGenerator) -> None:
        """Test enriched title with high technology count."""
        stats = {"dominant_category": "Frontend"}
        title = generator.generate_with_context(stats, tech_count=15)

        assert "15" in title
        assert "Technologies" in title

    def test_generate_with_context_low_count(self, generator: TitleGenerator) -> None:
        """Test that low count doesn't enrich title."""
        stats = {"dominant_category": "Backend"}
        title = generator.generate_with_context(stats, tech_count=5)

        # Should not include count for low numbers
        assert "5" not in title
        assert title in generator.METAPHORS["Backend"]

    def test_all_categories_have_metaphors(self, generator: TitleGenerator) -> None:
        """Test that all categories have at least one metaphor."""
        categories = generator.get_categories()

        for category in categories:
            metaphors = generator.METAPHORS[category]
            assert len(metaphors) > 0, f"Category '{category}' has no metaphors"
            # Check all metaphors are non-empty strings
            for metaphor in metaphors:
                assert isinstance(metaphor, str)
                assert len(metaphor) > 0

    def test_randomness_without_seed(self) -> None:
        """Test that titles vary when no seed is set (randomness works)."""
        generator = TitleGenerator()  # No seed
        stats = {"dominant_category": "Frontend"}

        # Generate multiple titles
        titles = [generator.generate(stats) for _ in range(20)]

        # Should have some variation (not all identical)
        # Frontend has 5 metaphors, so we should see at least 2 different ones
        unique_titles = set(titles)
        assert len(unique_titles) >= 2

    def test_get_all_metaphors_returns_copy(self, generator: TitleGenerator) -> None:
        """Test that get_all_metaphors returns a copy (not the original)."""
        metaphors = generator.get_all_metaphors()

        # Modify the returned dict
        metaphors["Frontend"].append("Test Metaphor")

        # Original should be unchanged
        assert "Test Metaphor" not in generator.METAPHORS["Frontend"]

    def test_categories_coverage(self, generator: TitleGenerator) -> None:
        """Test that all expected categories are present."""
        expected_categories = [
            "Frontend",
            "Backend",
            "Database",
            "DevOps",
            "AI_ML",
            "Mobile",
            "Testing",
            "Cloud",
            "Other",
        ]

        categories = generator.get_categories()

        for expected in expected_categories:
            assert (
                expected in categories
            ), f"Expected category '{expected}' not found"
