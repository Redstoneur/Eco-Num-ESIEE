"""
Module principal pour l'application de prédiction de crimes à San Francisco.

Ce module initialise l'application FastAPI, configure les routes et démarre le serveur.
Il utilise également une classe AI pour effectuer des prédictions basées sur les données fournies.
"""

####################################################################################################
### Importation des modules nécessaires ############################################################
####################################################################################################

import time
from typing import List

import numpy as np
from codecarbon import EmissionsTracker
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scipy.integrate import odeint

####################################################################################################
### Constantes #####################################################################################
####################################################################################################

energie_utilisee_unit: str = "kWh"  # Unité de l'énergie utilisée
emissions_co2_unit: str = "kgCO2"  # Unité des émissions de CO2


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


class SimulationCableTemperatureResponse(BaseModel):
    """
    Modèle pour structurer la réponse de l'API de simulation de température de câble.
    """
    temperature_finale: float
    temps_execution: float


class SimulationCableTemperatureConsommationResponse(BaseModel):
    """
    Modèle pour structurer la réponse de l'API de simulation de température de câble.
    """
    temperature_finale: float
    energie_utilisee: float
    energie_utilisee_unit: str
    emissions_co2: float
    emissions_co2_unit: str
    temps_execution: float


class MultipleSimulationCableTemperatureResponse(BaseModel):
    """
    Modèle pour structurer la réponse de l'API de simulation de température de câble.
    """
    temperature_finale_list: List[float]
    temps_execution: List[float]


class MultipleSimulationCableTemperatureConsommationResponse(BaseModel):
    """
    Modèle pour structurer la réponse de l'API de simulation de température de câble.
    """
    temperature_finale_list: List[float]
    energie_utilisee_list: List[float]
    energie_utilisee_cumule: float
    energie_utilisee_unit: str
    emissions_co2_list: List[float]
    emissions_co2_cumule: float
    emissions_co2_unit: str
    temps_execution: List[float]


####################################################################################################
### Fonction générique #############################################################################
####################################################################################################

def d_tc_dt(
        temperature_cable_initiale: float,
        temps: float,
        temperature_ambiante: float,
        vitesse_vent: float,
        intensite_courant: float
) -> float:
    """
    Calcule la dérivée de la température du câble à un instant donné.
    :param temperature_cable_initiale: Température actuelle du câble (°C)
    :param temps: Temps (s)
    :param temperature_ambiante: Température ambiante (°C)
    :param vitesse_vent: Vitesse du vent (m/s)
    :param intensite_courant: Intensité (A)
    :return: Dérivée de la température du câble (°C/s)
    """
    a: float = ((vitesse_vent ** 2) / 1600) * 0.4 + 0.1
    b: float = ((intensite_courant ** 1.4) / 73785) * 130
    return -(1 / 60) * a * (temperature_cable_initiale - temperature_ambiante - b)


def simuler_temperature_cable(
        temperature_ambiante: float,
        vitesse_vent: float,
        intensite_courant: float,
        temperature_cable_initiale: float,
        duree_simulation_secondes: int = 60,
        pas_temps_microseconde: float = 1e-6
) -> SimulationCableTemperatureResponse:
    """
    Simule la température du câble sur une période donnée.
    :param temperature_ambiante: Température ambiante (°C)
    :param vitesse_vent: Vitesse du vent (m/s)
    :param intensite_courant: Intensité (A)
    :param temperature_cable_initiale: Température initiale du câble (°C)
    :param duree_simulation_secondes: Durée de la simulation (s)
    :param pas_temps_microseconde: Pas de temps pour la simulation (s)
    :return: Tuple contenant la température finale du câble, l'énergie utilisée (Wh), les émissions
             de CO2 (g) et le temps d'exécution (s).
    """
    total_time_s: float = duree_simulation_secondes
    temp: np.ndarray = np.arange(0, total_time_s, pas_temps_microseconde)

    start_time: float = time.time()
    tc_sol: np.ndarray = odeint(d_tc_dt, temperature_cable_initiale, temp,
                                args=(temperature_ambiante, vitesse_vent, intensite_courant),
                                hmax=pas_temps_microseconde)
    end_time: float = time.time()

    final_tc: float = float(tc_sol[-1])

    return SimulationCableTemperatureResponse(
        temperature_finale=final_tc,
        temps_execution=end_time - start_time
    )


