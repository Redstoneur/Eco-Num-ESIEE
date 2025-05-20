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

TEMPERATURE_UNIT: str = "°C"  # Unité de la température
TIME_UNIT: str = "s"  # Unité du temps
ENERGY_USED_UNIT: str = "kWh"  # Unité de l'énergie utilisée
CO2_EMISSIONS_UNIT: str = "kgCO2"  # Unité des émissions de CO2


####################################################################################################
### Modèle de données ##############################################################################
####################################################################################################

class RootResponse(BaseModel):
    """
    Modèle pour structurer la réponse de l'API racine.
    """
    message: str


class HealthCheckResponse(BaseModel):
    """
    Modèle pour structurer la réponse de l'API de vérification de l'état.
    """
    status: str = "alive"


class CableTemperatureSimulationResponse(BaseModel):
    """
    Modèle pour structurer la réponse de l'API de simulation de température de câble.
    """
    final_temperature: float
    final_temperature_unit: str = TEMPERATURE_UNIT
    execution_time: float
    execution_time_unit: str = TIME_UNIT


class CableTemperatureConsumptionSimulationResponse(BaseModel):
    """
    Modèle pour structurer la réponse de l'API de simulation de température de câble.
    """
    final_temperature: float
    final_temperature_unit: str = TEMPERATURE_UNIT
    energy_used: float
    energy_used_unit: str = ENERGY_USED_UNIT
    co2_emissions: float
    co2_emissions_unit: str = CO2_EMISSIONS_UNIT
    execution_time: float
    execution_time_unit: str = TIME_UNIT


class MultipleCableTemperatureSimulationResponse(BaseModel):
    """
    Modèle pour structurer la réponse de l'API de simulation de température de câble.
    """
    final_temperature_list: List[float]
    final_temperature_unit: str = TEMPERATURE_UNIT
    execution_time: List[float]
    cumulative_execution_time: float
    execution_time_unit: str = TIME_UNIT


class MultipleCableTemperatureConsumptionSimulationResponse(BaseModel):
    """
    Modèle pour structurer la réponse de l'API de simulation de température de câble.
    """
    final_temperature_list: List[float]
    final_temperature_unit: str = TEMPERATURE_UNIT
    energy_used_list: List[float]
    cumulative_energy_used: float
    energy_used_unit: str = ENERGY_USED_UNIT
    co2_emissions_list: List[float]
    cumulative_co2_emissions: float
    co2_emissions_unit: str = CO2_EMISSIONS_UNIT
    execution_time: List[float]
    cumulative_execution_time: float
    execution_time_unit: str = TIME_UNIT


class GlobalConsumptionResponse(BaseModel):
    """
    Modèle pour structurer la réponse de l'API pour voir la consommation globale.
    """
    energy_used: float = 0
    energy_used_list: List[float] = []
    energy_used_unit: str = ENERGY_USED_UNIT
    co2_emissions: float = 0
    co2_emissions_list: List[float] = []
    co2_emissions_unit: str = CO2_EMISSIONS_UNIT


####################################################################################################
### Variables globales #############################################################################
####################################################################################################

global_consumption: GlobalConsumptionResponse = GlobalConsumptionResponse()


####################################################################################################
### Fonction générique #############################################################################
####################################################################################################

def d_tc_dt(
        cable_temperature_initial: float,
        time_s: float,
        ambient_temperature: float,
        wind_speed: float,
        current_intensity: float
) -> float:
    """
    Calcule la dérivée de la température du câble à un instant donné.
    :param cable_temperature_initial: Température actuelle du câble (°C)
    :param time_s: Temps (s)
    :param ambient_temperature: Température ambiante (°C)
    :param wind_speed: Vitesse du vent (m/s)
    :param current_intensity: Intensité (A)
    :return: Dérivée de la température du câble (°C/s)
    """
    a: float = ((wind_speed ** 2) / 1600) * 0.4 + 0.1
    b: float = ((current_intensity ** 1.4) / 73785) * 130
    return -(1 / 60) * a * (cable_temperature_initial - ambient_temperature - b)


