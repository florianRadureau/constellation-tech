"""
Tests unitaires pour le service TechAnalyzer.
"""
import pytest
from services.tech_analyzer import TechAnalyzer


class TestTechAnalyzer:
    """Tests de base pour TechAnalyzer."""

    def test_analyzer_initialization(self):
        """Test que l'analyseur s'initialise correctement."""
        analyzer = TechAnalyzer()
        assert len(analyzer.known_techs) > 300  # Au moins 300 technos

    def test_analyze_simple_text(self):
        """Test analyse d'un texte simple."""
        analyzer = TechAnalyzer()
        text = "I have experience with Python, Angular and Docker."

        result = analyzer.analyze(text)

        # Vérifie la structure du résultat
        assert "technologies" in result
        assert "stats" in result
        assert isinstance(result["technologies"], list)
        assert len(result["technologies"]) >= 3  # Au moins Python, Angular, Docker

    def test_detect_python(self):
        """Test détection de Python."""
        analyzer = TechAnalyzer()
        text = "Python developer with 5 years experience in Python."

        result = analyzer.analyze(text)

        # Trouve Python dans les résultats
        python_tech = None
        for tech in result["technologies"]:
            if tech["name"].lower() == "python":
                python_tech = tech
                break

        assert python_tech is not None
        assert python_tech["category"] == "Backend"
        assert python_tech["raw_count"] == 2  # Apparaît 2 fois

    def test_case_insensitive(self):
        """Test que la détection est case-insensitive."""
        analyzer = TechAnalyzer()
        text = "PYTHON Python python PyThOn"

        result = analyzer.analyze(text)

        # Doit détecter Python (4 occurrences)
        python_tech = next(
            (t for t in result["technologies"] if t["name"].lower() == "python"),
            None
        )
        assert python_tech is not None
        assert python_tech["raw_count"] == 4


class TestTechScoring:
    """Tests du système de scoring."""

    def test_score_normalization(self):
        """Test que les scores sont normalisés entre 0 et 100."""
        analyzer = TechAnalyzer()
        text = "Python " * 10 + "Angular " * 5 + "Docker"

        result = analyzer.analyze(text)

        for tech in result["technologies"]:
            assert 0 <= tech["score"] <= 100

        # Le plus fréquent doit avoir score 100
        max_score = max(t["score"] for t in result["technologies"])
        assert max_score == 100

    def test_relative_scoring(self):
        """Test que les scores sont relatifs."""
        analyzer = TechAnalyzer()
        text = "Python Python Python Angular"

        result = analyzer.analyze(text)

        python_score = next(t["score"] for t in result["technologies"] if t["name"].lower() == "python")
        angular_score = next(t["score"] for t in result["technologies"] if t["name"].lower() == "angular")

        # Python (3x) doit avoir un score plus élevé qu'Angular (1x)
        assert python_score > angular_score


class TestStatsCalculation:
    """Tests du calcul des statistiques."""

    def test_stats_structure(self):
        """Test que les stats ont la bonne structure."""
        analyzer = TechAnalyzer()
        text = "Python Angular FastAPI Docker"

        result = analyzer.analyze(text)
        stats = result["stats"]

        assert "total_technologies" in stats
        assert "dominant_category" in stats
        assert "experience_level" in stats

    def test_dominant_category(self):
        """Test détection de la catégorie dominante."""
        analyzer = TechAnalyzer()
        # Texte avec beaucoup de Frontend
        text = "Angular React Vue TypeScript JavaScript HTML CSS"

        result = analyzer.analyze(text)

        assert result["stats"]["dominant_category"] == "Frontend"