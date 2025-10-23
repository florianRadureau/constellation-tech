"""
Unit tests for PromptGenerator service.
"""

import pytest

from services.prompt_generator import PromptGenerator


class TestPromptGenerator:
    """Test suite for PromptGenerator."""

    @pytest.fixture
    def generator(self) -> PromptGenerator:
        """Create a PromptGenerator instance."""
        return PromptGenerator()

    def test_initialization(self, generator: PromptGenerator) -> None:
        """Test that generator initializes correctly."""
        assert generator is not None

    def test_generate_basic_prompt(self, generator: PromptGenerator) -> None:
        """Test basic prompt generation."""
        prompt = generator.generate(tech_count=7, dominant_category="Frontend")

        assert isinstance(prompt, str)
        assert "7 bright stars" in prompt
        assert len(prompt) > 0

    def test_generate_frontend_prompt(self, generator: PromptGenerator) -> None:
        """Test prompt generation for Frontend category."""
        prompt = generator.generate(tech_count=8, dominant_category="Frontend")

        assert "8 bright stars" in prompt
        assert "warm colors" in prompt or "red" in prompt or "orange" in prompt

    def test_generate_backend_prompt(self, generator: PromptGenerator) -> None:
        """Test prompt generation for Backend category."""
        prompt = generator.generate(tech_count=10, dominant_category="Backend")

        assert "10 bright stars" in prompt
        assert "cool colors" in prompt or "blue" in prompt or "teal" in prompt

    def test_generate_ai_ml_prompt(self, generator: PromptGenerator) -> None:
        """Test prompt generation for AI_ML category."""
        prompt = generator.generate(tech_count=6, dominant_category="AI_ML")

        assert "6 bright stars" in prompt
        assert "vibrant" in prompt or "purple" in prompt or "magenta" in prompt

    def test_tech_count_minimum_constraint(self, generator: PromptGenerator) -> None:
        """Test that tech_count is constrained to minimum 3."""
        prompt = generator.generate(tech_count=1, dominant_category="Frontend")

        # Should be adjusted to 3
        assert "3 bright stars" in prompt

    def test_tech_count_maximum_constraint(self, generator: PromptGenerator) -> None:
        """Test that tech_count is constrained to maximum 15."""
        prompt = generator.generate(tech_count=20, dominant_category="Backend")

        # Should be adjusted to 15
        assert "15 bright stars" in prompt

    def test_unknown_category_fallback(self, generator: PromptGenerator) -> None:
        """Test fallback for unknown category."""
        prompt = generator.generate(
            tech_count=7, dominant_category="UnknownCategory"
        )

        assert "7 bright stars" in prompt
        # Should use "Other" category colors (multicolor)
        assert "multicolor" in prompt

    def test_generate_from_stats(self, generator: PromptGenerator) -> None:
        """Test prompt generation from stats dictionary."""
        stats = {"dominant_category": "DevOps", "total_techs_found": 9}

        prompt = generator.generate_from_stats(stats, tech_count=9)

        assert "9 bright stars" in prompt
        assert "DevOps" not in prompt  # Category shouldn't be in prompt text
        # But colors should match DevOps
        assert "technical" in prompt or "blue" in prompt or "green" in prompt

    def test_generate_from_stats_missing_category(
        self, generator: PromptGenerator
    ) -> None:
        """Test prompt generation from stats without dominant_category."""
        stats = {"total_techs_found": 5}

        prompt = generator.generate_from_stats(stats, tech_count=5)

        assert "5 bright stars" in prompt
        # Should use fallback (Other)
        assert "multicolor" in prompt

    def test_generate_simple(self, generator: PromptGenerator) -> None:
        """Test simple prompt generation without category hints."""
        prompt = generator.generate_simple(tech_count=8)

        assert "8 bright stars" in prompt
        assert "constellation" in prompt.lower()
        # Should not have specific color hints
        assert "warm" not in prompt
        assert "cool" not in prompt

    def test_style_variations(self, generator: PromptGenerator) -> None:
        """Test that different style indices produce different styles."""
        prompts = [
            generator.generate(7, "Frontend", style_index=i) for i in range(4)
        ]

        # All should have the tech count
        for prompt in prompts:
            assert "7 bright stars" in prompt

        # Styles should vary
        unique_prompts = set(prompts)
        assert len(unique_prompts) == 4

    def test_prompt_length_validation_pass(self, generator: PromptGenerator) -> None:
        """Test that normal prompts pass length validation."""
        prompt = generator.generate(tech_count=10, dominant_category="Frontend")

        assert generator.validate_prompt_length(prompt) is True
        assert len(prompt) < 500

    def test_prompt_length_validation_fail(self, generator: PromptGenerator) -> None:
        """Test length validation fails for very long prompts."""
        long_prompt = "x" * 600  # Artificially long

        assert generator.validate_prompt_length(long_prompt) is False

    def test_get_color_hints(self, generator: PromptGenerator) -> None:
        """Test retrieval of all color hints."""
        color_hints = generator.get_color_hints()

        assert isinstance(color_hints, dict)
        assert "Frontend" in color_hints
        assert "Backend" in color_hints
        assert "AI_ML" in color_hints
        assert len(color_hints) > 0

    def test_all_categories_have_colors(self, generator: PromptGenerator) -> None:
        """Test that all categories have color definitions."""
        categories = [
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

        for category in categories:
            assert (
                category in generator.CATEGORY_COLORS
            ), f"Missing colors for {category}"
            colors = generator.CATEGORY_COLORS[category]
            assert isinstance(colors, str)
            assert len(colors) > 0

    def test_prompt_contains_required_elements(
        self, generator: PromptGenerator
    ) -> None:
        """Test that generated prompts contain all required elements."""
        prompt = generator.generate(tech_count=12, dominant_category="Backend")

        # Required elements
        assert "constellation" in prompt.lower()
        assert "stars" in prompt
        assert "12" in prompt
        assert "background" in prompt.lower() or "nebula" in prompt.lower()

    def test_generate_various_tech_counts(self, generator: PromptGenerator) -> None:
        """Test prompt generation with various tech counts."""
        for count in [3, 5, 7, 10, 12, 15]:
            prompt = generator.generate(tech_count=count, dominant_category="Frontend")

            assert f"{count} bright stars" in prompt
            assert len(prompt) > 0
            assert generator.validate_prompt_length(prompt)
