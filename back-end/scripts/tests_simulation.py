# Vérification de la présence de Cython et du module cython_simulation.py
import os
import time
from typing import Tuple, Optional

import cython_simulator.cython_simulation as cython_simulation
import matplotlib.pyplot as plt
import numpy as np
import psutil
from codecarbon import EmissionsTracker
from numba import jit
from scipy.integrate import odeint
from tabulate import tabulate

# Paramètres de simulation
ta: float = 25  # Température ambiante (°C)
ws: float = 1  # Vitesse du vent (m/s)
i: float = 300  # Intensité (A)
tc_initial: float = 25  # Température initiale (°C)
simulation_time: float = 60  # Durée (s)
dt: float = 1e-1  # Pas de temps (s)
t: np.ndarray = np.arange(0, simulation_time, dt)


def d_tc_dt(tc: float, t: float, ta: float, ws: float, i: float) -> float:
    """
    Calcule la dérivée de la température du câble à l'instant t.

    :param tc: Température actuelle du câble (°C)
    :param t: Temps (s)
    :param ta: Température ambiante (°C)
    :param ws: Vitesse du vent (m/s)
    :param i: Intensité (A)
    :return: Dérivée de la température (°C/s)
    """
    a: float = ((ws ** 2) / 1600) * 0.4 + 0.1
    b: float = ((i ** 1.4) / 73785) * 130
    return -(1 / 60) * a * (tc - ta - b)


def sci(val):
    try:
        return f"{float(val):.10e}"
    except:
        return val


def simulate_python_loop(tc0: float, t: np.ndarray, ta: float, ws: float, i: float) -> np.ndarray:
    """
    Simule l'évolution de la température du câble avec une boucle Python (Euler explicite).

    :param tc0: Température initiale (°C)
    :param t: Vecteur temps (s)
    :param ta: Température ambiante (°C)
    :param ws: Vitesse du vent (m/s)
    :param i: Intensité (A)
    :return: Tableau des températures simulées (°C)
    """
    tc: float = tc0
    tc_list: list[float] = [tc]
    for idx in range(1, len(t)):
        dt_local: float = t[idx] - t[idx - 1]
        tc += d_tc_dt(tc, t[idx - 1], ta, ws, i) * dt_local
        tc_list.append(tc)
    return np.array(tc_list)


def run_1min(method, *args):
    """
    Lance une simulation de 1 minute avec la méthode spécifiée.

    :param method: Fonction de simulation (ex: simulate_python_loop)
    :param args: Arguments pour la fonction de simulation
    :return: Température finale après 1 minute
    """
    t_1min = np.arange(0, 60, dt)
    return method(*args, t_1min, ta, ws, i)


def run_30x1min(method, *args):
    """
    Effectue 30 simulations consécutives de 1 minute chacune.

    :param method: Fonction de simulation
    :param args: Arguments pour la fonction de simulation
    :return: Température finale après 30 minutes
    """
    tc = tc_initial
    for _ in range(30):
        tc_list = method(tc, np.arange(0, 60, dt), ta, ws, i)
        tc = tc_list[-1]
    return tc


def run_1x30min(method, *args):
    """
    Effectue une simulation unique de 30 minutes.

    :param method: Fonction de simulation
    :param args: Arguments pour la fonction de simulation
    :return: Température finale après 30 minutes
    """
    t_30min = np.arange(0, 1800, dt)
    tc_list = method(*args, t_30min, ta, ws, i)
    return tc_list[-1]


def plot_results(tc_py: np.ndarray, tc_odeint: np.ndarray, tc_numba: np.ndarray,
                 tc_cython: np.ndarray) -> None:
    """
    Affiche les résultats de la simulation sous forme de graphique.

    :param tc_py: np.ndarray - Températures simulées avec la boucle Python
    :param tc_odeint: np.ndarray - Températures simulées avec odeint
    :param tc_numba: np.ndarray - Températures simulées avec Numba
    :param tc_cython: np.ndarray - Températures simulées avec Cython
    """
    plt.figure(figsize=(10, 6))
    plt.plot(tc_py, label='Python Loop', color='blue')
    plt.plot(tc_odeint, label='odeint', color='orange')
    plt.plot(tc_numba, label='Numba', color='green')
    plt.plot(tc_cython, label='Cython', color='red')
    plt.xlabel('Time (s)')
    plt.ylabel('Temperature (°C)')
    plt.title('Cable Temperature Simulation')
    plt.legend()
    plt.grid()
    plt.show()


