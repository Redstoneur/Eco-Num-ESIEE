# Scripts de simulation et de test backend

Ce dossier contient différents scripts Python pour :

- Simuler la température d'un câble électrique avec plusieurs méthodes (Python, Numba, Cython, odeint)
- Tester la consommation d'énergie de l'API backend sous charge

## Structure

- `tests_simulation.py` : Compare les performances de plusieurs méthodes de simulation.
- `simulation_preview.py` : Visualisation rapide de la simulation.
- `api_tests.py` : Teste la consommation d'énergie de l'API backend avec des appels concurrents.
- `cython_simulator/` : Module Cython pour accélérer la simulation.

## Installation

Installez les dépendances nécessaires :

```bash
pip install -r requirements.txt
```

Pour utiliser Cython, compilez le module dans `cython_simulator` :

```bash
cd cython_simulator
python setup.py build_ext --inplace
```

Pour plus de détails voir [README.md](cython_simulator/README.md)

## Utilisation

- Lancez une simulation :
  ```bash
  python tests_simulation.py
  ```
- Testez l'API backend :
  ```bash
  python api_tests.py
  ```

- Visualisez une simulation rapide :
  ```bash
  python simulation_preview.py
  ```

Assurez-vous que le backend FastAPI est démarré pour les tests API.