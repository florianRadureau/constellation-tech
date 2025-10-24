"""
Pre-calculated constellation templates with star positions and connections.

Each template defines a deterministic constellation pattern that can be
used to position technology labels in a beautiful, predictable way.
"""

from typing import TypedDict


class ConstellationTemplate(TypedDict):
    """
    Template for a constellation pattern.

    Attributes:
        name: Display name of the constellation
        stars: List of (x, y) positions for each star (0-indexed)
        connections: List of (star_idx1, star_idx2) tuples defining lines between stars
        center: (x, y) center point of the constellation for positioning
    """

    name: str
    stars: list[tuple[int, int]]
    connections: list[tuple[int, int]]
    center: tuple[int, int]


# Pre-calculated constellation templates
# Canvas size: 1024x1024
# Positions are carefully chosen for visual balance and professional appearance
CONSTELLATIONS: dict[str, ConstellationTemplate] = {
    "orion": {
        "name": "Orion",
        "stars": [
            (300, 200),  # 0: Épaule gauche (Betelgeuse)
            (700, 180),  # 1: Épaule droite (Bellatrix)
            (350, 400),  # 2: Ceinture gauche (Alnitak)
            (512, 420),  # 3: Ceinture centre (Alnilam)
            (650, 400),  # 4: Ceinture droite (Mintaka)
            (280, 750),  # 5: Pied gauche (Rigel)
            (720, 780),  # 6: Pied droit (Saiph)
        ],
        "connections": [
            (0, 2),
            (1, 4),  # Épaules → Ceinture
            (2, 3),
            (3, 4),  # Ceinture horizontale
            (2, 5),
            (4, 6),  # Ceinture → Pieds
        ],
        "center": (512, 490),
    },
    "cassiopeia": {
        "name": "Cassiopée",
        "stars": [
            (150, 512),  # 0: Gauche (bas)
            (350, 300),  # 1: Montée
            (512, 450),  # 2: Centre (bas)
            (670, 250),  # 3: Descente
            (870, 480),  # 4: Droite (bas)
        ],
        "connections": [
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 4),  # Zigzag caractéristique en W
        ],
        "center": (512, 398),
    },
    "ursa_major": {
        "name": "Grande Ourse",
        "stars": [
            (200, 280),  # 0: Queue (première)
            (320, 260),  # 1: Queue (seconde)
            (450, 300),  # 2: Queue (troisième)
            (550, 260),  # 3: Corps gauche haut
            (800, 320),  # 4: Corps droite haut
            (720, 580),  # 5: Corps droite bas
            (500, 550),  # 6: Corps gauche bas
        ],
        "connections": [
            (0, 1),
            (1, 2),
            (2, 3),  # Queue (3 étoiles)
            (3, 4),  # Haut du corps
            (4, 5),  # Côté droit
            (5, 6),  # Bas du corps
            (6, 3),  # Côté gauche (ferme le carré)
        ],
        "center": (512, 405),
    },
}


def get_constellation_template(index: int) -> ConstellationTemplate:
    """
    Get constellation template by index.

    Cycles through available templates using modulo to ensure
    deterministic selection even with many CVs.

    Args:
        index: Index number (e.g., hash of CV content)

    Returns:
        ConstellationTemplate dict

    Example:
        >>> template = get_constellation_template(0)
        >>> print(template["name"])
        Orion
        >>> print(len(template["stars"]))
        7
    """
    templates = list(CONSTELLATIONS.values())
    return templates[index % len(templates)]


def get_available_constellations() -> list[str]:
    """
    Get list of available constellation names.

    Returns:
        List of constellation keys

    Example:
        >>> constellations = get_available_constellations()
        >>> print(constellations)
        ['orion', 'cassiopeia', 'ursa_major']
    """
    return list(CONSTELLATIONS.keys())
