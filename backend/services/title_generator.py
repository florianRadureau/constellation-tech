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
            "Le Maître des Galaxies Connectées",
            "La Fusion des Mondes Frontend-Backend",
            "L'Oracle de l'Architecture Totale",
            "Les Gardiens du Stack Universel",
            "La Voie Lactée du Code Complet",
            "Le Nexus des Compétences Infinies",
        ],
        "Frontend": [
            "La Constellation du Pixel Parfait",
            "L'Étoile d'Argent des Interfaces",
            "La Nebula de l'Expérience Visuelle",
            "Les Forges Lumineuses du Frontend",
            "Le Sanctuaire des Écrans Enchantés",
            "Les Tisserands de l'Interface Céleste",
            "La Galaxie des Pixels Animés",
            "Le Temple de l'Expérience Utilisateur",
            "Les Magiciens de la Réactivité",
            "L'Atelier des Écrans Interactifs",
            "La Constellation des Composants",
            "Les Artisans du Rendu Visuel",
        ],
        "Backend": [
            "Les Forges d'Orion Backend",
            "La Nebula des Architectures Invisibles",
            "Le Gardien de la Constellation Serveur",
            "L'Anneau Stellaire des API",
            "Les Piliers Cosmiques du Code",
            "Les Architectes de l'Invisible",
            "La Citadelle des Serveurs",
            "Le Réseau Neuronal des Microservices",
            "Les Gardiens du Cache Cosmique",
            "L'Écosystème des Endpoints",
            "Les Bâtisseurs de Logique Serveur",
            "La Matrice des Traitements Asynchrones",
        ],
        "Database": [
            "Le Sanctuaire des Données Éternelles",
            "La Constellation des Schémas Sacrés",
            "Les Coffres Stellaires de l'Information",
            "La Nebula des Requêtes Infinies",
            "Le Gardien de la Voie Lactée des Données",
            "L'Univers des Transactions ACID",
            "Les Maîtres des Index Galactiques",
            "Le Temple des Relations Éternelles",
            "La Bibliothèque Cosmique du Stockage",
            "Les Architectes des Schémas NoSQL",
            "La Forteresse des Données Persistantes",
            "Le Réseau des Réplications Stellaires",
        ],
        "DevOps": [
            "La Chaîne Stellaire DevOps",
            "Le Gardien des Voies Cosmiques",
            "La Constellation du Déploiement Continu",
            "Les Sentinelles de l'Infrastructure",
            "L'Anneau des Pipelines Automatiques",
            "Les Orchestrateurs des Conteneurs Spatiaux",
            "La Nebula de l'Automatisation",
            "Le Réseau des Déploiements Instantanés",
            "Les Gardiens du Monitoring Stellaire",
            "L'Écosystème CI/CD Galactique",
            "Les Maîtres de l'Infrastructure as Code",
            "La Voie de la Livraison Continue",
        ],
        "AI_ML": [
            "La Nebula de l'Intelligence Artificielle",
            "Les Forges d'Algorithmes Quantiques",
            "La Constellation des Modèles Prédictifs",
            "Le Sanctuaire de l'Apprentissage Machine",
            "Les Éclaireurs de la Data Science",
            "Les Architectes des Réseaux Neuronaux",
            "La Matrice des Transformers Cosmiques",
            "Le Temple du Deep Learning",
            "Les Alchimistes des Données",
            "La Galaxie des Modèles Génératifs",
            "Les Maîtres du Gradient Descent",
            "L'Univers de l'Intelligence Augmentée",
        ],
        "Mobile": [
            "La Constellation des Interfaces Nomades",
            "L'Étoile Tactile du Mobile",
            "Les Navigateurs de l'Espace Portable",
            "La Nebula des Applications Mobiles",
            "Le Sanctuaire des Expériences Mobiles",
            "Les Artisans des Écrans Tactiles",
            "La Galaxie des Apps Natives",
            "Le Réseau des Expériences Hybrides",
            "Les Maîtres du Responsive Design",
            "L'Univers des Progressive Web Apps",
            "Les Architectes Cross-Platform",
            "La Voie des Interfaces Gestuelles",
        ],
        "Testing": [
            "Le Gardien de la Qualité Stellaire",
            "La Constellation des Tests Infaillibles",
            "Les Sentinelles de la Fiabilité",
            "L'Anneau de Validation Continue",
            "Les Éclaireurs de la Qualité Code",
            "Les Architectes des Test Suites",
            "La Nebula du Test-Driven Development",
            "Le Réseau des Assertions Cosmiques",
            "Les Maîtres de la Couverture Totale",
            "L'Univers des Tests End-to-End",
            "Les Gardiens de la Non-Régression",
            "La Voie de l'Assurance Qualité",
        ],
        "Cloud": [
            "La Nebula des Nuages Infinis",
            "Les Maîtres de l'Infrastructure Céleste",
            "La Constellation de l'Échelle Cosmique",
            "Les Gardiens de la Voûte Cloud",
            "L'Anneau des Services Distribués",
            "Les Architectes du Multi-Cloud",
            "La Galaxie des Serverless Functions",
            "Le Réseau des Instances Élastiques",
            "Les Orchestrateurs des Clusters Kubernetes",
            "L'Univers de l'Abstraction Cloud",
            "Les Maîtres de la Scalabilité Infinie",
            "La Voie de l'Infrastructure Immuable",
        ],
        "Other": [
            "La Constellation du Code Universel",
            "Les Forges de l'Innovation Numérique",
            "La Nebula des Solutions Hybrides",
            "Le Sanctuaire Technologique",
            "Les Navigateurs du Cosmos Digital",
            "Les Pionniers des Technologies Émergentes",
            "La Galaxie des Compétences Polyvalentes",
            "Le Réseau des Savoirs Interconnectés",
            "Les Explorateurs du Code Multidisciplinaire",
            "L'Univers des Innovations Disruptives",
            "Les Architectes du Futur Numérique",
            "La Voie de la Maîtrise Technique",
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
