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
    "pegasus": {
        "name": "Pégase",
        "stars": [
            (220, 320),  # 0: Angle haut-gauche (Markab)
            (780, 300),  # 1: Angle haut-droit (Scheat)
            (800, 720),  # 2: Angle bas-droit (Algenib)
            (260, 740),  # 3: Angle bas-gauche (Alpheratz)
            (520, 180),  # 4: Tête/encolure
            (650, 220),  # 5: Cou
            (350, 550),  # 6: Corps centre
            (480, 620),  # 7: Ventre
        ],
        "connections": [
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 0),  # Grand carré de Pégase
            (1, 5),
            (5, 4),  # Encolure
            (0, 6),
            (6, 7),  # Corps
        ],
        "center": (512, 500),
    },
    "cygnus": {
        "name": "Cygne",
        "stars": [
            (512, 150),  # 0: Queue (Deneb)
            (512, 350),  # 1: Corps centre
            (512, 550),  # 2: Cou
            (512, 750),  # 3: Tête (Albireo)
            (250, 380),  # 4: Aile gauche
            (380, 320),  # 5: Aile gauche intérieure
            (644, 320),  # 6: Aile droite intérieure
            (774, 380),  # 7: Aile droite
            (400, 600),  # 8: Patte gauche
        ],
        "connections": [
            (0, 1),
            (1, 2),
            (2, 3),  # Corps central (Croix du Nord)
            (4, 5),
            (5, 1),
            (1, 6),
            (6, 7),  # Ailes
            (2, 8),  # Patte
        ],
        "center": (512, 450),
    },
    "draco": {
        "name": "Dragon",
        "stars": [
            (400, 800),  # 0: Queue extrémité
            (480, 720),  # 1: Queue milieu
            (580, 650),  # 2: Queue base
            (650, 550),  # 3: Corps bas
            (700, 420),  # 4: Corps milieu
            (680, 280),  # 5: Corps haut
            (580, 180),  # 6: Cou
            (450, 150),  # 7: Tête (Thuban)
        ],
        "connections": [
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 4),
            (4, 5),
            (5, 6),
            (6, 7),  # Serpentement du dragon
        ],
        "center": (565, 465),
    },
    "lyra": {
        "name": "Lyre",
        "stars": [
            (512, 200),  # 0: Véga (étoile brillante)
            (420, 350),  # 1: Base gauche de la lyre
            (604, 350),  # 2: Base droite de la lyre
            (460, 520),  # 3: Corde gauche bas
            (564, 520),  # 4: Corde droite bas
        ],
        "connections": [
            (0, 1),
            (0, 2),  # Branches de la lyre
            (1, 3),
            (2, 4),  # Cordes
            (3, 4),  # Base
        ],
        "center": (512, 360),
    },
    "aquila": {
        "name": "Aigle",
        "stars": [
            (512, 250),  # 0: Tête
            (420, 380),  # 1: Aile gauche
            (512, 450),  # 2: Altaïr (corps centre)
            (604, 380),  # 3: Aile droite
            (480, 620),  # 4: Queue gauche
            (512, 680),  # 5: Queue centre
            (544, 620),  # 6: Queue droite
        ],
        "connections": [
            (0, 2),  # Tête au corps
            (1, 2),
            (2, 3),  # Ailes
            (2, 5),  # Corps à queue
            (4, 5),
            (5, 6),  # Plumes de la queue
        ],
        "center": (512, 465),
    },
    "scorpius": {
        "name": "Scorpion",
        "stars": [
            (200, 400),  # 0: Pinces gauche haut
            (250, 500),  # 1: Pinces gauche bas
            (350, 450),  # 2: Tête
            (450, 420),  # 3: Antares (cœur)
            (520, 450),  # 4: Corps 1
            (580, 500),  # 5: Corps 2
            (650, 560),  # 6: Corps 3
            (700, 640),  # 7: Queue 1
            (730, 730),  # 8: Queue 2
            (780, 800),  # 9: Dard
            (200, 300),  # 10: Pince droite haut
            (250, 350),  # 11: Pince droite bas
        ],
        "connections": [
            (0, 2),
            (1, 2),  # Pinces gauches
            (10, 2),
            (11, 2),  # Pinces droites
            (2, 3),
            (3, 4),
            (4, 5),
            (5, 6),
            (6, 7),
            (7, 8),
            (8, 9),  # Corps et queue
        ],
        "center": (490, 540),
    },
    "leo": {
        "name": "Lion",
        "stars": [
            (300, 350),  # 0: Tête (Régulus)
            (420, 320),  # 1: Cou
            (540, 280),  # 2: Épaule
            (650, 320),  # 3: Dos milieu
            (750, 400),  # 4: Dos arrière
            (700, 550),  # 5: Queue début
            (780, 650),  # 6: Queue bout
            (480, 480),  # 7: Ventre
            (380, 520),  # 8: Patte avant
        ],
        "connections": [
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 4),  # Ligne du dos
            (4, 5),
            (5, 6),  # Queue
            (2, 7),
            (0, 8),  # Ventre et pattes
        ],
        "center": (540, 430),
    },
    "andromeda": {
        "name": "Andromède",
        "stars": [
            (300, 400),  # 0: Alpheratz (tête)
            (420, 380),  # 1: Mirach
            (560, 340),  # 2: Milieu
            (680, 300),  # 3: Corps
            (400, 550),  # 4: Bras gauche
            (540, 520),  # 5: Hanche
            (450, 700),  # 6: Jambe gauche
            (640, 680),  # 7: Jambe droite
        ],
        "connections": [
            (0, 1),
            (1, 2),
            (2, 3),  # Corps principal
            (1, 4),
            (4, 6),  # Bras et jambe gauche
            (2, 5),
            (5, 7),  # Hanche et jambe droite
        ],
        "center": (495, 490),
    },
    "perseus": {
        "name": "Persée",
        "stars": [
            (450, 200),  # 0: Tête (Mirfak)
            (520, 320),  # 1: Épaule
            (600, 420),  # 2: Bras droit
            (680, 520),  # 3: Épée
            (420, 400),  # 4: Bras gauche (tenant Méduse)
            (350, 500),  # 5: Méduse
            (480, 550),  # 6: Hanche
            (440, 680),  # 7: Jambe gauche
            (560, 720),  # 8: Jambe droite
            (520, 480),  # 9: Torse centre
        ],
        "connections": [
            (0, 1),  # Tête à épaule
            (1, 2),
            (2, 3),  # Bras droit avec épée
            (1, 4),
            (4, 5),  # Bras gauche tenant Méduse
            (1, 9),
            (9, 6),  # Torse
            (6, 7),
            (6, 8),  # Jambes
        ],
        "center": (505, 460),
    },
    "gemini": {
        "name": "Gémeaux",
        "stars": [
            (350, 250),  # 0: Castor (tête gauche)
            (650, 230),  # 1: Pollux (tête droite)
            (320, 380),  # 2: Épaule gauche
            (680, 360),  # 3: Épaule droite
            (300, 550),  # 4: Hanche gauche
            (700, 530),  # 5: Hanche droite
            (280, 720),  # 6: Pied gauche
            (720, 700),  # 7: Pied droit
        ],
        "connections": [
            (0, 2),
            (2, 4),
            (4, 6),  # Jumeau gauche (Castor)
            (1, 3),
            (3, 5),
            (5, 7),  # Jumeau droit (Pollux)
            (2, 3),  # Épaules liées
        ],
        "center": (500, 475),
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
