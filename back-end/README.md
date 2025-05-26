# Eco-Num-ESIEE - Backend

Ce backend propose une API FastAPI pour simuler la température d'un câble électrique, estimer la consommation
énergétique et les émissions de CO2 associées.

## Fonctionnalités principales

- Simulation de la température d'un câble électrique selon différents paramètres physiques.
- Calcul de la consommation énergétique et des émissions de CO2 via [CodeCarbon](https://mlco2.github.io/codecarbon/).
- Stockage et récupération de la consommation globale via Redis.
- API REST documentée (Swagger UI).

## Prérequis

- Python 3.10+
- Docker (optionnel, recommandé)
- Redis (service requis pour la persistance)

## Installation

### 1. Clonage du dépôt

```bash
git clone <repo-url>
cd back-end
```

### 2. Installation des dépendances (hors Docker)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Lancer un serveur Redis (si besoin)

```bash
docker run -d --name redis -p 6379:6379 redis
```

## Lancement

### Avec Docker

```bash
docker build -t econum-backend .
docker run --rm -p 8000:8000 --env REDIS_HOST=<host_redis> econum-backend
```

Par défaut, `REDIS_HOST=redis` (modifiable via variable d'environnement).

### Sans Docker

```bash
uvicorn main:app --reload
```

## Endpoints principaux

- `GET /` : Message de bienvenue
- `GET /health` : Vérification de l'état de l'API
- `POST /cable_temperature_simulation` : Simulation simple de température
- `POST /cable_temperature_consumption_simulation` : Simulation avec consommation énergétique et CO2
- `POST /cable_temperature_simulation_list` : Simulation sur plusieurs minutes
- `POST /cable_temperature_consumption_simulation_list` : Simulation multi-minutes avec consommation
- `GET /global_consumption` : Consommation globale cumulée
- `POST /reset_global_consumption` : Réinitialisation de la consommation globale

La documentation interactive est disponible sur `/docs`.

## Configuration

- Les paramètres Redis peuvent être définis via les variables d'environnement :
    - `REDIS_HOST` (défaut : `redis`)
    - `REDIS_PORT` (défaut : `6379`)

## Structure des dossiers

- `src/` : Code source principal (API, logique métier, accès Redis)
- `scripts/` : Notebooks et scripts de simulation
- `requirements.txt` : Dépendances Python
- `Dockerfile` : Construction de l'image Docker

## Développement

- Lancement local : voir section "Lancement"
- Pour modifier la logique métier, éditer les fichiers dans `src/`
- Pour tester la simulation, utiliser les notebooks dans `scripts/`

