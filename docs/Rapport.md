# Rapport technique Eco-Num-ESIEE

## Architecture de la solution

*(Schéma ou description de l’architecture front/back, Redis, etc.)*

## Performances algorithmiques

| Testcase      | CPU                                    | RAM (MB) | Énergie (kgCO2) | Temps de code (min) | Complexité estimée (* = simple, ***** = très complexe) |
|---------------|----------------------------------------|----------|-----------------|---------------------|--------------------------------------------------------|
| Boucle Python | AMD Ryzen 5 4500U with Radeon Graphics | 402.254  | 1.05817e-07     | 0                   | *                                                      |
| Scipy odeint  | AMD Ryzen 5 4500U with Radeon Graphics | 402.047  | 3.55041e-07     | 0                   | **                                                     |
| Jit numba     | AMD Ryzen 5 4500U with Radeon Graphics | 401.145  | 3.8964e-07      | 0.060668            | **                                                     |
| Cython        | AMD Ryzen 5 4500U with Radeon Graphics | 401.625  | 6.44821e-09     | 121.895             | ***                                                    |
| 30x 1min      | AMD Ryzen 5 4500U with Radeon Graphics | 402.301  | 3.20355e-06     | 2.41826             | *                                                      |
| 1x30min       | AMD Ryzen 5 4500U with Radeon Graphics | 400.684  | 3.0676e-06      | 2.31577             | *                                                      |

*(Remplir avec les résultats du notebook)*

## Performances backend (énergie)

| Testcase                         |   Énergie (kgCO2) |
|----------------------------------|-------------------|
| 10 utilisateurs/minute           |       1.74424e-05 |
| 100 utilisateurs/minute          |       0.00020747  |
| 1000 utilisateurs/minute         |       0.00238575  |
| 1000 utilisateurs/minute + cache |       0.00414722  |

## Empreinte du front

*(Mesures ou estimations)*

## Préconisations d’optimisation

- Backend : ...
- Frontend : ...
- Algorithme : ...