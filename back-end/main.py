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

R_cable: float = 0.0001  # Ohms (résistance du câble)
CO2_factor: int = 82  # g CO2 / kWh


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
    energie_utilisee: float
    emissions_co2: float
    temps_execution: float


class MultipleSimulationCableTemperatureResponse(BaseModel):
    """
    Modèle pour structurer la réponse de l'API de simulation de température de câble.
    """
    temperature_finale_list: List[float]
    energie_utilisee_list: List[float]
    emissions_co2_list: List[float]
    temps_execution: List[float]


####################################################################################################
### Fonction générique #############################################################################
####################################################################################################

def calculer_consommation(nombre: int) -> ConsommationResponse:
    """
    Fonction générique pour calculer les émissions de CO2 basées sur la simulation d'une consommation d'énergie.
    :param nombre: Nombre d'éléments simulés pour la consommation d'énergie.
    :return: Instance de ConsommationResponse contenant l'énergie utilisée et les émissions de CO2 associées.
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
    energy_wh: float = (R_cable * intensite_courant ** 2 * total_time_s) / 3600
    co2_emitted: float = energy_wh * CO2_factor

    print(f"Final Temperature: {final_tc:.2f}°C")
    print(f"Energy Used: {energy_wh:.4f} Wh")
    print(f"CO2 Emissions: {co2_emitted:.2f} g")
    print(f"Execution Time: {end_time - start_time:.2f} s")
    print("Simulation completed.")

    return SimulationCableTemperatureResponse(
        temperature_finale=final_tc,
        energie_utilisee=energy_wh,
        emissions_co2=co2_emitted,
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
    energie_utilisee_list: List[float] = []
    emissions_co2_list: List[float] = []
    temps_execution: List[float] = []

    temperature_cable_actuel: float = temperature_cable_initiale

    minutes_seconde = duree_minutes * 60
    for tmp in range(0, minutes_seconde, pas_seconde):
        minute = (tmp + pas_seconde) / 60
        print(f"Simulation de la minute {minute}...")

        res = simuler_temperature_cable(
            temperature_ambiante, vitesse_vent, intensite_courant, temperature_cable_actuel,
            duree_simulation_secondes=pas_seconde,
            pas_temps_microseconde=pas_microseconde
        )

        temperature_finale_list.append(res.temperature_finale)
        energie_utilisee_list.append(res.energie_utilisee)
        emissions_co2_list.append(res.emissions_co2)
        temps_execution.append(res.temps_execution)
        temperature_cable_actuel = res.temperature_finale  # Utiliser la temp finale comme nouvelle initiale

        print(
            f"Minute {minute}: Tc = {res.temperature_finale:.2f}°C,"
            f" Énergie = {res.energie_utilisee:.4f} Wh, CO2 = {res.emissions_co2:.2f} g, "
            f"Temps = {res.temps_execution:.2f} s"
        )

    return MultipleSimulationCableTemperatureResponse(
        temperature_finale_list=temperature_finale_list,
        energie_utilisee_list=energie_utilisee_list,
        emissions_co2_list=emissions_co2_list,
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

        @self.post(
            "/simulation_cable_temperature",
            response_model=SimulationCableTemperatureResponse
        )
        def simulation_cable_temperature_api(
                temperature_ambiante: float= 25,
                vitesse_vent: float = 1,
                intensite_courant: float = 300,
                temperature_cable_initiale: float = 25,
                duree_simulation_minutes: int = 60,
                pas_temps_microseconde: float = 1e-6
        ):
            """
            API pour simuler la température d'un câble électrique.
            :param request: Instance de SimulationCableTemperatureRequest contenant les paramètres de simulation.
            :return: Instance de SimulationCableTemperatureResponse contenant les résultats de la simulation.
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
                duree_minutes: int = 30,
                pas_seconde: int = 60,
                pas_microseconde: float = 1e-6,
                temperature_ambiante: float = 25,
                vitesse_vent: float = 1,
                intensite_courant: float = 300,
                temperature_cable_initiale: float = 25
        ):
            """
            API pour simuler la température d'un câble électrique sur plusieurs minutes.
            :param duree_minutes: Nombre de minutes à simuler (par défaut 30).
            :param pas_seconde: Pas de temps pour la simulation (s)
            :param pas_microseconde: Pas de temps pour la simulation (s)
            :param temperature_ambiante: Température ambiante (°C)
            :param vitesse_vent: Vitesse du vent (m/s)
            :param intensite_courant: Intensité (A)
            :param temperature_cable_initiale: Température initiale du câble
            :return: Instance de MultipleSimulationCableTemperatureResponse contenant les résultats de la simulation.
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
