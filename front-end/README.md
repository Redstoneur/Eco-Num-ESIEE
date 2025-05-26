# Eco-Num-ESIEE - Frontend

Ce frontend est une application Vue 3 + TypeScript permettant de simuler la température d'un câble électrique,
d'afficher la consommation énergétique et les émissions de CO₂, et de visualiser les résultats sous forme de graphiques
interactifs.

## Fonctionnalités

- Formulaire interactif pour paramétrer la simulation.
- Affichage des résultats détaillés et graphiques (Plotly.js).
- Suivi de la consommation énergétique globale et des émissions de CO₂.
- Intégration avec une API FastAPI (backend).
- Responsive et ergonomique.

## Prérequis

- Node.js 18+ (recommandé Node 20+)
- npm 9+
- (Optionnel) Docker

## Installation

### 1. Clonage du dépôt

```bash
git clone <repo-url>
cd front-end
```

### 2. Installation des dépendances

```bash
npm install
```

## Lancement

### En mode développement

```bash
npm run dev
```

L'application sera accessible sur [http://localhost:5173](http://localhost:5173) (ou le port affiché dans la console).

### En production (build statique)

```bash
npm run build
npm run preview
```

### Avec Docker

```bash
docker build -t econum-frontend .
docker run --rm -p 3000:3000 econum-frontend
```

L'application sera alors accessible sur [http://localhost:3000](http://localhost:3000).

## Configuration

- L'URL de l'API backend est définie dans `src/fonctions/api_client.ts` (`baseURL`).
- Par défaut : `http://localhost:8000`
- Modifiez cette valeur selon l'adresse de votre backend.

## Scripts npm

- `npm run dev` : Démarre le serveur de développement Vite.
- `npm run build` : Compile l'application pour la production.
- `npm run preview` : Sert le build de production localement.

## Structure du projet

- `src/` : Code source principal (composants, pages, styles, fonctions API)
- `components/` : Composants Vue réutilisables
- `fonctions/` : Fonctions utilitaires et client API
- `style.css` : Styles globaux

## Technologies utilisées

- [Vue 3](https://vuejs.org/)
- [TypeScript](https://www.typescriptlang.org/)
- [Vite](https://vitejs.dev/)
- [Plotly.js](https://plotly.com/javascript/)
- [vue3-plotly](https://github.com/David-Desmaisons/vue3-plotly)
- [Axios](https://axios-http.com/)

