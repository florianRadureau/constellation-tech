#!/usr/bin/env python3
"""
Test isolé du positionnement des labels.

Visualise le placement des labels sur une constellation simple (noir sur blanc)
pour faciliter le débogage sans générer toute la constellation.
"""

import logging
from PIL import Image, ImageDraw

from services.star_detector import StarPosition
from services.technology_mapper import StarTechMapping, TechData
from services.text_overlay_service import TextOverlayService
from utils.constellation_templates import get_constellation_template

# Configure logging to show INFO level
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(name)s - %(message)s'
)


def main():
    """Test du positionnement des labels sur fond blanc."""
    print("🧪 TEST POSITIONNEMENT LABELS")
    print("=" * 60)

    # 1. Récupérer template Orion (index 0 - 7 étoiles)
    print("📐 Chargement template Orion...")
    template = get_constellation_template(0)
    star_positions = template["stars"]
    connections = template["connections"]
    print(f"   ✓ {len(star_positions)} étoiles, {len(connections)} connexions")

    # 2. Créer image blanche 1024x1024
    print("🖼️  Création image blanche 1024x1024...")
    image = Image.new("RGB", (1024, 1024), "white")
    draw = ImageDraw.Draw(image)

    # 3. Dessiner constellation (noir sur blanc)
    print("🎨 Dessin constellation...")

    # Lignes de connexion (noires, 2px)
    for conn in connections:
        x1, y1 = star_positions[conn[0]]
        x2, y2 = star_positions[conn[1]]
        draw.line([(x1, y1), (x2, y2)], fill="black", width=2)

    # Étoiles (cercles noirs, rayon 8px)
    for x, y in star_positions:
        draw.ellipse([(x - 8, y - 8), (x + 8, y + 8)], fill="black")

    print("   ✓ Constellation dessinée")

    # 4. Créer mappings avec 7 technologies (simule test_full_pipeline.py)
    print("⚙️  Création mappings technologies...")
    technologies = [
        {"name": "Angular", "category": "Frontend", "score": 100},
        {"name": "Javascript", "category": "Frontend", "score": 100},
        {"name": "Python", "category": "Backend", "score": 100},
        {"name": "Fastapi", "category": "Backend", "score": 100},
        {"name": "Postgresql", "category": "Database", "score": 100},
        {"name": "Docker", "category": "DevOps", "score": 100},
        {"name": "Kubernetes", "category": "DevOps", "score": 100},
    ]

    mappings = []
    for i, tech in enumerate(technologies):
        x, y = star_positions[i]
        star = StarPosition(x=x, y=y, brightness=255, color=(0, 0, 0), size=20)
        tech_data = TechData(
            name=tech["name"],
            category=tech["category"],
            color="#000000",
            score=tech["score"],
            size="medium",
        )
        mappings.append(StarTechMapping(star=star, tech=tech_data))

    print(f"   ✓ {len(mappings)} mappings créés")

    # 5. Appeler compose()
    print("🏷️  Ajout des labels via TextOverlayService.compose()...")
    title = "Test Placement Labels"
    overlay_service = TextOverlayService()
    result = overlay_service.compose(image, mappings, title, connections, star_positions)
    print("   ✓ Labels ajoutés")

    # 6. Sauvegarder
    output_file = "test_overlay_output.png"
    result.save(output_file)
    print()
    print("=" * 60)
    print(f"✅ Image générée: {output_file}")
    print()
    print("Contenu de l'image:")
    print("  - Fond: blanc")
    print("  - Étoiles: cercles noirs (8px rayon)")
    print("  - Connexions: lignes noires (2px)")
    print("  - Labels: texte avec fond gris")
    print("  - Titre: en haut")
    print("  - Watermark: en bas")
    print("=" * 60)


if __name__ == "__main__":
    main()