def main_simulate_python_loop() -> Tuple[np.ndarray, float, Optional[float], float, str]:
    """
    Exécute la simulation de la température du câble avec une boucle Python et mesure les performances.
    :return: Un tuple contenant :
            - tc_py : np.ndarray - Températures simulées
            - temps_code_py : float - Temps d'exécution (minutes)
            - energy_py : Optional[float] - Énergie consommée (kgCO2)
            - ram_py : float - Mémoire utilisée (MB)
            - cpu_py : str - Modèle du processeur utilisé
    """
    tracker: EmissionsTracker = EmissionsTracker(measure_power_secs=1, save_to_file=False,
                                                 log_level="warning")
    tracker.start()
    start: float = time.time()
    tc_py: np.ndarray = simulate_python_loop(tc_initial, t, ta, ws, i)
    end: float = time.time()
    temps_code_py: float = (end - start) * 60  # en secondes -> minutes
    energy_py: Optional[float] = tracker.stop()
    ram_py: float = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2
    cpu_py: str = tracker._conf["cpu_model"]  # Nom du processeur
    print(f"Boucle Python : {cpu_py}, énergie {energy_py:.6f} kgCO2, RAM {ram_py:.2f} MB")

    return tc_py, temps_code_py, energy_py, ram_py, cpu_py


def main_simulate_odeint() -> Tuple[np.ndarray, float, Optional[float], float, str]:
    """
    Exécute la simulation de la température du câble avec odeint et mesure les performances.
    :return: Un tuple contenant :
            - tc_py : np.ndarray - Températures simulées
            - temps_code_py : float - Temps d'exécution (minutes)
            - energy_py : Optional[float] - Énergie consommée (kgCO2)
            - ram_py : float - Mémoire utilisée (MB)
            - cpu_py : str - Modèle du processeur utilisé
    """

    tracker = EmissionsTracker(measure_power_secs=1, save_to_file=False, log_level="warning")
    tracker.start()
    start = time.time()
    tc_odeint = odeint(d_tc_dt, tc_initial, t, args=(ta, ws, i), hmax=dt).flatten()
    end = time.time()
    energy_odeint = tracker.stop()
    temps_code_odeint = (end - start) * 60  # en secondes -> minutes
    ram_odeint = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2
    cpu_odeint = tracker._conf["cpu_model"]
    print(f"odeint : {cpu_odeint}, énergie {energy_odeint:.6f} kgCO2, RAM {ram_odeint:.2f} MB")

    return tc_odeint, temps_code_odeint, energy_odeint, ram_odeint, cpu_odeint


