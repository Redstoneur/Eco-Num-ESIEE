# Rendu pour le TP

## Deadline :
**Lundi 2 juin 20h30**  
*Attention : -1pt/heure de retard à partir de là.*

---

## Attendus :

- Un (ou deux) repo GitHub avec le code du front et du back
- Des scripts de lancement front et back
- Une documentation sous MkDocs comportant :
  - Un onglet rapport
  - Un onglet documentation classique
  - Un onglet documentation technique
- Un notebook avec vos tests (vous pouvez inclure le notebook dans le MkDocs)

---

## Il faudra que le rapport comporte :

- L'architecture de votre solution
- Les performances algo avec le tableau suivant rempli :

### Tableau de performances (algo)

| Testcase                                                                 | CPU       | RAM  | Énergie | Temps de code | Complexité estimée (* = simple, ***** = très complexe) |
|--------------------------------------------------------------------------|-----------|------|---------|----------------|----------------------------------------------------------|
| Pure python (for loop)                                                  |           |      |         |                |                                                          |
| Scipy odeint                                                            |           |      |         |                |                                                          |
| **Au choix :**<br> - Jit python base (>=3.13)<br> - Jit numba            |           |      |         |                |                                                          |
| **Au choix :**<br> - cython<br> - pythermal                             |           |      |         |                |                                                          |
| Vaut-il mieux faire 30 fois 1min de prévision ou une prévision de 30min ? |           |      |         | X              | X                                                        |
| - 30x 1min : ...                                                        |           |      |         |                |                                                          |
| - 1x30min : ...                                                         |           |      |         |                |                                                          |

> - Les performances back avec la meilleure solution algo choisie en utilisant request ou Postman

---

### Testcase backend (énergie)

| Testcase                                                                                      | Énergie |
|-----------------------------------------------------------------------------------------------|---------|
| 10 utilisateurs/minute, vent, intensité change toutes les minutes                             |         |
| 100 utilisateurs/minute, vent, intensité change toutes les minutes                            |         |
| 1000 utilisateurs/minute, vent, intensité change toutes les minutes                           |         |
| 1000 utilisateurs/minute en rajoutant un cache (frauche ? via le navigateur ?)                |         |

> - L'empreinte du front (énergie)

---

## Conclusion :
**Écrivez vos préconisations pour optimiser le logiciel sur chaque composant.**
