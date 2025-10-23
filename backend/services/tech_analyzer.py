"""
Service d'analyse sémantique de CV pour extraire les technologies.

Détecte les technologies mentionnées dans un CV et calcule des scores
basés sur la fréquence d'apparition.
"""
import re
from typing import Dict, List
from collections import Counter
from utils.tech_dictionary import (
    get_all_keywords,
    get_category_for_tech,
    get_color_for_tech,
)


class TechAnalyzer:
    """
    Analyse un CV et extrait les technologies mentionnées.

    Utilise le dictionnaire de technologies pour détecter les compétences
    et calcule des scores basés sur la fréquence.
    """

    def __init__(self):
        """Initialise l'analyseur avec le dictionnaire de technologies."""
        self.known_techs = get_all_keywords()

    def analyze(self, cv_text: str) -> Dict:
        """
        Analyse le CV et retourne les technologies trouvées.

        Args:
            cv_text: Texte brut du CV

        Returns:
            Dict avec technologies, scores et métadonnées

        Exemple:
            {
                "technologies": [
                    {
                        "name": "Angular",
                        "category": "Frontend",
                        "raw_count": 15,
                        "score": 100,
                        "size": "large",
                        "color": "#DD0031"
                    },
                    ...
                ],
                "stats": {
                    "total_technologies": 12,
                    "dominant_category": "Frontend",
                    "experience_level": "Senior",
                    "category_distribution": {...}
                }
            }
        """
        # Étape 1 : Compter les occurrences de chaque technologie
        tech_counts = self._count_tech_occurrences(cv_text)

        # Étape 2 : Enrichir avec métadonnées (catégorie, score, couleur)
        tech_details = self._enrich_tech_data(tech_counts)

        # Étape 3 : Calculer les statistiques globales
        stats = self._compute_stats(tech_details)

        return {
            "technologies": tech_details,
            "stats": stats,
            "total_techs_found": len(tech_details)
        }

    def _count_tech_occurrences(self, text: str) -> Counter:
        """
        Compte les occurrences de chaque technologie dans le texte.

        Utilise des regex avec word boundaries pour éviter les faux positifs.
        Exemple: "java" ne doit pas matcher dans "javascript"

        Args:
            text: Texte du CV

        Returns:
            Counter avec {technologie: nombre_occurrences}
        """
        tech_counter = Counter()
        text_lower = text.lower()

        for tech in self.known_techs:
            # Pattern avec word boundaries (\b)
            # \b assure qu'on matche des mots entiers
            # re.escape() échappe les caractères spéciaux (ex: "c++", ".net")
            pattern = r'\b' + re.escape(tech) + r'\b'

            # Trouve toutes les occurrences (case-insensitive)
            matches = re.findall(pattern, text_lower, re.IGNORECASE)

            if matches:
                tech_counter[tech] = len(matches)

        return tech_counter

    def _enrich_tech_data(self, tech_counts: Counter) -> List[Dict]:
        """
        Enrichit les données brutes avec catégorie, couleur, score normalisé.

        Le score est normalisé entre 0 et 100, avec 100 pour la technologie
        la plus fréquente.

        Args:
            tech_counts: Counter avec les occurrences brutes

        Returns:
            Liste de dicts avec toutes les métadonnées
        """
        if not tech_counts:
            return []

        # Trouve le maximum pour normaliser les scores
        max_count = max(tech_counts.values())

        tech_list = []

        # Trie par fréquence décroissante (most_common)
        for tech, count in tech_counts.most_common():
            # Récupère la catégorie depuis le dictionnaire
            category = get_category_for_tech(tech)

            # Calcule le score normalisé (0-100)
            normalized_score = int((count / max_count) * 100)

            # Détermine la taille de l'étoile pour la visualisation
            size = self._compute_star_size(normalized_score)

            # Récupère la couleur de la catégorie
            color = get_color_for_tech(tech)

            tech_list.append({
                "name": tech.title(),  # Capitalisation propre
                "category": category,
                "raw_count": count,
                "score": normalized_score,
                "size": size,
                "color": color
            })

        return tech_list

    def _compute_star_size(self, score: int) -> str:
        """
        Détermine la taille de l'étoile selon le score.

        Utilisé pour le rendu visuel de la constellation.

        Args:
            score: Score normalisé (0-100)

        Returns:
            Taille: "large", "medium", "small" ou "tiny"
        """
        if score >= 80:
            return "large"
        elif score >= 50:
            return "medium"
        elif score >= 20:
            return "small"
        else:
            return "tiny"

    def _compute_stats(self, tech_details: List[Dict]) -> Dict:
        """
        Calcule des statistiques globales sur le profil.

        - Nombre total de technologies
        - Catégorie dominante
        - Niveau d'expérience estimé
        - Distribution par catégories

        Args:
            tech_details: Liste des technologies enrichies

        Returns:
            Dict avec les statistiques
        """
        if not tech_details:
            return {
                "total_technologies": 0,
                "dominant_category": None,
                "experience_level": "Junior",
                "category_distribution": {}
            }

        # Compte les technologies par catégorie
        categories = [tech["category"] for tech in tech_details]
        category_counts = Counter(categories)

        # Catégorie dominante (la plus représentée)
        dominant_category = category_counts.most_common(1)[0][0]

        # Estimation du niveau basé sur le nombre de technologies
        total_techs = len(tech_details)
        if total_techs >= 20:
            level = "Expert"
        elif total_techs >= 12:
            level = "Senior"
        elif total_techs >= 6:
            level = "Intermediate"
        else:
            level = "Junior"

        return {
            "total_technologies": total_techs,
            "dominant_category": dominant_category,
            "experience_level": level,
            "category_distribution": dict(category_counts)
        }