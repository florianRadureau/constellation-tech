# CLAUDE.md - Guide Développement Constellation Tech

> Documentation complète pour reprendre le développement efficacement avec Claude ou tout développeur.

---

## 🎯 Vue d'Ensemble du Projet

**Constellation Tech** est une API backend qui transforme des CVs en visualisations spatiales magnifiques où chaque technologie devient une étoile dans une constellation personnalisée générée par IA.

### Philosophie du Code

⚡ **Qualité > Rapidité**
- Code production-ready dès le départ
- Tests exhaustifs (>80% couverture)
- Documentation inline complète
- Architecture maintenable

🎨 **Simplicité & Élégance**
- Services découplés et responsabilité unique
- Pipeline clair en 10 étapes
- Pas de sur-ingénierie
- Solutions pragmatiques

---

## 📐 Architecture & Design Patterns

### Structure Globale

```
backend/
├── services/              # ⭐ CORE - Logique métier (11 services)
│   ├── cv_parser.py              # Extraction PDF/DOCX
│   ├── tech_analyzer.py          # Détection 355+ technologies
│   ├── title_generator.py        # Titres poétiques
│   ├── prompt_generator.py       # Prompts Vertex AI
│   ├── image_generator.py        # Génération Imagen
│   ├── star_detector.py          # Détection OpenCV
│   ├── technology_mapper.py      # Mapping étoiles↔technos
│   ├── text_overlay_service.py   # Annotations Pillow
│   ├── storage_service.py        # Upload GCS
│   └── constellation_orchestrator.py  # Orchestration pipeline
│
├── models/                # Pydantic schemas (API)
├── routers/               # FastAPI endpoints
├── exceptions/            # Custom exceptions
├── utils/                 # Utilities (tech_dictionary, etc.)
├── tests/                 # Tests unitaires (48+)
├── config.py              # Configuration centralisée
└── main.py                # FastAPI application
```

### Pipeline de Génération (10 Étapes)

```
[1] CVParser          → Extraction texte (PDF/DOCX)
[2] TechAnalyzer      → Détection 355+ technologies + scoring
[3] TitleGenerator    → Titre poétique selon profil
[4] PromptGenerator   → Prompt ultra-simple pour Imagen
[5] ImageGenerator    → Génération constellation (Vertex AI)
[6] StarDetector      → Détection étoiles (OpenCV threshold)
[7] TechnologyMapper  → Mapping étoiles ↔ technologies
[8] TextOverlay       → Annotations avec anti-collision
[9] StorageService    → Upload GCS + URL signée
[10] ConstellationResult → Retour final
```

**Temps moyen :** ~12 secondes end-to-end

---

## 🏗️ Patterns & Principes Appliqués

### 1. Dependency Injection Pattern

**Utilisation :** Orchestrateur initialise tous les services

```python
class ConstellationOrchestrator:
    def __init__(self):
        self.cv_parser = CVParser()
        self.tech_analyzer = TechAnalyzer()
        self.image_generator = ImageGenerator()
        # ... tous les services
```

**Avantages :**
- Testabilité (injection de mocks)
- Découplage
- Single responsibility

### 2. Factory Pattern

**Utilisation :** TitleGenerator avec banques de métaphores

```python
METAPHORS = {
    "Frontend": ["L'Architecte des Interfaces", ...],
    "Backend": ["Le Bâtisseur de Systèmes", ...],
    # ... 9 catégories
}

def generate(self, stats):
    category = stats['dominant_category']
    return random.choice(self.METAPHORS[category])
```

### 3. Strategy Pattern

**Utilisation :** Détection adaptative dans StarDetector

```python
def detect_with_adjustable_threshold(self, image, target_count):
    # Essaie threshold initial
    stars = self.detect(image)

    # Si insuffisant, ajuste threshold
    if len(stars) < target_count:
        for lower_threshold in [160, 140, 120]:
            self.min_brightness = lower_threshold
            stars = self.detect(image)
            if len(stars) >= target_count:
                break

    return stars
```

