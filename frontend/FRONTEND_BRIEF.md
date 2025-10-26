# BRIEF TECHNIQUE - FRONTEND CONSTELLATION TECH

> **Mission**: Créer une landing page HTML élégante pour transformer des CVs en constellations spatiales magnifiques.
>
> **Cible**: Professionnels tech cherchant à visualiser leur profil de manière unique.
>
> **Niveau de qualité attendu**: Production hollywoodienne - attention extrême aux détails, animations fluides, design immersif.

---

## 📐 CONTRAINTES TECHNIQUES

- **Hébergement**: GitHub Pages (site statique)
- **Technologies**: HTML5 + CSS3 + JavaScript vanilla (ES6+)
- **Pas de framework**: React/Vue/Angular non autorisés (page unique simple)
- **Performance**: Temps de chargement < 2s, animations 60fps
- **Compatibilité**: Chrome/Firefox/Safari/Edge (dernières versions)
- **Responsive**: Mobile-first (320px → 4K)

---

## 🔌 CONTRAT D'INTERFACE API

### Base URL
```
https://[CLOUD_RUN_URL]
```
> **NOTE**: L'URL Cloud Run exacte sera fournie après déploiement. Pour développement local: `http://localhost:8000`

---

### Endpoint: POST /api/generate-constellation

**Description**: Upload un CV (PDF/DOCX) et génère une constellation personnalisée.

#### Request

**Headers**:
```http
Content-Type: multipart/form-data
```

**Body**:
```javascript
const formData = new FormData();
formData.append('file', cvFile); // File object from input[type="file"]
```

**Exemple complet**:
```javascript
async function generateConstellation(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('https://[CLOUD_RUN_URL]/api/generate-constellation', {
        method: 'POST',
        body: formData
        // Pas de Content-Type header (auto avec FormData)
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Generation failed');
    }

    return await response.json();
}
```

#### Response SUCCESS (200 OK)

**Format**:
```json
{
    "image_url": "https://storage.googleapis.com/constellation-tech-images/constellation_abc123.png?X-Goog-Signature=...",
    "title": "La Constellation Complète",
    "technologies": [
        {
            "name": "Angular",
            "category": "Frontend",
            "score": 100,
            "color": "#DD0031",
            "size": "large"
        },
        {
            "name": "Python",
            "category": "Backend",
            "score": 95,
            "color": "#3776AB",
            "size": "large"
        }
    ],
    "stats": {
        "total_techs_found": 12,
        "dominant_category": "Fullstack",
        "level": "Senior",
        "categories_count": {
            "Frontend": 4,
            "Backend": 3,
            "Database": 2,
            "DevOps": 3
        }
    },
    "generation_time": 14.32,
    "stars_detected": 12
}
```

**Champs**:
- `image_url` (string): URL publique de l'image générée (valide 7 jours)
- `title` (string): Titre poétique généré (ex: "L'Architecte des Deux Mondes")
- `technologies` (array): Liste des technologies détectées
  - `name`: Nom affiché (ex: "Angular", "Python")
  - `category`: Catégorie (Frontend, Backend, Database, DevOps, AI_ML, etc.)
  - `score`: Score de pertinence 0-100
  - `color`: Code couleur hexadécimal de la catégorie
  - `size`: Taille visuelle (large/medium/small/tiny)
- `stats` (object): Statistiques globales
  - `total_techs_found`: Nombre total de technologies
  - `dominant_category`: Catégorie principale ("Fullstack", "Frontend", "Backend", etc.)
  - `level`: Niveau estimé (Junior/Intermediate/Senior/Expert)
  - `categories_count`: Distribution par catégories
- `generation_time` (float): Temps de génération en secondes
- `stars_detected` (int): Nombre d'étoiles détectées dans la constellation

#### Response ERROR

##### 400 Bad Request - Fichier invalide

**Cas 1: Fichier trop volumineux**
```json
{
    "detail": "File too large: 6.2MB (max 5MB)"
}
```

**Cas 2: Format non supporté**
```json
{
    "detail": "Failed to parse CV: Unsupported file format. Please upload PDF or DOCX."
}
```

**Cas 3: Fichier corrompu**
```json
{
    "detail": "Failed to parse CV: Unable to extract text from PDF"
}
```

**UI à implémenter**:
```
❌ Erreur - Fichier invalide

[Message d'erreur précis]

Formats acceptés: PDF, DOCX
Taille maximale: 5 MB

[Bouton: Réessayer]
```

---

##### 429 Too Many Requests - Quota dépassé

```json
{
    "detail": "Daily quota exceeded: 100/100 generations used"
}
```

**UI à implémenter**:
```
⏸️ Quota quotidien atteint

Notre quota de 100 générations quotidiennes est atteint.
Le quota se réinitialise chaque jour à minuit UTC.

Prochain reset: [calculer temps restant]

💡 Ce projet utilise Vertex AI Imagen (coûteux).
Revenez demain ou contactez-nous pour une instance privée.

[Bouton: Voir mon LinkedIn] [Bouton: GitHub du projet]
```

---

##### 500 Internal Server Error - Erreur serveur

```json
{
    "detail": "Generation failed: Vertex AI timeout"
}
```

**UI à implémenter**:
```
⚠️ Erreur serveur

Une erreur est survenue lors de la génération.
Nos serveurs ont peut-être du mal à suivre.

[Bouton: Réessayer] [Bouton: Signaler le problème]
```

---

### Endpoint: GET /api/quota (optionnel)

**Description**: Récupère le statut du quota quotidien.

#### Request
```javascript
const response = await fetch('https://[CLOUD_RUN_URL]/api/quota');
const quota = await response.json();
```