def main_simulate_numba() -> Tuple[np.ndarray, float, Optional[float], float, str]:
    """
    Exécute la simulation de la température du câble avec Numba et mesure les performances.
    :return: Un tuple contenant :
            - tc_py : np.ndarray - Températures simulées
            - temps_code_py : float - Temps d'exécution (minutes)
            - energy_py : Optional[float] - Énergie consommée (kgCO2)
            - ram_py : float - Mémoire utilisée (MB)
            - cpu_py : str - Modèle du processeur utilisé
    """

    @jit(nopython=True)
    def d_tc_dt_numba(tc, t, ta, ws, i):
        """
        Version Numba de l'équation différentielle pour accélération JIT.
        """
        a = ((ws ** 2) / 1600) * 0.4 + 0.1
        b = ((i ** 1.4) / 73785) * 130
        return -(1 / 60) * a * (tc - ta - b)

    @jit(nopython=True)
    def simulate_numba(tc0, t, ta, ws, i):
        """
        Simule l'évolution de la température du câble avec Numba (Euler explicite compilé).
        """
        tc = tc0
        tc_list = np.empty(len(t))
        tc_list[0] = tc
        for idx in range(1, len(t)):
            dt_local = t[idx] - t[idx - 1]
            tc += d_tc_dt_numba(tc, t[idx - 1], ta, ws, i) * dt_local
            tc_list[idx] = tc
        return tc_list

    tracker = EmissionsTracker(measure_power_secs=1, save_to_file=False, log_level="warning")
    tracker.start()
    start = time.time()
    tc_numba = simulate_numba(tc_initial, t, ta, ws, i)
    end = time.time()
    energy_numba = tracker.stop()
    temps_code_numba = (end - start) * 60  # en secondes -> minutes
    ram_numba = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2
    cpu_numba = tracker._conf["cpu_model"]
    print(f"Numba : {cpu_numba}, énergie {energy_numba:.6f} kgCO2, RAM {ram_numba:.2f} MB")

    return tc_numba, temps_code_numba, energy_numba, ram_numba, cpu_numba


def main_simulate_cython() -> Tuple[np.ndarray, float, Optional[float], float, str]:
    """
    Exécute la simulation de la température du câble avec Cython et mesure les performances.
    :return: Un tuple contenant :
            - tc_py : np.ndarray - Températures simulées
            - temps_code_py : float - Temps d'exécution (minutes)
            - energy_py : Optional[float] - Énergie consommée (kgCO2)
            - ram_py : float - Mémoire utilisée (MB)
            - cpu_py : str - Modèle du processeur utilisé
    """
    tracker = EmissionsTracker(measure_power_secs=1, save_to_file=False, log_level="warning")
    tracker.start()
    start = time.time()
    tc_cython = cython_simulation.simulate_cython(tc_initial, t, ta, ws, i)
    end = time.time()
    energy_cython = tracker.stop()
    temps_code_cython = (end - start) * 60
    ram_cython = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2
    cpu_cython = tracker._conf["cpu_model"]
    print(f"Cython : {cpu_cython}, énergie {energy_cython:.6f} kgCO2, RAM {ram_cython:.2f} MB")
    return tc_cython, temps_code_cython, energy_cython, ram_cython, cpu_cython


def main_simulate_run_30x1min() -> Tuple[np.ndarray, float, Optional[float], float, str]:
    """
    Exécute la simulation de la température du câble avec une boucle Python sur 30 minutes et mesure les performances.
    :return: Un tuple contenant :
            - tc_py : np.ndarray - Températures simulées
            - temps_code_py : float - Temps d'exécution (minutes)
            - energy_py : Optional[float] - Énergie consommée (kgCO2)
            - ram_py : float - Mémoire utilisée (MB)
            - cpu_py : str - Modèle du processeur utilisé
    """
    tracker = EmissionsTracker(measure_power_secs=1, save_to_file=False, log_level="warning")
    tracker.start()
    start = time.time()
    tc_30x1min_py = run_30x1min(simulate_python_loop, tc_initial)
    end = time.time()
    energy_30x1min_py = tracker.stop()
    cpu_30x1min_py = tracker._conf["cpu_model"]
    ram_30x1min_py = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2
    time_30x1min_py = end - start

    print(
        f"Boucle Python 30x1min : {time_30x1min_py:.3f}s, énergie {energy_30x1min_py:.6f} kgCO2, RAM {ram_30x1min_py:.2f} MB, CPU {cpu_30x1min_py}")

    return tc_30x1min_py, time_30x1min_py * 60, energy_30x1min_py, ram_30x1min_py, cpu_30x1min_py