### 4. Builder Pattern (implicite)

**Utilisation :** TextOverlayService compose l'image finale

```python
def compose(self, image, mappings, title):
    result = image.copy()
    result = self.add_title(result, title)
    result = self.add_tech_labels(result, mappings)
    result = self.add_watermark(result)
    return result
```

---

## 🎨 Standards de Code

### Type Hints (100% du code)

```python
# ✅ BON
def generate(
    self,
    tech_count: int,
    dominant_category: str = "Other"
) -> str:
    """Generate prompt for Imagen."""
    pass

# ❌ MAUVAIS
def generate(self, tech_count, dominant_category="Other"):
    pass
```

### Docstrings Google-Style

```python
def map(
    self,
    stars: list[StarPosition],
    technologies: list[Dict[str, Any]]
) -> list[StarTechMapping]:
    """
    Map stars to technologies by brightness/score.

    Args:
        stars: List of detected stars (sorted by brightness)
        technologies: List of technology dicts from TechAnalyzer

    Returns:
        List of StarTechMapping objects

    Example:
        >>> mapper = TechnologyMapper()
        >>> mappings = mapper.map(stars[:8], techs[:8])
    """
```

### Logging Structuré

```python
# ✅ BON - Contexte clair
logger.info(f"✓ Detected {len(stars)} stars")
logger.debug(f"Star 1: {stars[0]}")
logger.error(f"Failed to upload: {e}", exc_info=True)

# ❌ MAUVAIS - Pas de contexte
print("Done")
logger.info("Error")
```

### Exceptions Personnalisées

```python
# ✅ BON - Exceptions spécifiques
class QuotaExceededError(ImageGenerationError):
    def __init__(self, current_count: int, max_quota: int):
        self.current_count = current_count
        self.max_quota = max_quota
        super().__init__(
            f"Quota exceeded: {current_count}/{max_quota}"
        )

# ❌ MAUVAIS - Exception générique
raise Exception("Quota exceeded")
```

---

## 🧪 Tests - Approche TDD

### Structure des Tests

```python
class TestTitleGenerator:
    """Test suite for TitleGenerator."""

    @pytest.fixture
    def generator(self) -> TitleGenerator:
        """Create instance with fixed seed."""
        return TitleGenerator(seed=42)

    def test_generate_frontend_title(self, generator):
        """Test title generation for Frontend."""
        stats = {"dominant_category": "Frontend"}
        title = generator.generate(stats)

        assert isinstance(title, str)
        assert title in generator.METAPHORS["Frontend"]
```

### Coverage Goals

- **Services critiques :** 100% (cv_parser, tech_analyzer, etc.)
- **Services core :** >90% (title_generator, prompt_generator, etc.)
- **Services support :** >80% (storage, text_overlay, etc.)
- **Overall :** >80%

### Commandes

```bash
# Tous les tests
pytest

# Avec couverture
pytest --cov=services --cov-report=html

# Test spécifique
pytest tests/test_title_generator.py -v

# Test pipeline complet (local)
python test_full_pipeline.py
```

---

## 🔧 Configuration & Environnement

### Variables d'Environnement (.env)

```bash
# GCP - OBLIGATOIRE
GCP_PROJECT_ID=constellation-tech
GCP_REGION=europe-west1
GCS_BUCKET_NAME=constellation-tech-images
GOOGLE_APPLICATION_CREDENTIALS=../secrets/gcp-service-account.json

# Application
DAILY_QUOTA=100
ENVIRONMENT=development
LOG_LEVEL=INFO

# Image Generation
CANVAS_SIZE=1024
MIN_STAR_DISTANCE=120
RANDOM_NOISE=30
MAX_CONNECTIONS_PER_STAR=3

# Storage
SIGNED_URL_EXPIRATION_DAYS=7
```