def simulation_temperature_cable_sur_x_minutes(
        duree_minutes: int = 30,
        pas_seconde: int = 60,
        pas_microseconde: float = 1e-6,
        temperature_ambiante: float = 25,
        vitesse_vent: float = 1,
        intensite_courant: float = 300,
        temperature_cable_initiale: float = 25
) -> MultipleSimulationCableTemperatureResponse:
    """
    Simule la température du câble sur 30 minutes, en répétant la simulation chaque minute.
    :param duree_minutes: Nombre de minutes à simuler (par défaut 30).
    :param pas_seconde: Pas de temps pour la simulation (s)
    :param pas_microseconde: Pas de temps pour la simulation (s)
    :param temperature_ambiante: Température ambiante (°C)
    :param vitesse_vent: Vitesse du vent (m/s)
    :param intensite_courant: Intensité (A)
    :param temperature_cable_initiale: Température initiale du câble
    :return: Liste des températures, énergies et émissions de CO2 pour chaque minute.
    """

    temperature_finale_list: List[float] = []
    temps_execution: List[float] = []

    temperature_cable_actuel: float = temperature_cable_initiale

    minutes_seconde = duree_minutes * 60
    for tmp in range(0, minutes_seconde, pas_seconde):
        minute = (tmp + pas_seconde) / 60

        res: SimulationCableTemperatureResponse = simuler_temperature_cable(
            temperature_ambiante, vitesse_vent, intensite_courant, temperature_cable_actuel,
            duree_simulation_secondes=pas_seconde,
            pas_temps_microseconde=pas_microseconde
        )

        temperature_finale_list.append(res.temperature_finale)
        temps_execution.append(res.temps_execution)
        temperature_cable_actuel = res.temperature_finale

    return MultipleSimulationCableTemperatureResponse(
        temperature_finale_list=temperature_finale_list,
        temps_execution=temps_execution
    )


def simuler_temperature_cable_avec_consommation(
        temperature_ambiante: float,
        vitesse_vent: float,
        intensite_courant: float,
        temperature_cable_initiale: float,
        duree_simulation_secondes: int = 60,
        pas_temps_microseconde: float = 1e-6
) -> SimulationCableTemperatureConsommationResponse:
    """
    Simule la température du câble sur une période donnée et calcule la consommation d'énergie.
    :param temperature_ambiante: Température ambiante (°C)
    :param vitesse_vent: Vitesse du vent (m/s)
    :param intensite_courant: Intensité (A)
    :param temperature_cable_initiale: Température initiale du câble (°C)
    :param duree_simulation_secondes: Durée de la simulation (s)
    :param pas_temps_microseconde: Pas de temps pour la simulation (s)
    :return: Instance de ConsommationResponse contenant l'énergie utilisée et les émissions de CO2
             associées.
    """
    tracker = EmissionsTracker(measure_power_secs=1, save_to_file=False)
    try:
        tracker.start()

        res: SimulationCableTemperatureResponse = simuler_temperature_cable(
            temperature_ambiante=temperature_ambiante,
            vitesse_vent=vitesse_vent,
            intensite_courant=intensite_courant,
            temperature_cable_initiale=temperature_cable_initiale,
            duree_simulation_secondes=duree_simulation_secondes,
            pas_temps_microseconde=pas_temps_microseconde
        )

        # Arrête le tracker et récupère les émissions de CO2
        emissions_co2 = tracker.stop()  # Récupère les émissions en kg de CO2
        energie_utilisee = tracker._total_energy.kWh

        return SimulationCableTemperatureConsommationResponse(
            temperature_finale=res.temperature_finale,
            energie_utilisee=energie_utilisee,
            energie_utilisee_unit=energie_utilisee_unit,
            emissions_co2=emissions_co2,  # round(emissions_co2, 4),  # Émissions de CO2 en kg
            emissions_co2_unit=emissions_co2_unit,
            temps_execution=res.temps_execution
        )
    except Exception as e:
        tracker.stop()
        raise ValueError(f"Erreur lors du calcul des émissions de CO2 : {str(e)}")


