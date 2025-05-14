"""
Module principal pour l'application de prédiction de crimes à San Francisco.

Ce module initialise l'application FastAPI, configure les routes et démarre le serveur.
Il utilise également une classe AI pour effectuer des prédictions basées sur les données fournies.
"""

####################################################################################################
### Importation des modules nécessaires ############################################################
####################################################################################################

from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


####################################################################################################
### Modèle de données ##############################################################################
####################################################################################################


class Date(BaseModel):
    """
    Modèle Pydantic représentant une date avec des attributs d'année, de mois et de jour.
    """
    annee: int
    mois: int
    jour: int
    heure: int
    minute: int
    seconde: int

    def __str__(self):
        """
        Retourne une chaîne de caractères représentant la date.
        :return: Chaîne de caractères représentant la date au format "AAAA-MM-JJ HH:MM:SS".
        """
        return (
            f"{self.annee}-{self.mois:02d}-{self.jour:02d}"
            f" "
            f"{self.heure:02d}:{self.minute:02d}:{self.seconde:02d}"
        )

    def __datetime__(self):
        """
        Retourne un objet datetime représentant la date.
        :return: Objet datetime représentant la date.
        """
        return datetime.strptime(self.__str__(), "%Y-%m-%d %H:%M:%S")

    def __day_of_week__(self):
        """
        Retourne le jour de la semaine.
        :return: Jour de la semaine.
        """
        return self.__datetime__().strftime("%A")

    def __is_valide__(self):
        """
        Vérifie si la date est valide.
        :return: True si la date est valide, False sinon.
        """
        try:
            self.__datetime__()
            return True
        except ValueError:
            return False


####################################################################################################
### Classe personnalisée FastAPI ###################################################################
####################################################################################################

class MyAPI(FastAPI):
    """
    Classe personnalisée FastAPI qui initialise les routes.
    """

    def __init__(self):
        """
        Initialise l'application FastAPI et ajoute les routes.
        """
        super().__init__(
            title="Eco-Num-ESIEE",
            description="API",
            version="1.0.0",
            docs_url="/docs",  # URL pour Swagger UI
            redoc_url="/redoc"  # URL pour ReDoc
        )
        # noinspection PyTypeChecker
        self.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Permettre toutes les origines, à ajuster selon vos besoins
            allow_credentials=True,
            allow_methods=["*"],  # Permettre toutes les méthodes HTTP
            allow_headers=["*"],  # Permettre tous les en-têtes
        )
        self.add_routes()

    def add_routes(self):
        """
        Ajoute des routes à l'application FastAPI.
        """

        @self.get("/")
        def read_root():
            """
            Point de terminaison GET qui retourne un message de bienvenue.
            """
            return {"message": "Bonjour, le monde!"}


####################################################################################################
### Point d'entrée de l'application ################################################################
####################################################################################################

# Crée une instance de l'application FastAPI
app = MyAPI()

####################################################################################################
### Test d'utilisation #############################################################################
####################################################################################################


# Si le script est exécuté directement, démarre le serveur FastAPI
if __name__ == "__main__":
    # Importe uvicorn et démarre le serveur FastAPI
    import uvicorn

    # Démarre le serveur FastAPI
    uvicorn.run(app, host="127.0.0.1", port=8000)

####################################################################################################
### Fin du fichier address.py ######################################################################
####################################################################################################