### Configuration Centralisée (config.py)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gcp_project_id: str
    daily_quota: int = Field(default=100, ge=1, le=10000)
    # ... validation + defaults

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
```

**Avantages :**
- Validation automatique Pydantic
- Type hints
- Defaults sécurisés
- Une seule source de vérité

---

## 📝 Conventions de Commit

### Format

```
<type>: <description courte en français>

<corps optionnel avec détails>
```

### Types

- `Ajout` - Nouveau service/feature
- `Fix` - Correction bug
- `Refactor` - Refactoring sans changement fonctionnel
- `Tests` - Ajout/modification tests
- `Docs` - Documentation
- `Config` - Configuration

### Exemples

```bash
✅ BON
"Ajout TitleGenerator avec tests complets

- 9 catégories de métaphores
- Génération aléatoire avec seed
- 14 tests unitaires"

❌ MAUVAIS
"wip"
"fix bug"
"update"
```

---

## 🚀 Workflow Développement

### 1. Nouvelle Feature

```bash
# 1. Créer le service
touch services/new_service.py

# 2. Écrire les tests AVANT (TDD)
touch tests/test_new_service.py

# 3. Implémenter le service
# - Type hints complets
# - Docstrings Google-style
# - Logging approprié

# 4. Tester
pytest tests/test_new_service.py -v

# 5. Quality check
black services/new_service.py
pylint services/new_service.py
mypy services/new_service.py

# 6. Commit
git add services/new_service.py tests/test_new_service.py
git commit -m "Ajout NewService avec tests"
```

### 2. Bug Fix

```bash
# 1. Créer test reproduisant le bug
def test_bug_reproduction():
    # Setup qui fait échouer
    assert expected == actual  # Fail

# 2. Fixer le code
# 3. Vérifier test passe
# 4. Commit avec "Fix: ..."
```

### 3. Refactoring

```bash
# 1. S'assurer tests passent
pytest

# 2. Refactorer
# 3. Re-tester (doit toujours passer)
# 4. Commit avec "Refactor: ..."
```

---

## 🎯 Bonnes Pratiques Spécifiques

### Services

**✅ DO:**
- Un service = une responsabilité
- Méthodes publiques avec docstrings complètes
- Méthodes privées préfixées `_`
- Logging à chaque étape importante
- Gestion erreurs avec exceptions custom

**❌ DON'T:**
- Services qui font tout
- Couplage fort entre services
- Print() pour debug
- Exceptions génériques
- Magic numbers (utiliser constantes)

### API (FastAPI)

**✅ DO:**
- Pydantic models pour validation
- Documentation OpenAPI détaillée
- Gestion erreurs avec HTTPException
- Status codes appropriés
- Response models typés

```python
@router.post(
    "/api/generate-constellation",
    response_model=ConstellationResponse,
    responses={
        400: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
    }
)
async def generate_constellation(
    file: UploadFile = File(...)
) -> ConstellationResponse:
    """Documentation détaillée..."""
```

### Tests

**✅ DO:**
- Fixtures pytest pour setup
- Mocks pour services externes (Vertex AI, GCS)
- Tests unitaires isolés
- Noms descriptifs `test_<action>_<expected>`
- Assertions claires

```python
def test_generate_with_high_tech_count(generator):
    """Test that tech_count is limited to 15."""
    prompt = generator.generate(tech_count=20)
    assert "15 bright stars" in prompt
```

---

## 🔍 Debugging & Troubleshooting

### Logging

```python
import logging
logger = logging.getLogger(__name__)

# Niveaux appropriés
logger.debug("Détails internes")      # Développement
logger.info("Étapes importantes")      # Production
logger.warning("Situations anormales") # Toujours
logger.error("Erreurs", exc_info=True) # Avec stacktrace
```

### Tests Locaux

```bash
# Pipeline complet
python test_full_pipeline.py

# Service spécifique
python -c "
from services.title_generator import TitleGenerator
gen = TitleGenerator()
print(gen.generate({'dominant_category': 'Frontend'}))
"

