"""
Technology mapping service.

Maps detected stars to technologies based on brightness/score correlation.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict

from services.star_detector import StarPosition

logger = logging.getLogger(__name__)


@dataclass
class TechData:
    """Technology data from TechAnalyzer."""

    name: str
    category: str
    color: str
    score: int
    size: str


@dataclass
class StarTechMapping:
    """Mapping between a star and a technology."""

    star: StarPosition
    tech: TechData

    def __repr__(self) -> str:
        """String representation."""
        return f"Mapping({self.tech.name} @ ({self.star.x}, {self.star.y}))"


class TechnologyMapper:
    """
    Map detected stars to technologies.

    Strategy: Brightest star → Highest score technology

    Example:
        >>> mapper = TechnologyMapper()
        >>> mappings = mapper.map(stars, technologies)
    """

    def __init__(self) -> None:
        """Initialize mapper."""
        logger.debug("TechnologyMapper initialized")

    def map(
        self, stars: list[StarPosition], technologies: list[Dict[str, Any]]
    ) -> list[StarTechMapping]:
        """
        Map stars to technologies by brightness/score.

        If more technologies than stars: limit to N brightest technologies
        If more stars than technologies: map only available technologies

        Args:
            stars: List of detected stars (sorted by brightness)
            technologies: List of technology dicts from TechAnalyzer

        Returns:
            List of StarTechMapping objects

        Example:
            >>> mappings = mapper.map(stars[:8], techs[:8])
            >>> print(mappings[0])  # Brightest star → highest score tech
        """
        if not stars:
            logger.warning("No stars provided for mapping")
            return []

        if not technologies:
            logger.warning("No technologies provided for mapping")
            return []

        # Convert technologies to TechData
        tech_data_list = [self._dict_to_tech_data(t) for t in technologies]

        # Sort technologies by score (descending)
        tech_data_list.sort(key=lambda t: t.score, reverse=True)

        # Determine mapping count
        mapping_count = min(len(stars), len(tech_data_list))

        if len(stars) > len(tech_data_list):
            logger.info(
                f"More stars ({len(stars)}) than technologies ({len(tech_data_list)})"
                f" - mapping top {mapping_count}"
            )
        elif len(tech_data_list) > len(stars):
            logger.info(
                f"More technologies ({len(tech_data_list)}) than stars ({len(stars)})"
                f" - using top {mapping_count} technologies"
            )

        # Create mappings (zip brightest stars with highest score techs)
        mappings: list[StarTechMapping] = []

        for i in range(mapping_count):
            mapping = StarTechMapping(star=stars[i], tech=tech_data_list[i])
            mappings.append(mapping)

        logger.info(f"Created {len(mappings)} star-technology mappings")

        # Log first 3 for debugging
        for i, mapping in enumerate(mappings[:3]):
            logger.debug(f"  Mapping {i+1}: {mapping}")

        return mappings

    def _dict_to_tech_data(self, tech_dict: Dict[str, Any]) -> TechData:
        """
        Convert technology dictionary to TechData object.

        Args:
            tech_dict: Technology dict from TechAnalyzer

        Returns:
            TechData object
        """
        return TechData(
            name=tech_dict["name"],
            category=tech_dict["category"],
            color=tech_dict["color"],
            score=tech_dict["score"],
            size=tech_dict["size"],
        )