#### Response (200 OK)
```json
{
    "current_count": 42,
    "max_quota": 100,
    "remaining": 58,
    "reset_date": "2025-10-27T00:00:00Z"
}
```

**Utilisation suggérée**: Afficher le quota restant dans le footer
```html
<div class="quota-badge">
    ⚡ 58 générations restantes aujourd'hui
</div>
```

---

## 🎨 SPÉCIFICATIONS UI/UX

### Layout Global

```
┌─────────────────────────────────────────┐
│         HERO SECTION                    │
│  (Background: constellation image)      │
│                                         │
│     🌟 [TITRE PRINCIPAL]                │
│        [Sous-titre]                     │
│                                         │
│    [Bouton Upload CV]                   │
│                                         │
│  🔒 Nous ne conservons aucun CV         │
│                                         │
└─────────────────────────────────────────┘
│                                         │
│      [Zone résultat - masquée]          │
│                                         │
└─────────────────────────────────────────┘
│  GitHub • LinkedIn                      │
└─────────────────────────────────────────┘
```

---

### Hero Section

#### Contenu Textuel

**Titre principal** (propositions):
- Option 1: "Transformez votre CV en Constellation Stellaire"
- Option 2: "Votre Parcours Tech, Visualisé comme une Constellation"
- Option 3: "De CV à Constellation - Powered by AI"

**Sous-titre** (propositions):
- Option 1: "Analysez vos compétences tech et générez une visualisation spatiale unique avec l'IA Imagen de Google"
- Option 2: "Intelligence Artificielle + Design Spatial = Votre Profil comme jamais vu"
- Option 3: "Upload votre CV, recevez une œuvre d'art cosmique personnalisée en 15 secondes"

> **À l'agent**: Choisissez la combinaison la plus impactante, ou proposez votre propre version si vous avez mieux.

#### Background

**Fichier**: `assets/constellation-hero-bg.png`

**Spécifications**:
- Résolution minimale: 2560x1440px (haute définition)
- Format: PNG avec transparence ou JPG optimisé
- Poids cible: < 500KB (compression intelligente)

**Traitement CSS**:
```css
.hero {
    background-image: url('assets/constellation-hero-bg.png');
    background-size: cover;
    background-position: center;
    background-attachment: fixed; /* Parallax effect */
}

/* Overlay sombre pour lisibilité du texte */
.hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(
        180deg,
        rgba(10, 10, 20, 0.7) 0%,
        rgba(10, 10, 20, 0.9) 100%
    );
}
```

#### Typography

**Font**: Space Mono (Google Fonts)
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
```

**Styles texte**:
```css
.hero-title {
    font-family: 'Space Mono', monospace;
    font-size: clamp(2rem, 5vw, 4rem); /* Responsive */
    font-weight: 700;
    line-height: 1.2;
    color: #FFFFFF;
    text-align: center;
    margin-bottom: 1rem;

    /* Effet lueur subtile */
    text-shadow:
        0 0 20px rgba(100, 150, 255, 0.5),
        0 0 40px rgba(100, 150, 255, 0.3);
}

.hero-subtitle {
    font-family: 'Space Mono', monospace;
    font-size: clamp(1rem, 2vw, 1.5rem);
    font-weight: 400;
    line-height: 1.6;
    color: rgba(255, 255, 255, 0.85);
    text-align: center;
    max-width: 700px;
    margin: 0 auto 3rem;
}
```

---

### Zone Upload

#### Bouton Upload

**Design**: Bouton imposant, spatial, avec effet hover spectaculaire

**HTML**:
```html
<div class="upload-container">
    <label for="cv-upload" class="upload-button">
        <svg class="upload-icon" width="48" height="48" viewBox="0 0 24 24">
            <path d="M19 13v6c0 1.1-.9 2-2 2H7c-1.1 0-2-.9-2-2v-6H3l9-9 9 9h-2z"/>
        </svg>
        <span class="upload-text">Choisir mon CV</span>
        <span class="upload-hint">PDF ou DOCX • Max 5 MB</span>
    </label>
    <input
        type="file"
        id="cv-upload"
        accept=".pdf,.docx"
        style="display: none;"
    >
