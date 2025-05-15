import time
from typing import List, Tuple

import numpy as np
import plotly.graph_objects as go
from scipy.integrate import odeint

# --- Constantes ---
R_cable: float = 0.0001  # Ohms (résistance du câble)
CO2_factor: int = 82  # g CO2 / kWh


# --- Équation différentielle ---
def d_tc_dt(tc: float, t: float, ta: float, ws: float, i: float) -> float:
    """
    Calcule la dérivée de la température du câble à un instant donné.
    :param tc: Température actuelle du câble (°C)
    :param t: Temps (s)
    :param ta: Température ambiante (°C)
    :param ws: Vitesse du vent (m/s)
    :param i: Intensité (A)
    :return: Dérivée de la température du câble (°C/s)
    """
    a: float = ((ws ** 2) / 1600) * 0.4 + 0.1
    b: float = ((i ** 1.4) / 73785) * 130
    return -(1 / 60) * a * (tc - ta - b)


# --- Fonction de simulation sur N minutes ---
def simulate_cable_temp(
        ta: float,
        ws: float,
        i: float,
        tc_initial: float,
        simulation_time_min: int = 1,
        microsecond_step: float = 1e-6
) -> Tuple[float, float, float, float]:
    """
    Simule la température du câble sur une période donnée.
    :param ta: Température ambiante (°C)
    :param ws: Vitesse du vent (m/s)
    :param i: Intensité (A)
    :param tc_initial: Température initiale du câble (°C)
    :param simulation_time_min: Durée de la simulation (minutes)
    :param microsecond_step: Pas de temps pour la simulation (s)
    :return: Tuple contenant la température finale du câble, l'énergie utilisée (Wh), les émissions
             de CO2 (g) et le temps d'exécution (s).
    """
    total_time_s: float = simulation_time_min * 60
    t: np.ndarray = np.arange(0, total_time_s, microsecond_step)

    start_time: float = time.time()
    tc_sol: np.ndarray = odeint(d_tc_dt, tc_initial, t, args=(ta, ws, i), hmax=microsecond_step)
    end_time: float = time.time()

    final_tc: float = float(tc_sol[-1])
    energy_wh: float = (R_cable * i ** 2 * total_time_s) / 3600
    co2_emitted: float = energy_wh * CO2_factor

    return final_tc, energy_wh, co2_emitted, end_time - start_time


# --- Simulation répétée 30 fois pour faire une courbe 30 minutes ---
def run_x_min_simulation(
        minutes: int = 30, microsecond_step: float = 1e-6
) -> Tuple[List[float], List[float], List[float], List[float]]:
    """
    Simule la température du câble sur 30 minutes, en répétant la simulation chaque minute.
    :param minutes: Nombre de minutes à simuler (par défaut 30).
    :param microsecond_step: Pas de temps pour la simulation (s)
    :return: Liste des températures, énergies et émissions de CO2 pour chaque minute.
    """
    ta: float = 25  # Température ambiante (°C)
    ws: float = 1  # Vitesse du vent (m/s)
    i: float = 300  # Intensité (A)
    tc_initial: float = 25  # Température initiale du câble

    tc_list: List[float] = []
    energy_list: List[float] = []
    co2_list: List[float] = []
    exec_times: List[float] = []

    tc_current: float = tc_initial

    for minute in range(minutes):
        minute: int  # annotation explicite
        tc: float
        e: float
        co2: float
        exec_time: float
        tc, e, co2, exec_time = simulate_cable_temp(
            ta, ws, i, tc_current,
            simulation_time_min=1,
            microsecond_step=microsecond_step
        )
        tc_list.append(tc)
        energy_list.append(e)
        co2_list.append(co2)
        exec_times.append(exec_time)
        tc_current = tc  # Utiliser la temp finale comme nouvelle initiale

        print(
            f"Minute {minute + 1}: Tc = {tc:.2f}°C, Énergie = {e:.4f} Wh, CO2 = {co2:.2f} g, "
            f"Temps = {exec_time:.2f} s"
        )

    return tc_list, energy_list, co2_list, exec_times


# --- Plotting avec Plotly ---
def plot_results(
        tc_list: List[float],
        energy_list: List[float],
        co2_list: List[float],
        minutes: int = 30
) -> None:
    """
    Affiche les résultats de la simulation sous forme de graphique interactif.
    :param tc_list: liste des températures du câble
    :param energy_list: liste des énergies utilisées
    :param co2_list: liste des émissions de CO2
    :param minutes: Nombre de minutes simulées
    """
    fig: go.Figure = go.Figure()
    fig.add_trace(go.Scatter(y=tc_list, mode='lines+markers', name='Température câble (°C)'))
    fig.add_trace(go.Scatter(y=np.cumsum(energy_list), mode='lines', name='Énergie cumulée (Wh)'))
    fig.add_trace(go.Scatter(y=np.cumsum(co2_list), mode='lines', name='CO2 cumulé (g)'))

    fig.update_layout(
        title=f"Simulation température câble sur {minutes} minutes",
        xaxis_title="Minute",
        yaxis_title="Valeur",
        template="plotly_dark"
    )

    fig.show()


# --- Exécution principale ---
if __name__ == "__main__":
    minutes: int = 30
    microsecond_step: float = 1e-6
    tc_list, energy_list, co2_list, exec_times = run_x_min_simulation(minutes, microsecond_step)
    plot_results(tc_list, energy_list, co2_list, minutes)
