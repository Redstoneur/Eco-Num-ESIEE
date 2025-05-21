"""
Module principal pour l'application de prédiction de crimes à San Francisco.

Ce module initialise l'application FastAPI, configure les routes et démarre le serveur.
Il utilise également une classe AI pour effectuer des prédictions basées sur les données fournies.
"""

####################################################################################################
### Importation des modules nécessaires ############################################################
####################################################################################################

import time
from decimal import Decimal, getcontext
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
    temperature_list: List[float]
    temperature_range_time_list: List[float]


class CableTemperatureConsumptionSimulationResponse(BaseModel):
    """
    Modèle pour structurer la réponse de l'API de simulation de température de câble.
    """
    final_temperature: float
    final_temperature_unit: str = TEMPERATURE_UNIT
    execution_time: float
    execution_time_unit: str = TIME_UNIT
    temperature_list: List[float]
    temperature_range_time_list: List[float]
    energy_used: float
    energy_used_unit: str = ENERGY_USED_UNIT
    co2_emissions: float
    co2_emissions_unit: str = CO2_EMISSIONS_UNIT


class GlobalConsumptionResponse(BaseModel):
    """
    Modèle pour structurer la réponse de l'API pour voir la consommation globale.
    """
    energy_used: float = 0
    maximum_energy_used: float = 0
    minimum_energy_used: float = 0
    energy_used_list: List[float] = []
    energy_used_unit: str = ENERGY_USED_UNIT
    co2_emissions: float = 0
    maximum_co2_emissions: float = 0
    minimum_co2_emissions: float = 0
    co2_emissions_list: List[float] = []
    co2_emissions_unit: str = CO2_EMISSIONS_UNIT


####################################################################################################
### Variables globales #############################################################################
####################################################################################################

global_consumption: GlobalConsumptionResponse = GlobalConsumptionResponse()

getcontext().prec = 28


####################################################################################################
### Fonction générique #############################################################################
####################################################################################################

def modulo(a: float, b: float) -> Decimal:
    """
    Retourne a modulo b en utilisant Decimal pour éviter les erreurs de flottants.

    Paramètres :
    - a : float ou str ou Decimal
    - b : float ou str ou Decimal

    Retour : Decimal (résultat du modulo avec haute précision)
    """
    a_dec: Decimal = Decimal(str(a))
    b_dec: Decimal = Decimal(str(b))

    resultat: Decimal = a_dec % b_dec

    if b < 0:
        resultat = Decimal(round(resultat, 6))

    return a_dec % b_dec


def update_global_consumption(
        energy_used: float,
        co2_emissions: float
):
    """
    Met à jour la consommation globale.
    :param energy_used: Énergie utilisée (kWh)
    :param co2_emissions: Émissions de CO2 (kgCO2)
    """
    global global_consumption

    global_consumption.energy_used += energy_used
    global_consumption.maximum_energy_used = max(
        global_consumption.maximum_energy_used,
        energy_used
    )
    global_consumption.minimum_energy_used = min(
        global_consumption.minimum_energy_used,
        energy_used
    )

    global_consumption.co2_emissions += co2_emissions
    global_consumption.maximum_co2_emissions = max(
        global_consumption.maximum_co2_emissions,
        co2_emissions
    )
    global_consumption.minimum_co2_emissions = min(
        global_consumption.minimum_co2_emissions,
        co2_emissions
    )
    global_consumption.energy_used_list.append(energy_used)
    global_consumption.co2_emissions_list.append(co2_emissions)