def simulate_cable_temperature(
        ambient_temperature: float,
        wind_speed: float,
        current_intensity: float,
        cable_temperature_initial: float,
        simulation_duration_seconds: int = 60,
        time_step_microsecond: float = 1e-6
) -> CableTemperatureSimulationResponse:
    """
    Simule la température du câble sur une période donnée.
    :param ambient_temperature: Température ambiante (°C)
    :param wind_speed: Vitesse du vent (m/s)
    :param current_intensity: Intensité (A)
    :param cable_temperature_initial: Température initiale du câble (°C)
    :param simulation_duration_seconds: Durée de la simulation (s)
    :param time_step_microsecond: Pas de temps pour la simulation (s)
    :return: Tuple contenant la température finale du câble, l'énergie utilisée (Wh), les émissions
             de CO2 (g) et le temps d'exécution (s).
    """
    total_time_s: float = simulation_duration_seconds
    time_s: np.ndarray = np.arange(0, total_time_s, time_step_microsecond)

    start_time: float = time.time()
    tc_sol: np.ndarray = odeint(d_tc_dt, cable_temperature_initial, time_s,
                                args=(ambient_temperature, wind_speed, current_intensity),
                                hmax=time_step_microsecond)
    end_time: float = time.time()

    final_tc: float = float(tc_sol[-1])

    return CableTemperatureSimulationResponse(
        final_temperature=final_tc,
        execution_time=end_time - start_time
    )


def simulate_cable_temperature_over_x_minutes(
        duration_minutes: int = 30,
        step_seconds: int = 60,
        step_microsecond: float = 1e-6,
        ambient_temperature: float = 25,
        wind_speed: float = 1,
        current_intensity: float = 300,
        cable_temperature_initial: float = 25
) -> MultipleCableTemperatureSimulationResponse:
    """
    Simule la température du câble sur 30 minutes, en répétant la simulation chaque minute.
    :param duration_minutes: Nombre de minutes à simuler (par défaut 30).
    :param step_seconds: Pas de temps pour la simulation (s)
    :param step_microsecond: Pas de temps pour la simulation (s)
    :param ambient_temperature: Température ambiante (°C)
    :param wind_speed: Vitesse du vent (m/s)
    :param current_intensity: Intensité (A)
    :param cable_temperature_initial: Température initiale du câble
    :return: Liste des températures, énergies et émissions de CO2 pour chaque minute.
    """

    final_temperature_list: List[float] = []
    execution_time: List[float] = []

    current_cable_temperature: float = cable_temperature_initial

    minutes_seconds = duration_minutes * 60
    for tmp in range(0, minutes_seconds, step_seconds):
        res: CableTemperatureSimulationResponse = simulate_cable_temperature(
            ambient_temperature, wind_speed, current_intensity, current_cable_temperature,
            simulation_duration_seconds=step_seconds,
            time_step_microsecond=step_microsecond
        )

        final_temperature_list.append(res.final_temperature)
        execution_time.append(res.execution_time)
        current_cable_temperature = res.final_temperature

    return MultipleCableTemperatureSimulationResponse(
        final_temperature_list=final_temperature_list,
        execution_time=execution_time,
        cumulative_execution_time=sum(execution_time)
    )


