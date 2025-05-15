"""
Module principal pour l'application de prédiction de crimes à San Francisco.

Ce module initialise l'application FastAPI, configure les routes et démarre le serveur.
Il utilise également une classe AI pour effectuer des prédictions basées sur les données fournies.
"""

####################################################################################################
### Importation des modules nécessaires ############################################################
####################################################################################################

import psutil
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from codecarbon import EmissionsTracker
import numpy as np


####################################################################################################
### Modèle de données ##############################################################################
####################################################################################################

class ConsommationResponse(BaseModel):
    """
    Modèle pour structurer la réponse de l'API de consommation.
    """
    energie: float
    unite: str
    emissions_co2: float
    unite_emissions: str

class ListConsommationResponse(BaseModel):
    """
    Modèle pour structurer la réponse de l'API de consommation.
    """
    energie: list[float]
    unite: str
    emissions_co2: list[float]
    unite_emissions: str

####################################################################################################
### Fonction générique #############################################################################
####################################################################################################

def calculer_consommation(nombre: int) -> ConsommationResponse:
    """
    Fonction générique pour calculer les émissions de CO2 basées sur la consommation d'énergie.
    :param energie: Quantité d'énergie consommée.
    :param unite: Unité de l'énergie (par défaut "kWh").
    :return: Instance de ConsommationResponse contenant les émissions de CO2.
    """
    tracker = EmissionsTracker(measure_power_secs=1, save_to_file=False)
    try:
        tracker.start()
        # Simule une consommation énergétique
        np.random.random(nombre)
        # Arrête le tracker et récupère les émissions de CO2
        emissions_co2 = tracker.stop()  # Récupère les émissions en kg de CO2
        energie_utilisee = tracker._total_energy.kWh

        return ConsommationResponse(
            energie=energie_utilisee,
            unite="kWh",
            emissions_co2=emissions_co2,  # round(emissions_co2, 4),  # Émissions de CO2 en kg
            unite_emissions="kgCO2"
        )
    except Exception as e:
        tracker.stop()
        raise ValueError(f"Erreur lors du calcul des émissions de CO2 : {str(e)}")


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

        @self.post("/consommation", response_model=ConsommationResponse)
        def calculer_consommation_api(nombre: int):
            """
            API pour calculer les émissions de CO2 basées sur une simulation de consommation d'énergie.
            :param nombre: Nombre d'éléments simulés pour la consommation d'énergie.
            :return: Instance de ConsommationResponse contenant l'énergie utilisée et les émissions de CO2 associées.
            """
            try:
                return calculer_consommation(nombre)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

        @self.post("/consommation_list", response_model=ListConsommationResponse)
        def calculer_consommation_list_api(nombre: int, repetition: int):
            """
            API pour calculer les émissions de CO2 basées sur une simulation de consommation d'énergie répétée.
            :param nombre: Nombre d'éléments simulés pour chaque consommation d'énergie.
            :param repetition: Nombre de répétitions de la simulation.
            :return: Instance de ListConsommationResponse contenant les énergies utilisées et les émissions de CO2 associées.
            """
            try:
                list_energie_utilisee = []
                list_emissions_co2 = []
                for i in range(repetition):
                    res = calculer_consommation(nombre)
                    list_energie_utilisee.append(res.energie)
                    list_emissions_co2.append(res.emissions_co2)

                return ListConsommationResponse(
                    energie=list_energie_utilisee,
                    unite="kWh",
                    emissions_co2=list_emissions_co2,
                    unite_emissions="kgCO2"
                )
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

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
