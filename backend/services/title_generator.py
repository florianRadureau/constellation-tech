"""
Title generation service for constellation visualizations.

Generates poetic, profile-specific titles based on dominant technology category.
"""

import copy
import logging
import random
from typing import Any, ClassVar, Dict

logger = logging.getLogger(__name__)


class TitleGenerator:
    """
    Generate poetic titles based on technology profile.

    Titles are selected randomly from category-specific metaphor banks
    to create engaging, personality-driven constellation names.

    Example:
        >>> generator = TitleGenerator()
        >>> stats = {"dominant_category": "Frontend"}
        >>> title = generator.generate(stats)
        >>> print(title)  # "L'Architecte des Interfaces"
    """

    METAPHORS: ClassVar[Dict[str, list[str]]] = {
        "Frontend": [
            "L'Architecte des Interfaces",
            "Le Sculpteur Visuel",
            "Le Designer de l'Expérience",
            "L'Artiste du Frontend",
            "Le Créateur d'Interfaces Élégantes",
        ],
        "Backend": [
            "Le Bâtisseur de Systèmes",
            "L'Architecte Invisible",
            "L'Ingénieur des Fondations",
            "Le Maître des Serveurs",
            "L'Orchestrateur Backend",
        ],
        "Database": [
            "Le Gardien des Données",
            "L'Architecte des Structures",
            "Le Maître des Requêtes",
            "L'Organisateur de l'Information",
        ],
        "DevOps": [
            "Le Gardien de l'Infrastructure",
            "L'Automaticien des Déploiements",
            "L'Architecte Cloud",
            "Le Maître de la Pipeline",
            "L'Ingénieur de la Fiabilité",
        ],
        "AI_ML": [
            "Le Dompteur d'Algorithmes",
            "L'Explorateur de Données",
            "Le Visionnaire Analytique",
            "L'Architecte de l'Intelligence",
            "Le Sculpteur de Modèles",
        ],
        "Mobile": [
            "L'Artisan des Applications Mobiles",
            "Le Créateur d'Expériences Nomades",
            "L'Architecte Mobile",
            "Le Designer d'Interfaces Tactiles",
        ],
        "Testing": [
            "Le Gardien de la Qualité",
            "L'Architecte des Tests",
            "Le Maître de la Fiabilité",
            "L'Ingénieur QA",
        ],
        "Cloud": [
            "L'Architecte Cloud",
            "Le Maître des Nuages",
            "L'Ingénieur de l'Échelle",
            "L'Orchestrateur d'Infrastructure",
        ],
        "Other": [
            "Le Créateur Technologique",
            "L'Innovateur Numérique",
            "L'Ingénieur Polyvalent",
            "L'Architecte de Solutions",
        ],
    }

    FALLBACK_TITLE = "Le Créateur Technologique"

    def __init__(self, seed: int | None = None) -> None:
        """
        Initialize title generator.

        Args:
            seed: Random seed for reproducible titles (optional)
        """
        if seed is not None:
            random.seed(seed)

        logger.debug("TitleGenerator initialized")

    def generate(self, stats: Dict[str, Any]) -> str:
        """
        Generate a poetic title based on dominant category.

        Args:
            stats: Statistics dictionary containing 'dominant_category' key

        Returns:
            Poetic title string in French

        Example:
            >>> stats = {
            ...     "dominant_category": "Frontend",
            ...     "total_techs_found": 8,
            ...     "level": "Senior"
            ... }
            >>> title = generator.generate(stats)
            >>> assert "Frontend" in title or "Interface" in title
        """
        dominant_category = stats.get("dominant_category")

        if not dominant_category:
            logger.warning("No dominant_category in stats, using fallback title")
            return self.FALLBACK_TITLE

        # Get metaphors for category
        metaphors = self.METAPHORS.get(dominant_category)

        if not metaphors:
            logger.warning(
                f"Unknown category '{dominant_category}', using fallback title"
            )
            return self.FALLBACK_TITLE

        # Select random metaphor
        title = random.choice(metaphors)

        logger.info(f"Generated title for category '{dominant_category}': {title}")
        return title

    def generate_with_context(
        self, stats: Dict[str, Any], tech_count: int
    ) -> str:
        """
        Generate enriched title with technology count context.

        Args:
            stats: Statistics dictionary
            tech_count: Number of technologies detected

        Returns:
            Enriched title with count (e.g., "L'Architecte des 12 Technologies")
        """
        base_title = self.generate(stats)

        # Add context if significant number of technologies
        if tech_count >= 10:
            enriched = f"{base_title} ({tech_count} Technologies)"
            logger.info(f"Enriched title with count: {enriched}")
            return enriched

        return base_title

    def get_all_metaphors(self) -> Dict[str, list[str]]:
        """
        Get all available metaphors by category.

        Returns:
            Dictionary mapping categories to their metaphor lists (deep copy)

        Useful for testing and validation.
        """
        return copy.deepcopy(self.METAPHORS)

    def get_categories(self) -> list[str]:
        """
        Get list of supported categories.

        Returns:
            List of category names
        """
        return list(self.METAPHORS.keys())