# Vérifier Vertex AI
python -c "
from services.image_generator import ImageGenerator
gen = ImageGenerator()
print(gen.get_quota_status())
"
```

### Problèmes Courants

| Problème | Cause | Solution |
|----------|-------|----------|
| `Aucun texte extractible` | PDF scanné | Utiliser PDF avec texte ou ajouter OCR |
| `Quota exceeded` | 100 générations/jour | Attendre reset minuit UTC |
| `No stars detected` | Image trop sombre | Ajuster `min_brightness` |
| `Import error` | Mauvais PYTHONPATH | Lancer depuis `backend/` |

---

## 📚 Technologies & Dépendances Clés

### Core

- **FastAPI 0.115.0** - Framework web async
- **Pydantic 2.9.0** - Validation données
- **Uvicorn 0.32.0** - ASGI server

### IA & Vision

- **google-cloud-aiplatform 1.70.0** - Vertex AI Imagen
- **opencv-python 4.8.1.78** - Détection étoiles
- **Pillow 10.4.0** - Manipulation images
- **numpy 1.26.4** - (Pas 2.x, incompatible OpenCV)

### Parsing

- **pypdf 5.1.0** - Extraction PDF
- **python-docx 1.1.2** - Extraction DOCX

### Quality

- **pytest 7.4.3** - Tests
- **black 24.1.1** - Formatting
- **pylint 3.0.3** - Linting
- **mypy 1.8.0** - Type checking

---

## 🎨 Philosophie Design - Approche Simple & Élégante

### Évolution de l'Architecture

**❌ Approche Initiale (Complexe):**
```
1. Générer 4 fonds pré-calculés avec Vertex AI
2. Calculer positions étoiles manuellement (formations)
3. Télécharger logos avec logo.dev API
4. Composer avec Pillow (fonds + logos + étoiles)
```

**✅ Approche Finale (Simple):**
```
1. Prompt minimaliste → Vertex AI génère TOUT (fond + étoiles)
2. Détection OpenCV → Positions automatiques
3. Annotation Pillow → Texte uniquement
```

**Résultats :**
- 🎨 Images plus belles (Imagen excelle naturellement)
- ⚡ Code plus simple (moins de services)
- 🐛 Moins de bugs (moins de complexité)
- 💰 Coûts similaires (1 appel Imagen vs assets)

**Leçon :** Faire confiance aux capacités natives de l'IA plutôt que sur-contrôler

---

## 🔐 Sécurité

### Credentials

- ✅ Service Account GCP (JSON key file)
- ✅ .env exclu du git (.gitignore)
- ✅ Pydantic SecretStr pour API keys
- ❌ Jamais de credentials hardcodés

### Validation Fichiers

```python
# Taille
if file_size > 5 * 1024 * 1024:  # 5MB
    raise HTTPException(400, "File too large")

# Format
if not filename.endswith(('.pdf', '.docx')):
    raise HTTPException(400, "Invalid format")