def main_simulate_run_1x30min() -> Tuple[np.ndarray, float, Optional[float], float, str]:
    """
    Exécute la simulation de la température du câble avec une boucle Python sur 30 minutes et mesure les performances.
    :return: Un tuple contenant :
            - tc_py : np.ndarray - Températures simulées
            - temps_code_py : float - Temps d'exécution (minutes)
            - energy_py : Optional[float] - Énergie consommée (kgCO2)
            - ram_py : float - Mémoire utilisée (MB)
            - cpu_py : str - Modèle du processeur utilisé
    """
    tracker = EmissionsTracker(measure_power_secs=1, save_to_file=False, log_level="warning")
    tracker.start()
    start = time.time()
    tc_1x30min_py = run_1x30min(simulate_python_loop, tc_initial)
    end = time.time()
    energy_1x30min_py = tracker.stop()
    cpu_1x30min_py = tracker._conf["cpu_model"]
    ram_1x30min_py = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2
    time_1x30min_py = end - start

    print(
        f"Boucle Python 1x30min : {time_1x30min_py:.3f}s, énergie {energy_1x30min_py:.6f} kgCO2, RAM {ram_1x30min_py:.2f} MB, CPU {cpu_1x30min_py}")

    return tc_1x30min_py, time_1x30min_py * 60, energy_1x30min_py, ram_1x30min_py, cpu_1x30min_py


def main() -> None:
    """
    Fonction principale pour exécuter la simulation et afficher les résultats.
    """
    # Exécution des simulations
    tc_py, temps_code_py, energy_py, ram_py, cpu_py = main_simulate_python_loop()
    tc_odeint, temps_code_odeint, energy_odeint, ram_odeint, cpu_odeint = main_simulate_odeint()
    tc_numba, temps_code_numba, energy_numba, ram_numba, cpu_numba = main_simulate_numba()
    tc_cython, temps_code_cython, energy_cython, ram_cython, cpu_cython = main_simulate_cython()
    # Affichage le graphe de la température
    plot_results(tc_py, tc_odeint, tc_numba, tc_cython)
    # Exécution des simulations de 30x1min et 1x30min
    tc_30x1min_py, time_30x1min_py, energy_30x1min_py, ram_30x1min_py, cpu_30x1min_py = main_simulate_run_30x1min()
    tc_1x30min_py, time_1x30min_py, energy_1x30min_py, ram_1x30min_py, cpu_1x30min_py = main_simulate_run_1x30min()
    # Informations de Complexité
    print("Complexité estimée :")
    print("- Boucle Python : O(N) (itération simple sur le temps)")
    print("- odeint : O(N) (méthode optimisée, dépend du solveur)")
    print("- Numba : O(N) (identique à la boucle Python, mais compilée)")
    print("- Cython : O(N) (similaire à Numba, mais avec overhead de compilation)")
    print("- 30x 1min : O(30N) (30 itérations de 1 minute)")
    print("- 1x 30min : O(N) (itération unique sur 30 minutes)")
    # Création du tableau final
    table_final = [
        [
            "Boucle Python",
            cpu_py,
            sci(ram_py),
            sci(energy_py),
            sci(temps_code_py),
            "*"
        ],
        [
            "Scipy odeint",
            cpu_odeint,
            sci(ram_odeint),
            sci(energy_odeint),
            sci(temps_code_odeint),
            "**"
        ],
        [
            "Jit numba",
            cpu_numba,
            sci(ram_numba),
            sci(energy_numba),
            sci(temps_code_numba),
            "**"
        ],
        [
            "Cython",
            cpu_cython,
            sci(ram_cython),
            sci(energy_cython),
            sci(temps_code_cython),
            "***"
        ],
        [
            "30x 1min",
            cpu_30x1min_py,
            sci(ram_30x1min_py),
            sci(energy_30x1min_py),
            sci(time_30x1min_py),
            "*"
        ],
        [
            "1x30min",
            cpu_1x30min_py,
            sci(ram_1x30min_py),
            sci(energy_1x30min_py),
            sci(time_1x30min_py),
            "*"
        ]
    ]

    headers_final = [
        "Testcase",
        "CPU",
        "RAM (MB)",
        "Énergie (kgCO2)",
        "Temps de code (min)",
        "Complexité estimée (* = simple, ***** = très complexe)"
    ]
    # Affichage du tableau final
    print(tabulate(table_final, headers=headers_final, tablefmt="github"))


if __name__ == "__main__":
    main()
