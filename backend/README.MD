# Constellation Tech

Application de génération de constellations technologiques personnalisées à partir de CV.

## Stack Technique

- **Backend:** FastAPI + Python 3.11
- **IA:** Vertex AI Imagen (GCP)
- **Storage:** Google Cloud Storage
- **Déploiement:** Cloud Run

## Structure du Projet
```
constellation-tech/
├── backend/          # API FastAPI
│   ├── services/     # Logique métier
│   ├── models/       # Modèles Pydantic
│   ├── utils/        # Utilitaires
│   └── tests/        # Tests unitaires
├── frontend/         # Interface web
└── docs/            # Documentation
```

## Installation
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Développement
```bash
# Lancer l'API en mode dev
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

**Auteur:** Florian RADUREAU  
**Contact:** fradureau@gmail.com
**GitHub:** github.com/florianRadureau