def simulation_temperature_cable_sur_x_minutes_avec_consommation(
        duree_minutes: int = 30,
        pas_seconde: int = 60,
        pas_microseconde: float = 1e-6,
        temperature_ambiante: float = 25,
        vitesse_vent: float = 1,
        intensite_courant: float = 300,
        temperature_cable_initiale: float = 25
) -> MultipleSimulationCableTemperatureConsommationResponse:
    """
    Simule la température du câble sur 30 minutes, en répétant la simulation chaque minute.
    :param duree_minutes: Nombre de minutes à simuler (par défaut 30).
    :param pas_seconde: Pas de temps pour la simulation (s)
    :param pas_microseconde: Pas de temps pour la simulation (s)
    :param temperature_ambiante: Température ambiante (°C)
    :param vitesse_vent: Vitesse du vent (m/s)
    :param intensite_courant: Intensité (A)
    :param temperature_cable_initiale: Température initiale du câble
    :return: Liste des températures, énergies et émissions de CO2 pour chaque minute.
    """

    temperature_finale_list: List[float] = []
    energie_utilisee_list: List[float] = []
    emissions_co2_list: List[float] = []
    temps_execution: List[float] = []

    temperature_cable_actuel: float = temperature_cable_initiale

    minutes_seconde = duree_minutes * 60
    for tmp in range(0, minutes_seconde, pas_seconde):
        minute = (tmp + pas_seconde) / 60

        res = simuler_temperature_cable_avec_consommation(
            temperature_ambiante, vitesse_vent, intensite_courant, temperature_cable_actuel,
            duree_simulation_secondes=pas_seconde,
            pas_temps_microseconde=pas_microseconde
        )

        temperature_finale_list.append(res.temperature_finale)
        energie_utilisee_list.append(res.energie_utilisee)
        emissions_co2_list.append(res.emissions_co2)
        temps_execution.append(res.temps_execution)
        temperature_cable_actuel = res.temperature_finale

    return MultipleSimulationCableTemperatureConsommationResponse(
        temperature_finale_list=temperature_finale_list,
        energie_utilisee_list=energie_utilisee_list,
        energie_utilisee_unit=energie_utilisee_unit,
        emissions_co2_list=emissions_co2_list,
        emissions_co2_unit=emissions_co2_unit,
        emissions_co2_cumule=sum(emissions_co2_list),
        energie_utilisee_cumule=sum(energie_utilisee_list),
        temps_execution=temps_execution
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

        @self.post(
            "/simulation_cable_temperature",
            response_model=SimulationCableTemperatureResponse
        )
        def simulation_cable_temperature_api(
                temperature_ambiante: float = 25,
                vitesse_vent: float = 1,
                intensite_courant: float = 300,
                temperature_cable_initiale: float = 25,
                duree_simulation_minutes: int = 60,
                pas_temps_microseconde: float = 1e-6
        ):
            """
            API pour simuler la température d'un câble électrique.
            :param temperature_ambiante: Température ambiante (°C)
            :param vitesse_vent: Vitesse du vent (m/s)
            :param intensite_courant: Intensité (A)
            :param temperature_cable_initiale: Température initiale du câble
            :param duree_simulation_minutes: Durée de la simulation (minutes)
            :param pas_temps_microseconde: Pas de temps pour la simulation (s)
            :return: Instance de SimulationCableTemperatureResponse contenant les résultats de la
                     simulation.
            """
            try:
                return simuler_temperature_cable(
                    temperature_ambiante=temperature_ambiante,
                    vitesse_vent=vitesse_vent,
                    intensite_courant=intensite_courant,
                    temperature_cable_initiale=temperature_cable_initiale,
                    duree_simulation_secondes=duree_simulation_minutes,
                    pas_temps_microseconde=pas_temps_microseconde
                )
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

        @self.post(
            "/simulation_cable_temperature_list",
            response_model=MultipleSimulationCableTemperatureResponse
        )
        def simulation_cable_temperature_list_api(
                temperature_ambiante: float = 25,
                vitesse_vent: float = 1,
                intensite_courant: float = 300,
                temperature_cable_initiale: float = 25,
                pas_seconde: int = 60,
                pas_microseconde: float = 1e-6,
                duree_minutes: int = 30
        ):
            """
            API pour simuler la température d'un câble électrique sur plusieurs minutes.

            :param temperature_ambiante: Température ambiante (°C)
            :param vitesse_vent: Vitesse du vent (m/s)
            :param intensite_courant: Intensité (A)
            :param temperature_cable_initiale: Température initiale du câble
            :param pas_seconde: Pas de temps pour la simulation (s)
            :param pas_microseconde: Pas de temps pour la simulation (s)
            :param duree_minutes: Nombre de minutes à simuler (par défaut 30).
            :return: Instance de MultipleSimulationCableTemperatureResponse contenant les résultats
                     de la simulation.
            """
            try:
                return simulation_temperature_cable_sur_x_minutes(
                    duree_minutes=duree_minutes,
                    pas_seconde=pas_seconde,
                    pas_microseconde=pas_microseconde,
                    temperature_ambiante=temperature_ambiante,
                    vitesse_vent=vitesse_vent,
                    intensite_courant=intensite_courant,
                    temperature_cable_initiale=temperature_cable_initiale
                )
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

        @self.post(
            "/simulation_cable_temperature_consommation",
            response_model=SimulationCableTemperatureConsommationResponse
        )
        def simulation_cable_temperature_consommation_api(
                temperature_ambiante: float = 25,
                vitesse_vent: float = 1,
                intensite_courant: float = 300,
                temperature_cable_initiale: float = 25,
                duree_simulation_minutes: int = 60,
                pas_temps_microseconde: float = 1e-6
        ):
            """
            API pour simuler la température d'un câble électrique avec consommation d'énergie.
            :param temperature_ambiante: Température ambiante (°C)
            :param vitesse_vent: Vitesse du vent (m/s)
            :param intensite_courant: Intensité (A)
            :param temperature_cable_initiale: Température initiale du câble
            :param duree_simulation_minutes: Durée de la simulation (minutes)
            :param pas_temps_microseconde: Pas de temps pour la simulation (s)
            :param temperature_cable_initiale: Température initiale du câble
            :param duree_simulation_minutes: Durée de la simulation (minutes)
            :return: Instance de SimulationCableTemperatureResponse contenant les résultats de la
                     simulation.
            """
            try:
                return simuler_temperature_cable_avec_consommation(
                    temperature_ambiante=temperature_ambiante,
                    vitesse_vent=vitesse_vent,
                    intensite_courant=intensite_courant,
                    temperature_cable_initiale=temperature_cable_initiale,
                    duree_simulation_secondes=duree_simulation_minutes,
                    pas_temps_microseconde=pas_temps_microseconde
                )
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

        @self.post(
            "/simulation_cable_temperature_consommation_list",
            response_model=MultipleSimulationCableTemperatureConsommationResponse
        )
        def simulation_cable_temperature_consommation_list_api(
                temperature_ambiante: float = 25,
                vitesse_vent: float = 1,
                intensite_courant: float = 300,
                temperature_cable_initiale: float = 25,
                pas_seconde: int = 60,
                pas_microseconde: float = 1e-6,
                duree_minutes: int = 30
        ):
            """
            API pour simuler la température d'un câble électrique avec consommation d'énergie sur
            plusieurs minutes.
            :param temperature_ambiante: Température ambiante (°C)
            :param vitesse_vent: Vitesse du vent (m/s)
            :param intensite_courant: Intensité (A)
            :param temperature_cable_initiale: Température initiale du câble
            :param pas_seconde: Pas de temps pour la simulation (s)
            :param pas_microseconde: Pas de temps pour la simulation (s)
            :param duree_minutes: Nombre de minutes à simuler (par défaut 30).
            :return: Instance de MultipleSimulationCableTemperatureResponse contenant les résultats
                     de la simulation.
            """
            try:
                return simulation_temperature_cable_sur_x_minutes_avec_consommation(
                    duree_minutes=duree_minutes,
                    pas_seconde=pas_seconde,
                    pas_microseconde=pas_microseconde,
                    temperature_ambiante=temperature_ambiante,
                    vitesse_vent=vitesse_vent,
                    intensite_courant=intensite_courant,
                    temperature_cable_initiale=temperature_cable_initiale
                )
            except Exception as e:
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