</div>
```

**CSS**:
```css
.upload-button {
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;

    padding: 2.5rem 4rem;
    border: 2px solid rgba(100, 150, 255, 0.5);
    border-radius: 16px;

    background: linear-gradient(
        135deg,
        rgba(100, 150, 255, 0.1),
        rgba(150, 100, 255, 0.1)
    );
    backdrop-filter: blur(10px);

    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.upload-button:hover {
    border-color: rgba(100, 150, 255, 0.8);
    background: linear-gradient(
        135deg,
        rgba(100, 150, 255, 0.2),
        rgba(150, 100, 255, 0.2)
    );
    transform: translateY(-4px);
    box-shadow:
        0 10px 40px rgba(100, 150, 255, 0.3),
        0 0 80px rgba(100, 150, 255, 0.2);
}

.upload-icon {
    fill: #FFFFFF;
    filter: drop-shadow(0 0 10px rgba(100, 150, 255, 0.6));
}

.upload-text {
    font-family: 'Space Mono', monospace;
    font-size: 1.25rem;
    font-weight: 700;
    color: #FFFFFF;
}

.upload-hint {
    font-family: 'Space Mono', monospace;
    font-size: 0.875rem;
    color: rgba(255, 255, 255, 0.6);
}
```

#### Validation Côté Client

**JavaScript**:
```javascript
const fileInput = document.getElementById('cv-upload');

fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];

    if (!file) return;

    // Validation format
    const validFormats = ['.pdf', '.docx'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();

    if (!validFormats.includes(fileExtension)) {
        showError('Format invalide', 'Veuillez uploader un fichier PDF ou DOCX.');
        return;
    }

    // Validation taille (5MB = 5 * 1024 * 1024 bytes)
    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
        const sizeMB = (file.size / 1024 / 1024).toFixed(1);
        showError(
            'Fichier trop volumineux',
            `Votre fichier fait ${sizeMB} MB. La taille maximale est de 5 MB.`
        );
        return;
    }

    // Si validation OK, lancer la génération
    generateConstellation(file);
});
```

---

### Animation Loading

**Déclenchement**: Dès que le fichier est uploadé et validé

**Durée estimée**: ~15 secondes (temps réel de l'API)

#### UI Loading

```html
<div class="loading-container" style="display: none;">
    <div class="loading-animation">
        <!-- Animation CSS de constellation qui se forme -->
        <div class="star star-1"></div>
        <div class="star star-2"></div>
        <div class="star star-3"></div>
        <!-- Lignes de connexion animées -->
        <svg class="constellation-lines">
            <line x1="0" y1="0" x2="100" y2="100" class="line line-1" />
            <!-- ... -->
        </svg>
    </div>

    <div class="loading-text">
        <h2 class="loading-title">Génération de votre constellation...</h2>
        <p class="loading-description">
            Notre IA analyse votre CV et génère une constellation unique.<br>
            Cela prend environ 15 secondes.
        </p>
        <div class="loading-progress">
            <div class="progress-bar"></div>
        </div>
        <p class="loading-step">Analyse des technologies...</p>
    </div>
</div>
```

#### Animation Recommandée

**Concept**: Étoiles qui apparaissent progressivement et se connectent

**CSS Animation**:
```css
@keyframes starAppear {
    0% {
        opacity: 0;
        transform: scale(0);
    }
    50% {
        opacity: 1;
        transform: scale(1.2);
    }
    100% {
        opacity: 1;
        transform: scale(1);
    }
}

.star {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #FFFFFF;
    box-shadow: 0 0 20px rgba(255, 255, 255, 0.8);
    animation: starAppear 0.6s ease-out forwards;
}

.star-1 { animation-delay: 0.2s; }
.star-2 { animation-delay: 0.4s; }
.star-3 { animation-delay: 0.6s; }

@keyframes lineGrow {
    from { stroke-dashoffset: 1000; }
    to { stroke-dashoffset: 0; }
}

.line {
    stroke: rgba(100, 150, 255, 0.5);
    stroke-width: 2;
    stroke-dasharray: 1000;
    stroke-dashoffset: 1000;
    animation: lineGrow 1s ease-in-out forwards;
}
```

#### Progression (Optionnel mais recommandé)

**JavaScript**:
```javascript
// Simuler progression pendant l'attente API
function simulateProgress() {
    const progressBar = document.querySelector('.progress-bar');
    const stepText = document.querySelector('.loading-step');

    const steps = [
        { progress: 20, text: 'Analyse des technologies...' },
        { progress: 40, text: 'Génération du titre poétique...' },
        { progress: 60, text: 'Création de la constellation avec Imagen...' },
        { progress: 80, text: 'Détection des étoiles...' },
        { progress: 95, text: 'Finalisation...' }
    ];

    let currentStep = 0;
    const interval = setInterval(() => {
        if (currentStep < steps.length) {
            const step = steps[currentStep];
            progressBar.style.width = `${step.progress}%`;
            stepText.textContent = step.text;
            currentStep++;
        } else {
            clearInterval(interval);
        }
    }, 3000); // Changer toutes les 3 secondes

    return interval; // Pour pouvoir clear si API termine avant
}
```

---

### Affichage Résultat

**Déclenchement**: Dès réception de la réponse API avec succès

#### Layout Résultat

```html
<div class="result-container" style="display: none;">
    <!-- Image principale -->
    <div class="result-image-wrapper">
        <img
            src=""
            alt="Constellation générée"
            class="constellation-image"
            id="result-image"
        >
    </div>

    <!-- Titre généré -->
    <h2 class="constellation-title" id="result-title"></h2>

    <!-- Technologies détectées -->
    <div class="technologies-section">
        <h3 class="section-title">Technologies détectées</h3>
        <div class="technologies-grid" id="technologies-list">
            <!-- Badges générés dynamiquement -->
        </div>
    </div>

    <!-- Statistiques -->
    <div class="stats-section">
        <div class="stat-card">
            <span class="stat-value" id="stat-total"></span>
            <span class="stat-label">Technologies</span>
        </div>
        <div class="stat-card">
            <span class="stat-value" id="stat-category"></span>
            <span class="stat-label">Profil</span>
        </div>
        <div class="stat-card">
            <span class="stat-value" id="stat-level"></span>
            <span class="stat-label">Niveau</span>
        </div>
    </div>

    <!-- Boutons d'action -->
    <div class="action-buttons">
        <button class="btn btn-primary" id="btn-linkedin">
            <svg><!-- LinkedIn icon --></svg>
            Partager sur LinkedIn
        </button>
        <button class="btn btn-secondary" id="btn-copy">
            <svg><!-- Link icon --></svg>
            Copier le lien
        </button>
        <button class="btn btn-secondary" id="btn-download">
            <svg><!-- Download icon --></svg>
            Télécharger
        </button>
    </div>

    <!-- Bouton recommencer -->
    <button class="btn-text" id="btn-restart">
        ← Analyser un autre CV
    </button>