```

### Rate Limiting

- Global : 100 générations/jour
- Compteur en mémoire (quota_reset_date)
- Reset automatique minuit UTC

---

## 📊 Métriques de Performance

### Benchmarks Typiques

```
Parse CV (PDF):           < 1s
Analyse technologies:     < 1s
Génération titre:         < 0.1s
Génération prompt:        < 0.1s
Vertex AI Imagen:         10-15s  ⏱️ (goulot)
Détection étoiles:        0.5-1s
Mapping + overlay:        0.5-1s
Upload GCS:               < 1s
─────────────────────────────────
TOTAL:                    12-20s
```

### Optimisations Possibles

1. **Cache générations** - Hash CV → check si déjà généré
2. **Parallel processing** - Parse + analyse en parallèle
3. **Batch Imagen** - Si multiple requests
4. **CDN** - Images via CDN au lieu de signed URLs

---

## 🗺️ Roadmap & TODO

### Fait ✅

- [x] Pipeline complet (10 services)
- [x] API FastAPI avec docs
- [x] Tests >80% couverture
- [x] Configuration centralisée
- [x] Logging structuré
- [x] README & documentation

### Prochaines Étapes

#### Phase 1: Frontend (1-2 jours)
- [ ] Page HTML/CSS/JS minimaliste
- [ ] Upload drag & drop
- [ ] Loader élégant (30s)
- [ ] Affichage résultat responsive

#### Phase 2: Déploiement (1 jour)
- [ ] Dockerfile multi-stage
- [ ] Cloud Run backend
- [ ] Cloud Storage frontend
- [ ] CI/CD GitHub Actions

#### Phase 3: Améliorations (optionnel)
- [ ] OCR pour PDFs scannés (Google Vision API)
- [ ] Cache Redis générations similaires
- [ ] Cloud Monitoring dashboard
- [ ] Logs structurés (Cloud Logging)
- [ ] Authentification utilisateurs

---

## 💡 Patterns de Conversation avec Claude

### Pour Ajouter une Feature

```
"Je veux ajouter [FEATURE] au projet Constellation Tech.

Contexte: [Lire CLAUDE.md pour comprendre l'architecture]

Requirements:
- Suivre les standards de code (type hints, docstrings, tests)
- Intégration avec le pipeline existant
- Tests unitaires avec >80% couverture
- Commit clair en français

Peux-tu implémenter cela en suivant les bonnes pratiques du projet ?"
```

### Pour un Bug Fix

```
"Bug dans [SERVICE]: [DESCRIPTION]

Steps to reproduce:
1. ...
2. ...

Expected: [COMPORTEMENT ATTENDU]
Actual: [COMPORTEMENT ACTUEL]

Peux-tu:
1. Créer un test reproduisant le bug
2. Fixer le code
3. Vérifier que tous les tests passent
4. Commit avec 'Fix: ...'"
```

### Pour du Refactoring

```
"Je veux refactorer [PARTIE DU CODE] pour [RAISON].

Contraintes:
- Ne pas casser les tests existants
- Garder la même API publique
- Améliorer la maintenabilité

Peux-tu proposer un refactoring en gardant tous les tests verts ?"
```

---

## 🎓 Ressources & Références

### Documentation Externe

- **FastAPI:** https://fastapi.tiangolo.com/
- **Pydantic:** https://docs.pydantic.dev/
- **Vertex AI Imagen:** https://cloud.google.com/vertex-ai/docs/generative-ai/image/overview
- **OpenCV Python:** https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html
- **Pillow:** https://pillow.readthedocs.io/

### Code Patterns

- **Clean Architecture:** Services découplés, responsabilité unique
- **SOLID Principles:** Appliqués dans les services
- **TDD:** Tests before code
- **12-Factor App:** Configuration via environnement

---

## ✅ Checklist Avant Push

```bash
# 1. Tests passent
pytest
✓ 48 tests passed

# 2. Quality checks
black .
pylint services/
mypy services/

# 3. Pas de secrets
grep -r "sk_" . --exclude-dir=venv
# → Aucun résultat

# 4. Commit message clair
git log -1
# → Message descriptif en français

# 5. README à jour
# → Version, features, exemples corrects
```

---

## 🏁 Conclusion

Ce projet démontre :

✨ **Excellence Technique**
- Architecture propre et maintenable
- Tests exhaustifs
- Documentation complète
- Performance optimisée

🎨 **Innovation Pragmatique**
- Approche simple & élégante
- IA utilisée intelligemment
- Résultats visuels époustouflants

💎 **Production-Ready**
- Gestion erreurs robuste
- Logging structuré
- Sécurité intégrée
- Prêt pour le déploiement

**Ce fichier CLAUDE.md est votre guide complet pour reprendre ou étendre le projet avec efficacité et qualité.**

---

*Dernière mise à jour: 2025-10-23*
*Version: 1.0.0*
*Auteur: Développé avec ❤️ et qualité*