def simulate_cable_temperature_with_consumption(
        ambient_temperature: float,
        wind_speed: float,
        current_intensity: float,
        cable_temperature_initial: float,
        simulation_duration_seconds: int = 60,
        time_step_microsecond: float = 1e-6
) -> CableTemperatureConsumptionSimulationResponse:
    """
    Simule la température du câble sur une période donnée et calcule la consommation d'énergie.
    :param ambient_temperature: Température ambiante (°C)
    :param wind_speed: Vitesse du vent (m/s)
    :param current_intensity: Intensité (A)
    :param cable_temperature_initial: Température initiale du câble (°C)
    :param simulation_duration_seconds: Durée de la simulation (s)
    :param time_step_microsecond: Pas de temps pour la simulation (s)
    :return: Instance de ConsommationResponse contenant l'énergie utilisée et les émissions de CO2
             associées.
    """
    tracker = EmissionsTracker(measure_power_secs=1, save_to_file=False)
    try:
        tracker.start()

        res: CableTemperatureSimulationResponse = simulate_cable_temperature(
            ambient_temperature=ambient_temperature,
            wind_speed=wind_speed,
            current_intensity=current_intensity,
            cable_temperature_initial=cable_temperature_initial,
            simulation_duration_seconds=simulation_duration_seconds,
            time_step_microsecond=time_step_microsecond
        )

        # Arrête le tracker et récupère les émissions de CO2
        co2_emissions = tracker.stop()  # Récupère les émissions en kg de CO2
        energy_used = tracker._total_energy.kWh

        return CableTemperatureConsumptionSimulationResponse(
            final_temperature=res.final_temperature,
            energy_used=energy_used,
            co2_emissions=co2_emissions,
            execution_time=res.execution_time
        )
    except Exception as e:
        tracker.stop()
        raise ValueError(f"Erreur lors du calcul des émissions de CO2 : {str(e)}")


def simulate_cable_temperature_over_x_minutes_with_consumption(
        duration_minutes: int = 30,
        step_seconds: int = 60,
        step_microsecond: float = 1e-6,
        ambient_temperature: float = 25,
        wind_speed: float = 1,
        current_intensity: float = 300,
        cable_temperature_initial: float = 25
) -> MultipleCableTemperatureConsumptionSimulationResponse:
    """
    Simule la température du câble sur 30 minutes, en répétant la simulation chaque minute.
    :param duration_minutes: Nombre de minutes à simuler (par défaut 30).
    :param step_seconds: Pas de temps pour la simulation (s)
    :param step_microsecond: Pas de temps pour la simulation (s)
    :param ambient_temperature: Température ambiante (°C)
    :param wind_speed: Vitesse du vent (m/s)
    :param current_intensity: Intensité (A)
    :param cable_temperature_initial: Température initiale du câble
    :return: Liste des températures, énergies et émissions de CO2 pour chaque minute.
    """

    final_temperature_list: List[float] = []
    energy_used_list: List[float] = []
    co2_emissions_list: List[float] = []
    execution_time: List[float] = []

    current_cable_temperature: float = cable_temperature_initial

    minutes_seconds = duration_minutes * 60
    for tmp in range(0, minutes_seconds, step_seconds):
        res = simulate_cable_temperature_with_consumption(
            ambient_temperature, wind_speed, current_intensity, current_cable_temperature,
            simulation_duration_seconds=step_seconds,
            time_step_microsecond=step_microsecond
        )

        final_temperature_list.append(res.final_temperature)
        energy_used_list.append(res.energy_used)
        co2_emissions_list.append(res.co2_emissions)
        execution_time.append(res.execution_time)
        current_cable_temperature = res.final_temperature

    return MultipleCableTemperatureConsumptionSimulationResponse(
        final_temperature_list=final_temperature_list,
        energy_used_list=energy_used_list,
        cumulative_energy_used=sum(energy_used_list),
        co2_emissions_list=co2_emissions_list,
        cumulative_co2_emissions=sum(co2_emissions_list),
        execution_time=execution_time,
        cumulative_execution_time=sum(execution_time)
    )


def update_global_consumption(var: CableTemperatureConsumptionSimulationResponse):
    """
    Met à jour la consommation globale.
    :param var: Instance de CableTemperatureConsumptionSimulationResponse contenant les données de
                consommation.
    """
    global global_consumption
    global_consumption.energy_used += var.energy_used
    global_consumption.energy_used_list.append(var.energy_used)
    global_consumption.co2_emissions += var.co2_emissions
    global_consumption.co2_emissions_list.append(var.co2_emissions)


