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


class ConsommationDirecteResponse(BaseModel):
    """
    Modèle pour structurer la réponse de l'API de consommation directe.
    """
    cpu_usage_percent: float
    consommation_estimee: float
    unite: str


class ConsommationDirecteCalculerResponse(BaseModel):
    """
    Modèle pour structurer la réponse de l'API de consommation directe calculée.
    """
    energie: float
    unite: str
    consommation_estimee: float
    cpu_usage_percent: float
    emissions_co2: float
    unite_emissions: str


####################################################################################################
### Fonction générique #############################################################################
####################################################################################################

def calculer_consommation(energie: float, unite: str = "kWh") -> ConsommationResponse:
    """
    Fonction générique pour calculer les émissions de CO2 basées sur la consommation d'énergie.
    :param energie: Quantité d'énergie consommée.
    :param unite: Unité de l'énergie (par défaut "kWh").
    :return: Instance de ConsommationResponse contenant les émissions de CO2.
    """
    try:
        return ConsommationResponse(
            energie=energie,
            unite=unite,
            emissions_co2=0,
            unite_emissions=""
        )
    except Exception as e:
        raise ValueError(f"Erreur lors du calcul des émissions de CO2 : {str(e)}")


def consommation_locale() -> ConsommationDirecteResponse:
    """
    Calcule une estimation de la consommation énergétique locale basée sur l'utilisation des
    ressources.
    :return: Instance de ConsommationDirecteResponse contenant la consommation estimée.
    """
    # Consommation approximative par CPU en kWh (à ajuster selon votre matériel)
    power_per_cpu = 0.05

    cpu_usage = psutil.cpu_percent(interval=1)  # Utilisation moyenne du CPU sur 1 seconde
    num_cpus = psutil.cpu_count(logical=True)  # Nombre de CPU logiques
    consommation = (cpu_usage / 100) * power_per_cpu * num_cpus

    return ConsommationDirecteResponse(
        cpu_usage_percent=cpu_usage,
        consommation_estimee=round(consommation, 4),  # Consommation estimée en kWh
        unite="kWh"
    )


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
        def calculer_consommation_api(energie: float, unite: str = "kWh"):
            """
            API pour calculer les émissions de CO2 basées sur la consommation d'énergie.
            :param energie: Quantité d'énergie consommée.
            :param unite: Unité de l'énergie (par défaut "kWh").
            :return: Instance de ConsommationResponse contenant les émissions de CO2.
            """
            try:
                return calculer_consommation(energie, unite)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

        @self.get("/consommation/directe", response_model=ConsommationDirecteResponse)
        def consommation_directe_api():
            """
            Retourne une estimation de la consommation d'énergie locale en direct.
            :return: Instance de ConsommationDirecteResponse contenant la consommation estimée.
            """
            try:
                return consommation_locale()
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Erreur lors du calcul de la consommation locale : {str(e)}"
                )

        @self.get(
            "/consommation/directe-calculer",
            response_model=ConsommationDirecteCalculerResponse
        )
        def consommation_directe_calculer_api():
            """
            Retourne une estimation de la consommation d'énergie locale en direct avec calcul des
            émissions de CO2.
            :return: Instance de ConsommationDirecteCalculerResponse contenant la consommation estimée
                     et les émissions de CO2.
            """
            try:
                consommation = consommation_locale()
                result = calculer_consommation(consommation.consommation_estimee,
                                               consommation.unite)
                return ConsommationDirecteCalculerResponse(
                    energie=consommation.consommation_estimee,
                    unite=consommation.unite,
                    consommation_estimee=consommation.consommation_estimee,
                    cpu_usage_percent=consommation.cpu_usage_percent,
                    emissions_co2=result.emissions_co2,
                    unite_emissions=result.unite_emissions
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Erreur lors du calcul de la consommation locale : {str(e)}"
                )


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
