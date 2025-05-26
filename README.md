# Eco-Num-ESIEE

Projet pédagogique ESIEE Paris : Plateforme de simulation de température de câble électrique, consommation énergétique et émissions de CO₂.

## Objectif

Ce projet propose une application web complète permettant de :
- Simuler la température d'un câble électrique selon différents paramètres physiques.
- Estimer la consommation énergétique et les émissions de CO₂ associées à chaque simulation.
- Visualiser les résultats et suivre la consommation globale.

## Structure du projet

```
Eco-Num-ESIEE/
│
├── back-end/      # API FastAPI, logique métier, calculs, persistance Redis
│   └── README.md
│
├── front-end/     # Application Vue 3, interface utilisateur, graphiques
│   └── README.md
│
├── docker-compose.yml  # Orchestration multi-conteneurs (API, Front, Redis)
├── LICENSE
└── README.md      # Ce fichier
```

## Démarrage rapide

### Prérequis

- Docker et Docker Compose
- (Optionnel) Python 3.10+ et Node.js 18+ pour un lancement manuel

### Lancement avec Docker Compose

```bash
docker compose up --build
```

- Frontend : [http://localhost:3000](http://localhost:3000)
- Backend (API) : [http://localhost:8000/docs](http://localhost:8000/docs)
- Redis : service interne

### Arrêt

```bash
docker compose down
```

## Technologies principales

- **Backend** : Python, FastAPI, CodeCarbon, Redis
- **Frontend** : Vue 3, TypeScript, Plotly.js, Axios, Vite
- **Conteneurisation** : Docker, Docker Compose

## Documentation détaillée

- [Documentation Backend](./back-end/README.md)
- [Documentation Frontend](./front-end/README.md)

## Licence

Ce projet est sous licence MIT.
