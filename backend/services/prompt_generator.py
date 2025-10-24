"""
Prompt generation service for Vertex AI Imagen.

Generates ultra-simple, effective prompts for beautiful constellation images.
"""

import logging
from typing import Any, ClassVar, Dict

logger = logging.getLogger(__name__)


class PromptGenerator:
    """
    Generate minimal, effective prompts for Imagen constellation generation.

    Philosophy: Simple prompts → Beautiful results
    Imagen excels at natural language, so we keep prompts concise and evocative.

    Example:
        >>> generator = PromptGenerator()
        >>> prompt = generator.generate(tech_count=7, dominant_category="Frontend")
        >>> print(prompt)
        Beautiful cosmic constellation with 7 bright stars...
    """

    # Color hints by category for visual consistency
    CATEGORY_COLORS: ClassVar[Dict[str, str]] = {
        "Frontend": "warm colors (red, orange, gold)",
        "Backend": "cool colors (blue, teal, cyan)",
        "Database": "structured colors (blue, purple, silver)",
        "DevOps": "technical colors (blue, green, cyan)",
        "AI_ML": "vibrant colors (purple, magenta, pink)",
        "Mobile": "dynamic colors (blue, green, orange)",
        "Testing": "precise colors (green, blue, white)",
        "Cloud": "ethereal colors (white, blue, cyan)",
        "Other": "multicolor spectrum",
    }

    # Base template for all prompts
    BASE_TEMPLATE = """Beautiful cosmic constellation with {tech_count} bright stars.
Stars of various sizes, connected with thin elegant luminous lines.
{color_hint}
Magnificent deep space nebula background.
Professional, stunning, captivating, high quality."""

    # Alternative variations for diversity
    STYLE_VARIATIONS: ClassVar[list[str]] = [
        "Professional, stunning, captivating, high quality.",
        "Breathtaking, elegant, professional quality.",
        "Impressive, sophisticated, premium quality.",
        "Stunning professional visualization, high quality.",
    ]

    def __init__(self) -> None:
        """Initialize prompt generator."""
        logger.debug("PromptGenerator initialized")

    def generate(
        self,
        tech_count: int,
        dominant_category: str = "Other",
        style_index: int = 0,
    ) -> str:
        """
        Generate a simple prompt for constellation image generation.

        Args:
            tech_count: Number of technologies/stars to generate
            dominant_category: Dominant tech category for color hints
            style_index: Style variation index (0-3)

        Returns:
            Prompt string optimized for Vertex AI Imagen

        Example:
            >>> generator = PromptGenerator()
            >>> prompt = generator.generate(8, "Backend")
            >>> assert "8 bright stars" in prompt
            >>> assert "cool colors" in prompt
        """
        # Ensure tech_count is reasonable (Imagen works best with 3-15 stars)
        if tech_count < 3:
            logger.warning(f"Tech count {tech_count} is low, setting to 3")
            tech_count = 3
        elif tech_count > 15:
            logger.warning(f"Tech count {tech_count} is high, setting to 15")
            tech_count = 15

        # Get color hint for category
        color_hint = self.CATEGORY_COLORS.get(dominant_category)
        if not color_hint:
            logger.warning(
                f"Unknown category '{dominant_category}', using 'Other'"
            )
            color_hint = self.CATEGORY_COLORS["Other"]

        # Build color line
        color_line = f"Colors: {color_hint}."

        # Select style variation
        style = self.STYLE_VARIATIONS[style_index % len(self.STYLE_VARIATIONS)]

        # Generate prompt
        prompt = self.BASE_TEMPLATE.format(
            tech_count=tech_count, color_hint=color_line
        )

        # Replace default style with selected variation
        prompt = prompt.replace(
            "Professional, stunning, captivating, high quality.", style
        )

        logger.info(
            f"Generated prompt for {tech_count} technologies, category '{dominant_category}'"
        )
        logger.debug(f"Prompt: {prompt[:100]}...")

        return prompt

    def generate_from_stats(self, stats: Dict[str, Any], tech_count: int) -> str:
        """
        Generate prompt directly from TechAnalyzer stats.

        Args:
            stats: Statistics from TechAnalyzer
            tech_count: Number of technologies

        Returns:
            Generated prompt string

        Example:
            >>> stats = {"dominant_category": "Frontend", "total_techs_found": 8}
            >>> prompt = generator.generate_from_stats(stats, tech_count=8)
        """
        dominant_category = stats.get("dominant_category", "Other")
        return self.generate(tech_count, dominant_category)

    def generate_simple(self, tech_count: int) -> str:
        """
        Generate ultra-simple prompt without category hints.

        Useful for maximum Imagen creativity without constraints.

        Args:
            tech_count: Number of stars

        Returns:
            Minimal prompt string
        """
        prompt = f"""Beautiful cosmic constellation with {tech_count} bright stars.
Stars of various sizes, connected with elegant lines.
Magnificent nebula background.
Stunning, professional, high quality."""

        logger.info(f"Generated simple prompt for {tech_count} stars")
        return prompt

    def generate_background_only(self, dominant_category: str = "Other") -> str:
        """
        Generate prompt for nebula background WITHOUT stars or lines.

        Used in the new deterministic architecture where constellation
        positions are pre-calculated. Imagen generates only the nebula
        background, then we compose stars and lines manually.

        Args:
            dominant_category: Dominant tech category for color hints

        Returns:
            Prompt string for pure nebula background

        Example:
            >>> generator = PromptGenerator()
            >>> prompt = generator.generate_background_only("Backend")
            >>> print(prompt)
            Beautiful deep space nebula background...
        """
        # Get color hint for category
        color_hint = self.CATEGORY_COLORS.get(
            dominant_category, self.CATEGORY_COLORS["Other"]
        )

        prompt = f"""Beautiful deep space nebula background.
Magnificent cosmic nebula with {color_hint}.
Rich colors, swirling gas clouds, cosmic dust.
No stars, no constellations, just pure nebula.
Professional, stunning, high quality."""

        logger.info(
            f"Generated background-only prompt for category '{dominant_category}'"
        )
        logger.debug(f"Prompt: {prompt[:100]}...")

        return prompt

    def get_color_hints(self) -> Dict[str, str]:
        """
        Get all available color hints by category.

        Returns:
            Dictionary of category -> color hints
        """
        return self.CATEGORY_COLORS.copy()

    def validate_prompt_length(self, prompt: str) -> bool:
        """
        Validate that prompt is within Imagen's optimal length.

        Imagen works best with prompts < 500 characters.

        Args:
            prompt: Prompt to validate

        Returns:
            True if length is acceptable
        """
        max_length = 500
        prompt_length = len(prompt)

        if prompt_length > max_length:
            logger.warning(
                f"Prompt length {prompt_length} exceeds recommended {max_length}"
            )
            return False

        logger.debug(f"Prompt length {prompt_length} is valid")
        return True
