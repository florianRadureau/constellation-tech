#!/usr/bin/env python3
"""
Test complet du pipeline avec un CV réel.

Génère une constellation à partir de cv_example.pdf et affiche le résultat.
"""

import asyncio
import sys
from pathlib import Path

from services.constellation_orchestrator import ConstellationOrchestrator


async def main():
    """Test du pipeline complet."""
    print("=" * 80)
    print("🧪 TEST PIPELINE COMPLET - CONSTELLATION TECH")
    print("=" * 80)
    print()

    # Vérifier que le CV existe
    cv_path = Path("tests/fixtures/sample_cv.pdf")
    if not cv_path.exists():
        print(f"❌ Fichier {cv_path} introuvable")
        print("Essayons avec cv_example.pdf...")
        cv_path = Path("cv_example.pdf")
        if not cv_path.exists():
            print(f"❌ Aucun CV trouvé")
            sys.exit(1)

    print(f"📄 CV: {cv_path}")
    print(f"   Taille: {cv_path.stat().st_size / 1024:.1f} KB")
    print()

    # Lire le CV
    with open(cv_path, "rb") as f:
        cv_content = f.read()

    # Créer l'orchestrateur
    print("🔧 Initialisation de l'orchestrateur...")
    orchestrator = ConstellationOrchestrator()
    print()

    # Générer la constellation
    print("🚀 Génération de la constellation...")
    print("=" * 80)

    try:
        result = await orchestrator.generate(cv_content, cv_path.name)

        print()
        print("=" * 80)
        print("✅ GÉNÉRATION RÉUSSIE !")
        print("=" * 80)
        print()
        print(f"📊 Résultats:")
        print(f"   Titre: {result.title}")
        print(f"   Technologies détectées: {len(result.technologies)}")
        print(f"   Étoiles dans la constellation: {result.stars_detected}")
        print(f"   Temps de génération: {result.generation_time:.2f}s")
        print(f"   Niveau: {result.stats.get('level', 'N/A')}")
        print(f"   Catégorie dominante: {result.stats.get('dominant_category', 'N/A')}")
        print()
        print(f"🔗 URL de l'image:")
        print(f"   {result.image_url}")
        print()

        # Afficher top 10 technologies
        print("🏆 Top 10 Technologies:")
        for i, tech in enumerate(result.technologies[:10], 1):
            print(f"   {i:2}. {tech['name']:20} - Score: {tech['score']:3} - {tech['category']}")
        print()

        # Statistiques par catégorie
        print("📈 Répartition par catégorie:")
        categories = result.stats.get('categories_count', {})
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                print(f"   {cat:15} : {count:2} technologies")
        print()

        print("=" * 80)
        print(f"💾 Pour télécharger l'image:")
        print(f"   wget '{result.image_url}' -O constellation_result.png")
        print("=" * 80)

    except Exception as e:
        print()
        print("=" * 80)
        print(f"❌ ERREUR lors de la génération")
        print(f"   {type(e).__name__}: {e}")
        print("=" * 80)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