</div>
```

#### Style Image

```css
.constellation-image {
    width: 100%;
    max-width: 800px;
    height: auto;
    border-radius: 16px;
    box-shadow:
        0 20px 60px rgba(0, 0, 0, 0.5),
        0 0 100px rgba(100, 150, 255, 0.3);

    /* Animation d'apparition */
    animation: imageReveal 0.8s ease-out;
}

@keyframes imageReveal {
    0% {
        opacity: 0;
        transform: scale(0.9);
    }
    100% {
        opacity: 1;
        transform: scale(1);
    }
}
```

#### Badges Technologies

**JavaScript de génération**:
```javascript
function displayTechnologies(technologies) {
    const container = document.getElementById('technologies-list');

    technologies.forEach(tech => {
        const badge = document.createElement('div');
        badge.className = 'tech-badge';
        badge.style.borderColor = tech.color;
        badge.innerHTML = `
            <span class="tech-name">${tech.name}</span>
            <span class="tech-score">${tech.score}</span>
        `;
        container.appendChild(badge);
    });
}
```

**CSS**:
```css
.technologies-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    justify-content: center;
}

.tech-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border: 2px solid;
    border-radius: 24px;
    background: rgba(0, 0, 0, 0.3);
    backdrop-filter: blur(10px);
    transition: transform 0.2s;
}

.tech-badge:hover {
    transform: scale(1.05);
}

.tech-name {
    font-family: 'Space Mono', monospace;
    font-size: 0.875rem;
    color: #FFFFFF;
}

