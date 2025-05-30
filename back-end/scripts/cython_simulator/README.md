# cython_simulator

Ce dossier contient le module Cython pour la simulation rapide de la température du câble.

## Compilation du module

Pour compiler le module Cython, ouvrez un terminal dans ce dossier et lancez :

```bash
python setup.py build_ext --inplace
```

Cela va générer un fichier binaire (`cython_simulation.*.pyd` ou `.so`) importable dans Python.

## Utilisation dans Python

Dans votre script Python, vous pouvez importer la fonction ainsi :

```python
from cython_simulation import simulate_cython
```

## Dépendances

- Cython
- numpy
- setuptools

Installez-les si besoin :

```bash
pip install cython numpy setuptools
```

ou 

```bash
pip install -r requirements.txt
```