def update_global_consumption_list(var: MultipleCableTemperatureConsumptionSimulationResponse):
    """
    Met à jour la consommation globale avec une liste de valeurs.
    :param var: Instance de MultipleCableTemperatureConsumptionSimulationResponse contenant les
                données de consommation.
    """
    global global_consumption
    global_consumption.energy_used += var.cumulative_energy_used
    global_consumption.energy_used_list.extend(var.energy_used_list)
    global_consumption.co2_emissions += var.cumulative_co2_emissions
    global_consumption.co2_emissions_list.extend(var.co2_emissions_list)


def reset_global_consumption():
    """
    Réinitialise la consommation globale.
    """
    global global_consumption
    global_consumption = GlobalConsumptionResponse()


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

        @self.get(
            "/",
            tags=["Root"],
            response_model=RootResponse
        )
        def read_root():
            """
            Point de terminaison GET qui retourne un message de bienvenue.

            **Retour :**
            - Instance de `RootResponse` contenant un message de bienvenue.

            """
            return RootResponse(
                message="Bienvenue sur l'API Eco-Num-ESIEE !"
            )

        @self.get(
            "/health",
            tags=["Health"],
            response_model=HealthCheckResponse
        )
        def health_check():
            """
            Point de terminaison GET pour vérifier l'état de l'API.

            **Retour :**
            - Instance de `HealthCheckResponse` contenant le statut de l'API.

            """
            return HealthCheckResponse()

        @self.post(
            "/cable_temperature_simulation",
            tags=["Simulation"],
            response_model=CableTemperatureSimulationResponse,
            responses={
                400: {
                    "description": "Erreur lors de la simulation de la température du câble.",
                    "content": {
                        "application/json": {
                            "example": {
                                "detail": "Erreur lors de la simulation de la température du câble."
                            }
                        }
                    }
                }
            }
        )
        def cable_temperature_simulation_api(
                ambient_temperature: float = 25,
                wind_speed: float = 1,
                current_intensity: float = 300,
                initial_cable_temperature: float = 25,
                simulation_duration_minutes: int = 60,
                time_step_microsecond: float = 1e-6
        ):
            """
            API pour simuler la température d’un câble électrique.

            **Paramètres :**
            - **ambient_temperature** (_float_, optionnel) : Température ambiante
              (_°C_, défaut : 25)
            - **wind_speed** (_float_, optionnel) : Vitesse du vent (_m/s_, défaut : 1)
            - **current_intensity** (_float_, optionnel) : Intensité du courant (_A_, défaut : 300)
            - **initial_cable_temperature** (_float_, optionnel) : Température initiale du câble
              (_°C_, défaut : 25)
            - **simulation_duration_minutes** (_int_, optionnel) : Durée de la simulation
              (_minutes_, défaut : 60)
            - **time_step_microsecond** (_float_, optionnel) : Pas de temps pour la simulation
              (_s_, défaut : 1e-6)

            **Retour :**
            - Instance de `CableTemperatureSimulationResponse` contenant les résultats de la
              simulation.
            """
            try:
                res: CableTemperatureConsumptionSimulationResponse = (
                    simulate_cable_temperature_with_consumption(
                        ambient_temperature=ambient_temperature,
                        wind_speed=wind_speed,
                        current_intensity=current_intensity,
                        cable_temperature_initial=initial_cable_temperature,
                        simulation_duration_seconds=simulation_duration_minutes,
                        time_step_microsecond=time_step_microsecond
                    )
                )

                update_global_consumption(res)
                return CableTemperatureSimulationResponse(
                    final_temperature=res.final_temperature,
                    execution_time=res.execution_time
                )
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

        @self.post(
            "/cable_temperature_simulation_list",
            tags=["Simulation"],
            response_model=MultipleCableTemperatureSimulationResponse,
            responses={
                400: {
                    "description": "Erreur lors de la simulation de la température du câble.",
                    "content": {
                        "application/json": {
                            "example": {
                                "detail": "Erreur lors de la simulation de la température du câble."
                            }
                        }
                    }
                }
            }
        )
        def cable_temperature_simulation_list_api(
                ambient_temperature: float = 25,
                wind_speed: float = 1,
                current_intensity: float = 300,
                initial_cable_temperature: float = 25,
                step_seconds: int = 60,
                step_microsecond: float = 1e-6,
                duration_minutes: int = 30
        ):
            """
            API permettant de simuler la température d’un câble électrique sur plusieurs minutes.

            **Paramètres :**
            - **ambient_temperature** (_float_, optionnel) : Température ambiante
              (_°C_, défaut : 25)
            - **wind_speed** (_float_, optionnel) : Vitesse du vent (_m/s_, défaut : 1)
            - **current_intensity** (_float_, optionnel) : Intensité du courant (_A_, défaut : 300)
            - **initial_cable_temperature** (_float_, optionnel) : Température initiale du câble
              (_°C_, défaut : 25)
            - **step_seconds** (_int_, optionnel) : Pas de temps pour la simulation
              (_s_, défaut : 60)
            - **step_microsecond** (_float_, optionnel) : Pas de temps pour la simulation
              (_s_, défaut : 1e-6)
            - **duration_minutes** (_int_, optionnel) : Nombre de minutes à simuler (_défaut : 30_)

            **Retour :**
            - Instance de `MultipleCableTemperatureSimulationResponse` contenant les résultats de la
              simulation.
            """
            try:
                res: MultipleCableTemperatureConsumptionSimulationResponse = (
                    simulate_cable_temperature_over_x_minutes_with_consumption(
                        duration_minutes=duration_minutes,
                        step_seconds=step_seconds,
                        step_microsecond=step_microsecond,
                        ambient_temperature=ambient_temperature,
                        wind_speed=wind_speed,
                        current_intensity=current_intensity,
                        cable_temperature_initial=initial_cable_temperature
                    )
                )

                update_global_consumption_list(res)
                return MultipleCableTemperatureSimulationResponse(
                    final_temperature_list=res.final_temperature_list,
                    execution_time=res.execution_time,
                    cumulative_execution_time=res.cumulative_execution_time
                )

            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

        @self.post(
            "/cable_temperature_consumption_simulation",
            tags=["Simulation"],
            response_model=CableTemperatureConsumptionSimulationResponse,
            responses={
                400: {
                    "description": "Erreur lors de la simulation de la température du câble.",
                    "content": {
                        "application/json": {
                            "example": {
                                "detail": "Erreur lors de la simulation de la température du câble."
                            }
                        }
                    }
                }
            }
        )
        def cable_temperature_consumption_simulation_api(
                ambient_temperature: float = 25,
                wind_speed: float = 1,
                current_intensity: float = 300,
                initial_cable_temperature: float = 25,
                simulation_duration_minutes: int = 60,
                time_step_microsecond: float = 1e-6
        ):
            """
            API pour simuler la température d’un câble électrique avec consommation d’énergie.

            **Paramètres :**
            - **ambient_temperature** (_float_, optionnel) : Température ambiante
              (_°C_, défaut : 25)
            - **wind_speed** (_float_, optionnel) : Vitesse du vent (_m/s_, défaut : 1)
            - **current_intensity** (_float_, optionnel) : Intensité du courant (_A_, défaut : 300)
            - **initial_cable_temperature** (_float_, optionnel) : Température initiale du câble
              (_°C_, défaut : 25)
            - **simulation_duration_minutes** (_int_, optionnel) : Durée de la simulation
              (_minutes_, défaut : 60)
            - **time_step_microsecond** (_float_, optionnel) : Pas de temps pour la simulation
              (_s_, défaut : 1e-6)

            **Retour :**
            - Instance de `CableTemperatureConsumptionSimulationResponse` contenant les résultats
              de la simulation.
            """
            try:
                res: CableTemperatureConsumptionSimulationResponse = (
                    simulate_cable_temperature_with_consumption(
                        ambient_temperature=ambient_temperature,
                        wind_speed=wind_speed,
                        current_intensity=current_intensity,
                        cable_temperature_initial=initial_cable_temperature,
                        simulation_duration_seconds=simulation_duration_minutes,
                        time_step_microsecond=time_step_microsecond
                    )
                )

                update_global_consumption(res)

                return res
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

        @self.post(
            "/cable_temperature_consumption_simulation_list",
            tags=["Simulation"],
            response_model=MultipleCableTemperatureConsumptionSimulationResponse,
            responses={
                400: {
                    "description": "Erreur lors de la simulation de la température du câble.",
                    "content": {
                        "application/json": {
                            "example": {
                                "detail": "Erreur lors de la simulation de la température du câble."
                            }
                        }
                    }
                }
            }
        )
        def cable_temperature_consumption_simulation_list_api(
                ambient_temperature: float = 25,
                wind_speed: float = 1,
                current_intensity: float = 300,
                initial_cable_temperature: float = 25,
                step_seconds: int = 60,
                step_microsecond: float = 1e-6,
                duration_minutes: int = 30
        ):
            """
            API permettant de simuler la température d’un câble électrique avec consommation
            d’énergie sur plusieurs minutes.

            **Paramètres :**
            - **ambient_temperature** (_float_, optionnel) : Température ambiante
              (_°C_, défaut : 25)
            - **wind_speed** (_float_, optionnel) : Vitesse du vent (_m/s_, défaut : 1)
            - **current_intensity** (_float_, optionnel) : Intensité du courant (_A_, défaut : 300)
            - **initial_cable_temperature** (_float_, optionnel) : Température initiale du câble
              (_°C_, défaut : 25)
            - **step_seconds** (_int_, optionnel) : Pas de temps pour la simulation
              (_s_, défaut : 60)
            - **step_microsecond** (_float_, optionnel) : Pas de temps pour la simulation
              (_s_, défaut : 1e-6)
            - **duration_minutes** (_int_, optionnel) : Nombre de minutes à simuler (_défaut : 30_)

            **Retour :**
            - Instance de `MultipleCableTemperatureConsumptionSimulationResponse` contenant les
              résultats de la simulation.
            """
            try:
                res: MultipleCableTemperatureConsumptionSimulationResponse = (
                    simulate_cable_temperature_over_x_minutes_with_consumption(
                        duration_minutes=duration_minutes,
                        step_seconds=step_seconds,
                        step_microsecond=step_microsecond,
                        ambient_temperature=ambient_temperature,
                        wind_speed=wind_speed,
                        current_intensity=current_intensity,
                        cable_temperature_initial=initial_cable_temperature
                    )
                )

                update_global_consumption_list(res)
                return res
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

        @self.get(
            "/global_consumption",
            tags=["Global Consumption"],
            response_model=GlobalConsumptionResponse,
            responses={
                400: {
                    "description": "Erreur lors de la récupération de la consommation globale.",
                    "content": {
                        "application/json": {
                            "example": {
                                "detail": "Erreur lors de la récupération de la consommation"
                                          " globale."
                            }
                        }
                    }
                }
            }
        )
        def global_consumption_api():
            """
            API pour obtenir la consommation globale.

            **Retour :**
            - Instance de `GlobalConsumptionResponse` contenant les données de consommation
              générale.
            """
            try:
                return global_consumption
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

        @self.post(
            "/reset_global_consumption",
            tags=["Global Consumption"],
            response_model=GlobalConsumptionResponse,
            responses={
                400: {
                    "description": "Erreur lors de la réinitialisation de la consommation globale.",
                    "content": {
                        "application/json": {
                            "example": {
                                "detail": "Erreur lors de la réinitialisation de la consommation"
                                          " globale."
                            }
                        }
                    }
                }
            }
        )
        def reset_global_consumption_api():
            """
            API pour réinitialiser la consommation globale.

            **Retour :**
            - Instance de `GlobalConsumptionResponse` contenant les données de consommation
              réinitialisées.
            """
            try:
                reset_global_consumption()
                return global_consumption
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
    uvicorn.run(app, host="127.0.0.1", port=9000)

####################################################################################################
### Fin du fichier address.py ######################################################################
####################################################################################################