def reset_global_consumption():
    """
    Réinitialise la consommation globale.
    """
    global global_consumption
    global_consumption = GlobalConsumptionResponse()


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
        time_step: float = 1e-6
) -> CableTemperatureSimulationResponse:
    """
    Simule la température du câble sur une période donnée.
    :param ambient_temperature: Température ambiante (°C)
    :param wind_speed: Vitesse du vent (m/s)
    :param current_intensity: Intensité (A)
    :param cable_temperature_initial: Température initiale du câble (°C)
    :param simulation_duration_seconds: Durée de la simulation (s)
    :param time_step: Pas de temps pour la simulation (s)
    :return: Tuple contenant la température finale du câble, l'énergie utilisée (Wh), les émissions
             de CO2 (g) et le temps d'exécution (s).
    """
    total_time_s: float = simulation_duration_seconds
    time_s: np.ndarray = np.arange(0, total_time_s, time_step)

    start_time: float = time.time()
    tc_sol: np.ndarray = odeint(d_tc_dt, cable_temperature_initial, time_s,
                                args=(ambient_temperature, wind_speed, current_intensity),
                                hmax=time_step)
    end_time: float = time.time()

    final_tc: float = float(tc_sol[-1])

    # Calcul du pas pour limiter la taille des tableaux
    max_points = 22_000_000  # Nombre maximum de points souhaités
    step = max(1, len(tc_sol) // max_points)

    # Création des listes avec un pas régulier
    temperature_list: List[float] = [float(tc_sol[i]) for i in range(0, len(tc_sol), step)]
    temperature_range_time_list: List[float] = [time_s[i] for i in range(0, len(time_s), step)]

    # Ajout de la dernière valeur si elle n'est pas incluse
    if len(tc_sol) - 1 not in range(0, len(tc_sol), step):
        temperature_list.append(float(tc_sol[-1]))
        temperature_range_time_list.append(time_s[-1])

    return CableTemperatureSimulationResponse(
        final_temperature=final_tc,
        execution_time=end_time - start_time,
        temperature_list=temperature_list,
        temperature_range_time_list=temperature_range_time_list
    )


def simulate_cable_temperature_with_consumption(
        ambient_temperature: float,
        wind_speed: float,
        current_intensity: float,
        cable_temperature_initial: float,
        simulation_duration_seconds: int = 60,
        time_step: float = 1e-6
) -> CableTemperatureConsumptionSimulationResponse:
    """
    Simule la température du câble sur une période donnée et calcule la consommation d'énergie.
    :param ambient_temperature: Température ambiante (°C)
    :param wind_speed: Vitesse du vent (m/s)
    :param current_intensity: Intensité (A)
    :param cable_temperature_initial: Température initiale du câble (°C)
    :param simulation_duration_seconds: Durée de la simulation (s)
    :param time_step: Pas de temps pour la simulation (s)
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
            time_step=time_step
        )

        # Arrête le tracker et récupère les émissions de CO2
        co2_emissions = tracker.stop()  # Récupère les émissions en kg de CO2
        energy_used = tracker._total_energy.kWh

        # Mise à jour de la consommation globale
        update_global_consumption(
            energy_used=energy_used,
            co2_emissions=co2_emissions
        )
        return CableTemperatureConsumptionSimulationResponse(
            final_temperature=res.final_temperature,
            execution_time=res.execution_time,
            temperature_list=res.temperature_list,
            temperature_range_time_list=res.temperature_range_time_list,
            energy_used=energy_used,
            co2_emissions=co2_emissions
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
                time_step: float = 1e-6
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
                if modulo(simulation_duration_minutes, time_step) != 0:
                    res_modulo: Decimal = modulo(simulation_duration_minutes, time_step)
                    raise HTTPException(
                        status_code=400,
                        detail="La durée de simulation (en secondes) doit être un multiple du pas "
                               f"de temps. {simulation_duration_minutes}%{time_step} = "
                               f"{res_modulo}"
                    )

                res: CableTemperatureConsumptionSimulationResponse = (
                    simulate_cable_temperature_with_consumption(
                        ambient_temperature=ambient_temperature,
                        wind_speed=wind_speed,
                        current_intensity=current_intensity,
                        cable_temperature_initial=initial_cable_temperature,
                        simulation_duration_seconds=simulation_duration_minutes,
                        time_step=time_step
                    )
                )

                return CableTemperatureSimulationResponse(
                    final_temperature=res.final_temperature,
                    execution_time=res.execution_time,
                    temperature_list=res.temperature_list,
                    temperature_range_time_list=res.temperature_range_time_list
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
                time_step: float = 1e-6
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
                if modulo(simulation_duration_minutes, time_step) != 0:
                    res_modulo: Decimal = modulo(simulation_duration_minutes, time_step)
                    raise HTTPException(
                        status_code=400,
                        detail="La durée de simulation (en secondes) doit être un multiple du pas "
                               f"de temps. {simulation_duration_minutes}%{time_step} = "
                               f"{res_modulo}"
                    )

                return simulate_cable_temperature_with_consumption(
                    ambient_temperature=ambient_temperature,
                    wind_speed=wind_speed,
                    current_intensity=current_intensity,
                    cable_temperature_initial=initial_cable_temperature,
                    simulation_duration_seconds=simulation_duration_minutes,
                    time_step=time_step
                )
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
    uvicorn.run(app, host="127.0.0.1", port=8000)

####################################################################################################
### Fin du fichier address.py ######################################################################
####################################################################################################