.tech-score {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.6);
}
```

---

### Boutons d'Action

#### Partager sur LinkedIn

**Fonctionnalité**: Ouvre une fenêtre de partage LinkedIn avec l'image et un texte pré-rempli

**JavaScript**:
```javascript
document.getElementById('btn-linkedin').addEventListener('click', () => {
    const imageUrl = document.getElementById('result-image').src;
    const title = document.getElementById('result-title').textContent;

    // LinkedIn share URL
    const text = encodeURIComponent(
        `J'ai transformé mon CV tech en constellation spatiale avec l'IA ! 🌟\n\n` +
        `"${title}"\n\n` +
        `Généré par Constellation Tech - un projet open-source qui visualise ` +
        `les compétences techniques comme une carte stellaire.\n\n` +
        `#TechVisualization #AI #OpenSource`
    );

    const linkedInUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(imageUrl)}&summary=${text}`;

    window.open(linkedInUrl, '_blank', 'width=600,height=600');
});
```

#### Copier le Lien

**Fonctionnalité**: Copie l'URL de l'image dans le presse-papier

**JavaScript**:
```javascript
document.getElementById('btn-copy').addEventListener('click', async () => {
    const imageUrl = document.getElementById('result-image').src;

    try {
        await navigator.clipboard.writeText(imageUrl);

        // Feedback visuel
        const btn = document.getElementById('btn-copy');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<svg><!-- Check icon --></svg> Lien copié !';
        btn.classList.add('success');

        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.classList.remove('success');
        }, 2000);

    } catch (err) {
        console.error('Failed to copy:', err);
        alert('Impossible de copier le lien. Veuillez le copier manuellement.');
    }
});
```

#### Télécharger

**Fonctionnalité**: Télécharge l'image sur l'appareil de l'utilisateur

**JavaScript**:
```javascript
document.getElementById('btn-download').addEventListener('click', async () => {
    const imageUrl = document.getElementById('result-image').src;

    try {
        // Fetch image et créer un blob
        const response = await fetch(imageUrl);
        const blob = await response.blob();

        // Créer un lien de téléchargement
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'ma-constellation.png';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

    } catch (err) {
        console.error('Download failed:', err);
        // Fallback: ouvrir dans un nouvel onglet
        window.open(imageUrl, '_blank');
    }
});
```

---

### Footer

**HTML**:
```html
<footer class="site-footer">
    <div class="footer-content">
        <p class="privacy-notice">
            🔒 Nous ne conservons aucun CV. Votre fichier est analysé temporairement puis supprimé.
        </p>

        <div class="footer-links">
            <a href="TODO_GITHUB_URL" target="_blank" rel="noopener noreferrer" class="footer-link">
                <svg width="24" height="24"><!-- GitHub icon --></svg>
                Code Source
            </a>
            <span class="separator">•</span>
            <a href="TODO_LINKEDIN_URL" target="_blank" rel="noopener noreferrer" class="footer-link">
                <svg width="24" height="24"><!-- LinkedIn icon --></svg>
                Créateur
            </a>
        </div>

        <p class="footer-credit">
            Made with ❤️ and AI • Powered by Google Vertex AI Imagen
        </p>
    </div>
</footer>
```

**CSS**:
```css
.site-footer {
    margin-top: 6rem;
    padding: 3rem 1rem;
    background: rgba(0, 0, 0, 0.3);
    border-top: 1px solid rgba(100, 150, 255, 0.2);
}

.footer-content {
    max-width: 800px;
    margin: 0 auto;
    text-align: center;
}

.privacy-notice {
    font-family: 'Space Mono', monospace;
    font-size: 0.875rem;
    color: rgba(255, 255, 255, 0.7);
    margin-bottom: 1.5rem;
}

.footer-links {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    margin-bottom: 1rem;
}

.footer-link {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.875rem;
    color: rgba(100, 150, 255, 0.9);
    text-decoration: none;
    transition: color 0.2s;
}

.footer-link:hover {
    color: #FFFFFF;
}

.separator {
    color: rgba(255, 255, 255, 0.3);
}
```

---

## 🔄 ÉTATS ET TRANSITIONS

### Machine à États

```
INITIAL
  └─> [User uploads file]
      └─> VALIDATING
          ├─> [Valid] → UPLOADING
          │   └─> [API Success] → SUCCESS
          │   └─> [API Error] → ERROR
          └─> [Invalid] → ERROR

ERROR
  └─> [User clicks retry] → INITIAL

SUCCESS
  └─> [User clicks restart] → INITIAL
```

### Gestion des États en JavaScript

```javascript
const STATE = {
    INITIAL: 'initial',
    VALIDATING: 'validating',
    UPLOADING: 'uploading',
    SUCCESS: 'success',
    ERROR: 'error'
};

let currentState = STATE.INITIAL;

function setState(newState, data = {}) {
    currentState = newState;

    // Masquer tous les conteneurs
    document.querySelector('.hero').style.display = 'none';
    document.querySelector('.loading-container').style.display = 'none';
    document.querySelector('.result-container').style.display = 'none';
    document.querySelector('.error-container').style.display = 'none';

    // Afficher le bon conteneur
    switch (newState) {
        case STATE.INITIAL:
            document.querySelector('.hero').style.display = 'flex';
            break;

        case STATE.UPLOADING:
            document.querySelector('.loading-container').style.display = 'flex';
            // Démarrer animation de progression
            simulateProgress();
            break;

        case STATE.SUCCESS:
            document.querySelector('.result-container').style.display = 'block';
            displayResult(data);
            // Scroll vers résultat
            document.querySelector('.result-container').scrollIntoView({
                behavior: 'smooth'
            });
            break;

        case STATE.ERROR:
            document.querySelector('.error-container').style.display = 'flex';
            displayError(data);
            break;
    }
}
```

### Transitions Animées

**CSS**:
```css
/* Toutes les sections ont une transition d'opacité */
.hero,
.loading-container,
.result-container,
.error-container {
    opacity: 0;
    animation: fadeIn 0.5s ease-out forwards;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Transition sortante */
.fade-out {
    animation: fadeOut 0.3s ease-out forwards;
}

@keyframes fadeOut {
    from { opacity: 1; transform: translateY(0); }
    to { opacity: 0; transform: translateY(-20px); }
}
```

---

## ⚠️ GESTION DES ERREURS

### Conteneur d'Erreur Universel

```html
<div class="error-container" style="display: none;">
    <div class="error-icon">
        <svg width="64" height="64" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M12 8v4M12 16h.01" stroke="currentColor" stroke-width="2"/>
        </svg>
    </div>

    <h2 class="error-title" id="error-title"></h2>
    <p class="error-message" id="error-message"></p>

    <div class="error-actions" id="error-actions">
        <!-- Boutons dynamiques selon le type d'erreur -->
    </div>
</div>
```

### Messages d'Erreur par Type

**JavaScript**:
```javascript
function displayError(errorData) {
    const titleEl = document.getElementById('error-title');
    const messageEl = document.getElementById('error-message');
    const actionsEl = document.getElementById('error-actions');

    const { type, detail, statusCode } = errorData;

    // Clear actions
    actionsEl.innerHTML = '';

    switch (statusCode) {
        case 400: // Bad Request
            titleEl.textContent = 'Fichier invalide';
            messageEl.innerHTML = `
                ${detail}<br><br>
                <strong>Formats acceptés :</strong> PDF, DOCX<br>
                <strong>Taille maximale :</strong> 5 MB
            `;
            actionsEl.innerHTML = `
                <button class="btn btn-primary" onclick="setState('initial')">
                    Choisir un autre fichier
                </button>
            `;
            break;

        case 429: // Quota Exceeded
            const resetTime = calculateResetTime(); // Calcul du temps avant minuit UTC
            titleEl.textContent = 'Quota quotidien atteint';
            messageEl.innerHTML = `
                Notre quota de 100 générations quotidiennes est atteint.<br>
                Le quota se réinitialise chaque jour à minuit UTC.<br><br>
                <strong>Prochain reset :</strong> dans ${resetTime}<br><br>
                💡 Ce projet utilise Vertex AI Imagen, qui a un coût important.
                Revenez demain ou contactez-nous pour une instance privée.
            `;
            actionsEl.innerHTML = `
                <button class="btn btn-secondary" onclick="window.open('TODO_LINKEDIN_URL', '_blank')">
                    Me contacter
                </button>
                <button class="btn btn-secondary" onclick="window.open('TODO_GITHUB_URL', '_blank')">
                    Voir le code
                </button>
            `;
            break;

        case 500: // Server Error
            titleEl.textContent = 'Erreur serveur';
            messageEl.innerHTML = `
                Une erreur est survenue lors de la génération.<br>
                ${detail}<br><br>
                Nos serveurs ont peut-être du mal à suivre. Veuillez réessayer.
            `;
            actionsEl.innerHTML = `
                <button class="btn btn-primary" onclick="setState('initial')">
                    Réessayer
                </button>
                <button class="btn btn-secondary" onclick="window.open('TODO_GITHUB_URL/issues', '_blank')">
                    Signaler le problème
                </button>
            `;
            break;

        default: // Erreur réseau ou inconnue
            titleEl.textContent = 'Erreur de connexion';
            messageEl.innerHTML = `
                Impossible de contacter le serveur.<br>
                Vérifiez votre connexion internet et réessayez.
            `;
            actionsEl.innerHTML = `
                <button class="btn btn-primary" onclick="location.reload()">
                    Recharger la page
                </button>
            `;
    }
}

function calculateResetTime() {
    const now = new Date();
    const tomorrow = new Date(now);
    tomorrow.setUTCHours(24, 0, 0, 0); // Minuit UTC demain

    const diff = tomorrow - now;
    const hours = Math.floor(diff / 3600000);
    const minutes = Math.floor((diff % 3600000) / 60000);

    return `${hours}h ${minutes}min`;
}
```

### Timeout Réseau

**JavaScript**:
```javascript
async function generateConstellationWithTimeout(file) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30s timeout

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(API_URL + '/api/generate-constellation', {
            method: 'POST',
            body: formData,
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            const error = await response.json();
            throw {
                statusCode: response.status,
                detail: error.detail || 'Unknown error'
            };
        }

        return await response.json();

    } catch (error) {
        clearTimeout(timeoutId);

        if (error.name === 'AbortError') {
            throw {
                statusCode: 0,
                detail: 'La requête a pris trop de temps (> 30 secondes)'
            };
        }

        throw error;
    }
}
```

---

## 🎭 QUALITÉ "HOLLYWOOD"

### Micro-animations

**Boutons avec effet ripple**:
```css
.btn {
    position: relative;
    overflow: hidden;
}

.btn::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.3);
    transform: translate(-50%, -50%);
    transition: width 0.6s, height 0.6s;
}

.btn:active::after {
    width: 300px;
    height: 300px;
}
```

**Hover effect sur tech badges**:
```css
.tech-badge {
    position: relative;
}

.tech-badge::before {
    content: '';
    position: absolute;
    inset: -2px;
    border-radius: inherit;
    padding: 2px;
    background: linear-gradient(45deg, transparent, var(--tech-color), transparent);
    -webkit-mask:
        linear-gradient(#fff 0 0) content-box,
        linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    opacity: 0;
    transition: opacity 0.3s;
}

.tech-badge:hover::before {
    opacity: 1;
}
```

### Parallax Subtil

**JavaScript**:
```javascript
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const parallax = document.querySelector('.hero');

    // Parallax à 30% de la vitesse de scroll
    parallax.style.transform = `translateY(${scrolled * 0.3}px)`;
});
```

### Particules Spatiales (Optionnel mais WOW)

**Canvas Animation**:
```javascript
const canvas = document.getElementById('particles-canvas');
const ctx = canvas.getContext('2d');

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

class Star {
    constructor() {
        this.reset();
    }

    reset() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.z = Math.random() * 1000;
        this.speed = Math.random() * 2 + 1;
    }

    update() {
        this.z -= this.speed;
        if (this.z <= 0) {
            this.reset();
            this.z = 1000;
        }
    }

    draw() {
        const x = (this.x - canvas.width / 2) * (1000 / this.z) + canvas.width / 2;
        const y = (this.y - canvas.height / 2) * (1000 / this.z) + canvas.height / 2;
        const radius = (1 - this.z / 1000) * 2;
        const opacity = 1 - this.z / 1000;

        ctx.fillStyle = `rgba(255, 255, 255, ${opacity})`;
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.fill();
    }
}

const stars = Array.from({ length: 200 }, () => new Star());

function animate() {
    ctx.fillStyle = 'rgba(10, 10, 20, 0.1)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    stars.forEach(star => {
        star.update();
        star.draw();
    });

    requestAnimationFrame(animate);
}

animate();
```

### Glassmorphism

**CSS pour cards**:
```css
.card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow:
        0 8px 32px 0 rgba(31, 38, 135, 0.37),
        inset 0 0 20px rgba(255, 255, 255, 0.05);
}
```

### Gradient Animé (Hero Background Overlay)

**CSS**:
```css
.hero::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(
        45deg,
        rgba(100, 150, 255, 0.1),
        rgba(150, 100, 255, 0.1),
        rgba(100, 200, 255, 0.1),
        rgba(200, 100, 255, 0.1)
    );
    background-size: 400% 400%;
    animation: gradientShift 15s ease infinite;
    pointer-events: none;
}

@keyframes gradientShift {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}
```

### Smooth Scrolling

**CSS**:
```css
html {
    scroll-behavior: smooth;
}
```

**JavaScript (meilleur contrôle)**:
```javascript
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    });
});
```

---

## 📱 RESPONSIVE DESIGN

### Breakpoints

```css
/* Mobile First */
:root {
    --container-padding: 1rem;
}

/* Tablet */
@media (min-width: 768px) {
    :root {
        --container-padding: 2rem;
    }
}

/* Desktop */
@media (min-width: 1024px) {
    :root {
        --container-padding: 3rem;
    }
}

/* Large Desktop */
@media (min-width: 1440px) {
    :root {
        --container-padding: 4rem;
    }
}
```

### Layout Mobile

**Hero mobile**:
```css
@media (max-width: 768px) {
    .hero-title {
        font-size: 2rem; /* Plus petit sur mobile */
    }

    .hero-subtitle {
        font-size: 1rem;
    }

    .upload-button {
        padding: 2rem 2rem; /* Moins de padding */
    }

    .technologies-grid {
        justify-content: flex-start; /* Aligné à gauche */
    }

    .action-buttons {
        flex-direction: column; /* Boutons en colonne */
        width: 100%;
    }

    .btn {
        width: 100%; /* Pleine largeur */
    }
}
```

---

## ♿ ACCESSIBILITÉ

### ARIA Labels

```html
<button
    class="upload-button"
    aria-label="Choisir un fichier CV à analyser"
    role="button"
>
    Upload CV
</button>

<div
    class="loading-container"
    role="status"
    aria-live="polite"
    aria-busy="true"
>
    Génération en cours...
</div>

<img
    src="constellation.png"
    alt="Constellation représentant votre profil technique avec 12 technologies détectées"
    role="img"
>
```

### Contraste

**Vérifier WCAG AA (ratio 4.5:1 minimum)**:
```css
/* Bon contraste */
.text-primary {
    color: #FFFFFF; /* Sur fond sombre #0A0A14 = ratio 18:1 ✓ */
}

.text-secondary {
    color: rgba(255, 255, 255, 0.85); /* Ratio 15:1 ✓ */
}
```

### Keyboard Navigation

**JavaScript**:
```javascript
// Upload via Enter/Space sur le label
document.querySelector('.upload-button').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        document.getElementById('cv-upload').click();
    }
});

// Navigation au clavier dans les boutons
document.querySelectorAll('.btn').forEach(btn => {
    btn.setAttribute('tabindex', '0');
});
```

### Focus Visible

```css
*:focus-visible {
    outline: 2px solid rgba(100, 150, 255, 0.8);
    outline-offset: 4px;
}
```

---

## 🚀 PERFORMANCE

### Optimisation Images

**Lazy Loading**:
```html
<img
    src="constellation.png"
    loading="lazy"
    decoding="async"
    alt="Constellation"
>
```

**Compression**:
- Background hero: WebP avec fallback JPG (< 500KB)
- Icons: SVG inline (évite requêtes HTTP)
- Constellation résultat: Déjà optimisée par backend

### Preload Critical Assets

```html
<head>
    <!-- Preload font critique -->
    <link
        rel="preload"
        href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap"
        as="style"
    >

    <!-- Preconnect vers API -->
    <link rel="preconnect" href="https://[CLOUD_RUN_URL]">

    <!-- Preload background hero -->
    <link
        rel="preload"
        href="assets/constellation-hero-bg.png"
        as="image"
    >
</head>
```

### Minification

**Build step recommandé**:
```bash
# Minifier CSS
npx clean-css-cli styles.css -o styles.min.css

# Minifier JS
npx terser script.js -o script.min.js --compress --mangle

# Optimiser images
npx imagemin assets/*.png --out-dir=assets/optimized
```

### Metrics Cibles

- **First Contentful Paint (FCP)**: < 1.5s
- **Largest Contentful Paint (LCP)**: < 2.5s
- **Cumulative Layout Shift (CLS)**: < 0.1
- **Time to Interactive (TTI)**: < 3s

---

## 🔍 SEO & META TAGS

### HTML Head Complet

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- Primary Meta Tags -->
    <title>Constellation Tech - Transformez votre CV en Constellation Stellaire</title>
    <meta name="title" content="Constellation Tech - CV en Constellation IA">
    <meta name="description" content="Analysez votre CV tech et générez une visualisation spatiale unique avec l'IA Imagen de Google. Gratuit, rapide, et magnifique.">
    <meta name="keywords" content="CV, visualisation, IA, constellation, tech, développeur, portfolio">
    <meta name="author" content="Florian RADUREAU">

    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://[GITHUB_PAGES_URL]">
    <meta property="og:title" content="Constellation Tech - Transformez votre CV en Constellation">
    <meta property="og:description" content="Analysez votre CV tech et générez une visualisation spatiale unique avec l'IA.">
    <meta property="og:image" content="https://[GITHUB_PAGES_URL]/assets/og-image.png">

    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:url" content="https://[GITHUB_PAGES_URL]">
    <meta property="twitter:title" content="Constellation Tech - CV en Constellation IA">
    <meta property="twitter:description" content="Visualisez votre profil tech comme une constellation stellaire.">
    <meta property="twitter:image" content="https://[GITHUB_PAGES_URL]/assets/og-image.png">

    <!-- Favicon -->
    <link rel="icon" type="image/png" sizes="32x32" href="assets/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="assets/favicon-16x16.png">
    <link rel="apple-touch-icon" sizes="180x180" href="assets/apple-touch-icon.png">

    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">

    <!-- Styles -->
    <link rel="stylesheet" href="styles.css">
</head>
```

---

## 📦 STRUCTURE DES FICHIERS

```
constellation-tech-frontend/
├── index.html              # Page principale
├── styles.css              # Styles (ou styles.min.css si minifié)
├── script.js               # JavaScript (ou script.min.js)
├── README.md               # Documentation déploiement
│
├── assets/
│   ├── constellation-hero-bg.png     # Background hero (fourni)
│   ├── og-image.png                  # Image Open Graph (1200x630)
│   ├── favicon-32x32.png
│   ├── favicon-16x16.png
│   └── apple-touch-icon.png
│
└── .gitignore             # Ignorer node_modules si build tools
```

---

## ✅ CHECKLIST DE VALIDATION

### Fonctionnel

- [ ] Upload fichier PDF fonctionne
- [ ] Upload fichier DOCX fonctionne
- [ ] Validation côté client (format + taille) fonctionne
- [ ] Appel API réussit avec bon fichier
- [ ] Erreur 400 affichée correctement
- [ ] Erreur 429 affichée correctement
- [ ] Erreur 500 affichée correctement
- [ ] Timeout réseau géré (30s)
- [ ] Animation loading s'affiche (~15s)
- [ ] Image résultat s'affiche
- [ ] Titre généré s'affiche
- [ ] Technologies affichées avec couleurs
- [ ] Stats affichées correctement
- [ ] Bouton LinkedIn partage correctement
- [ ] Bouton Copier lien fonctionne
- [ ] Bouton Télécharger fonctionne
- [ ] Bouton Recommencer reset l'état
- [ ] Liens footer cliquables (GitHub, LinkedIn)

### Design

- [ ] Font Space Mono chargée
- [ ] Background hero visible et net
- [ ] Effet parallax sur hero
- [ ] Glassmorphism sur cards
- [ ] Animations fluides (60fps)
- [ ] Hover effects sur boutons
- [ ] Transitions entre états smooth
- [ ] Responsive mobile (320px)
- [ ] Responsive tablet (768px)
- [ ] Responsive desktop (1024px+)
- [ ] Particules spatiales (si implémentées)

### Performance

- [ ] Temps chargement < 2s
- [ ] Images optimisées (WebP/JPG)
- [ ] CSS minifié
- [ ] JS minifié
- [ ] Lazy loading images
- [ ] Preload assets critiques
- [ ] Score Lighthouse > 90

### Accessibilité

- [ ] ARIA labels présents
- [ ] Contraste WCAG AA respecté
- [ ] Navigation clavier fonctionne
- [ ] Focus visible sur éléments
- [ ] Alt text sur images
- [ ] Rôles ARIA corrects

### SEO

- [ ] Meta tags présents
- [ ] Open Graph configuré
- [ ] Twitter Cards configurés
- [ ] Favicon présent (multiple sizes)
- [ ] Sitemap.xml (optionnel)
- [ ] robots.txt (optionnel)

### Code Quality

- [ ] HTML validé (W3C validator)
- [ ] CSS validé (W3C CSS validator)
- [ ] JavaScript sans erreurs console
- [ ] Code commenté (sections principales)
- [ ] Fonctions bien nommées
- [ ] Pas de code dupliqué
- [ ] Error handling complet
- [ ] Console.log supprimés (production)

---

## 🎯 LIVRABLES ATTENDUS

### Fichiers Obligatoires

1. **index.html** (structure complète, sémantique, commentée)
2. **styles.css** (organisé par sections, variables CSS, commenté)
3. **script.js** (modules, error handling, commenté)
4. **README.md** avec:
   - Instructions déploiement GitHub Pages
   - Variables à configurer (API URL, liens sociaux)
   - Screenshots du résultat
   - Commandes build (si minification)

### Assets à Créer

- `assets/og-image.png` - Image Open Graph (1200x630)
- `assets/favicon-*.png` - Favicons (générer via favicon.io)
- Placeholder pour `assets/constellation-hero-bg.png` (sera fourni)

### Documentation

**README.md structure**:
```markdown
# Constellation Tech - Frontend

## 🚀 Déploiement GitHub Pages

1. Fork ce repo
2. Configurer les variables dans `script.js`:
   ```javascript
   const API_URL = 'https://[YOUR_CLOUD_RUN_URL]';
   ```
3. Mettre à jour les liens dans `index.html`:
   - `TODO_GITHUB_URL` → votre repo
   - `TODO_LINKEDIN_URL` → votre profil
4. Settings > Pages > Source: main branch > Save

## 🎨 Personnalisation

- Background hero: Remplacer `assets/constellation-hero-bg.png`
- Couleurs: Modifier les CSS variables dans `styles.css`
- Textes: Éditer directement dans `index.html`

## 🛠️ Build (optionnel)

Pour minifier les assets:
```bash
npm install
npm run build
```

## 📸 Screenshots

[Captures d'écran de la page]

## 🙏 Crédits

- Design & Dev: [Votre nom]
- Backend API: Constellation Tech
- IA: Google Vertex AI Imagen
```

---

## 🎬 PROMPT FINAL POUR L'AGENT

> **Résumé ultra-condensé si besoin de copier-coller dans un chat**:

```
Tu es un développeur frontend expert. Crée une landing page HTML/CSS/JS vanilla
pour "Constellation Tech" - un outil qui transforme des CVs en constellations
spatiales via IA.

SPECS TECHNIQUES:
- HTML5 sémantique + CSS3 moderne + JS ES6+ (pas de framework)
- Font: Space Mono (Google Fonts)
- Thème: Spatial, sombre, moderne, qualité "hollywoodienne"
- Background hero: constellation-hero-bg.png (haute déf, à fournir)
- Responsive: mobile-first 320px → 4K

API CONTRACT:
POST https://[CLOUD_RUN_URL]/api/generate-constellation
- Input: multipart/form-data avec file (PDF/DOCX, max 5MB)
- Output: {image_url, title, technologies[], stats, generation_time}
- Errors: 400 (invalid), 429 (quota), 500 (server)
- Timeout: 30s max, génération réelle ~15s

UI FLOW:
1. Hero: Titre + sous-titre (proposer) + bouton upload
2. Loading: Animation spatiale ~15s avec progression
3. Résultat: Image + titre + techs + stats
4. Actions: Partager LinkedIn + Copier lien + Télécharger
5. Footer: "Pas de conservation CV" + liens GitHub/LinkedIn (placeholders)

QUALITÉ:
- Animations 60fps, transitions fluides, glassmorphism
- Micro-animations hover, parallax subtil, gradient animé
- Gestion erreurs détaillée (messages par type)
- Accessibilité WCAG AA, keyboard nav, ARIA
- Performance: FCP < 1.5s, LCP < 2.5s

LIVRABLES:
- index.html (complet, commenté)
- styles.css (organisé, variables CSS)
- script.js (error handling robuste)
- README.md (déploiement GitHub Pages)
- Assets: favicons, og-image, placeholder bg

Suis EXACTEMENT le brief FRONTEND_BRIEF.md pour tous les détails.
Objective: Créer une expérience immersive de qualité production.
```

---

**FIN DU BRIEF** - Document complet et prêt à être utilisé par un agent frontend. Bonne chance ! 🚀✨
