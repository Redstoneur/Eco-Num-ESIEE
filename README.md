# Eco-Num-ESIEE

---

![License](https://img.shields.io/github/license/Redstoneur/Eco-Num-ESIEE)
![Top Language](https://img.shields.io/github/languages/top/Redstoneur/Eco-Num-ESIEE)
![Python Version](https://img.shields.io/badge/python-3.10+-blue)
![Node Version](https://img.shields.io/badge/Node-22+-green)
![Size](https://img.shields.io/github/repo-size/Redstoneur/Eco-Num-ESIEE)
![Contributors](https://img.shields.io/github/contributors/Redstoneur/Eco-Num-ESIEE)
![Last Commit](https://img.shields.io/github/last-commit/Redstoneur/Eco-Num-ESIEE)
![Issues](https://img.shields.io/github/issues/Redstoneur/Eco-Num-ESIEE)
![Pull Requests](https://img.shields.io/github/issues-pr/Redstoneur/Eco-Num-ESIEE)

---

![Forks](https://img.shields.io/github/forks/Redstoneur/Eco-Num-ESIEE)
![Stars](https://img.shields.io/github/stars/Redstoneur/Eco-Num-ESIEE)
![Watchers](https://img.shields.io/github/watchers/Redstoneur/Eco-Num-ESIEE)

---

![Latest Release](https://img.shields.io/github/v/release/Redstoneur/Eco-Num-ESIEE)

![Release Date](https://img.shields.io/github/release-date/Redstoneur/Eco-Num-ESIEE)

---

Projet pédagogique ESIEE Paris : Plateforme de simulation de température de câble électrique, consommation énergétique
et émissions de CO₂.

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

## Documentation

- [Documentation Backend](./back-end/README.md)
- [Documentation Frontend](./front-end/README.md)
- [Rapport technique](docs/Rapport.md)
- [Documentation pour les Notebooks version script](./back-end/scripts/README.md)
- [Documentation Notebooks](notebooks/README.md)
- [Notebook de tests](notebooks/tests_simulation.ipynb)
- [Notebook de test des API](notebooks/api_tests.ipynb)
- [Notebook de preview de fonctionnement pour les API](notebooks/simulation_preview.ipynb)

## Licence

Ce projet est sous licence MIT.
