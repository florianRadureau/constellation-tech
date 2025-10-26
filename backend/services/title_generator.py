"""
Title generation service for constellation visualizations.

Generates evocative invented constellation names based on dominant technology category.
Titles use spatial metaphors (nebulas, forges, sanctuaries) for immersive experience.
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
        >>> print(title)  # "La Constellation du Pixel Parfait"
    """

    METAPHORS: ClassVar[Dict[str, list[str]]] = {
        "Fullstack": [
            "L'Architecte des Deux Mondes",
            "La Constellation Complète",
            "Le Pont Entre les Étoiles",
            "L'Équilibre Parfait du Code",
            "La Symphonie Full-Stack",
            "Le Tisseur d'Architectures",
        ],
        "Frontend": [
            "La Constellation du Pixel Parfait",
            "L'Étoile d'Argent des Interfaces",
            "La Nebula de l'Expérience Visuelle",
            "Les Forges Lumineuses du Frontend",
            "Le Sanctuaire des Écrans Enchantés",
        ],
        "Backend": [
            "Les Forges d'Orion Backend",
            "La Nebula des Architectures Invisibles",
            "Le Gardien de la Constellation Serveur",
            "L'Anneau Stellaire des API",
            "Les Piliers Cosmiques du Code",
        ],
        "Database": [
            "Le Sanctuaire des Données Éternelles",
            "La Constellation des Schémas Sacrés",
            "Les Coffres Stellaires de l'Information",
            "La Nebula des Requêtes Infinies",
            "Le Gardien de la Voie Lactée des Données",
        ],
        "DevOps": [
            "La Chaîne Stellaire DevOps",
            "Le Gardien des Voies Cosmiques",
            "La Constellation du Déploiement Continu",
            "Les Sentinelles de l'Infrastructure",
            "L'Anneau des Pipelines Automatiques",
        ],
        "AI_ML": [
            "La Nebula de l'Intelligence Artificielle",
            "Les Forges d'Algorithmes Quantiques",
            "La Constellation des Modèles Prédictifs",
            "Le Sanctuaire de l'Apprentissage Machine",
            "Les Éclaireurs de la Data Science",
        ],
        "Mobile": [
            "La Constellation des Interfaces Nomades",
            "L'Étoile Tactile du Mobile",
            "Les Navigateurs de l'Espace Portable",
            "La Nebula des Applications Mobiles",
            "Le Sanctuaire des Expériences Mobiles",
        ],
        "Testing": [
            "Le Gardien de la Qualité Stellaire",
            "La Constellation des Tests Infaillibles",
            "Les Sentinelles de la Fiabilité",
            "L'Anneau de Validation Continue",
            "Les Éclaireurs de la Qualité Code",
        ],
        "Cloud": [
            "La Nebula des Nuages Infinis",
            "Les Maîtres de l'Infrastructure Céleste",
            "La Constellation de l'Échelle Cosmique",
            "Les Gardiens de la Voûte Cloud",
            "L'Anneau des Services Distribués",
        ],
        "Other": [
            "La Constellation du Code Universel",
            "Les Forges de l'Innovation Numérique",
            "La Nebula des Solutions Hybrides",
            "Le Sanctuaire Technologique",
            "Les Navigateurs du Cosmos Digital",
        ],
    }

    FALLBACK_TITLE = "La Constellation du Code Universel"

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
