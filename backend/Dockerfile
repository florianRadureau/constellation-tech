# Dockerfile pour Constellation Tech Backend
# Optimisé pour Google Cloud Run

FROM python:3.11-slim

# Variables d'environnement pour Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY pyproject.toml ./

# Installer les dépendances Python (sans dev dependencies)
RUN pip install --no-cache-dir -e .

# Copier le code de l'application
COPY . .

# Exposer le port (Cloud Run utilise PORT env var)
ENV PORT=8080
EXPOSE 8080

# Commande de démarrage
# Cloud Run définit automatiquement PORT, on l'utilise
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}
