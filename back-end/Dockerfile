# Utiliser une image de base officielle de Python
FROM python:3.10-alpine

# Variables d'environnement pour la sécurité Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Créer un utilisateur non-root
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Installer les dépendances nécessaires pour la compilation puis les supprimer après installation
RUN apk add --no-cache gcc musl-dev g++ libffi-dev \
    && mkdir -p /app \
    && chown appuser:appgroup /app

WORKDIR /app

# Copier le fichier requirements.txt dans le conteneur
COPY requirements.txt .

# Installer les dépendances
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del gcc musl-dev g++ libffi-dev

# Installer curl pour les tests de santé
RUN apk add --no-cache curl

# Copier le reste du code de l'application dans le conteneur
COPY . .

# Changer les permissions du dossier de travail
RUN chown -R appuser:appgroup /app

# Utiliser l'utilisateur non-root
USER appuser

# Exposer le port sur lequel l'application va tourner
EXPOSE 8000

# Commande pour lancer l'application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
