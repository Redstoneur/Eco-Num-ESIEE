"""
Script pour tester l'énergie consommée par l'API backend selon la charge utilisateur.
Simule des appels concurrents à l'API et affiche un tableau récapitulatif.
"""

import threading
import requests
from codecarbon import EmissionsTracker
from tabulate import tabulate

API_URL = "http://localhost:8000/cable_temperature_consumption_simulation"

payload = {
    "ambient_temperature": 25,
    "wind_speed": 2,
    "current_intensity": 300,
    "initial_cable_temperature": 25,
    "simulation_duration": 60,
    "time_step": 1e-1
}

def sci(val):
    """Formatte une valeur en notation scientifique."""
    try:
        return f"{float(val):.10e}"
    except Exception:
        return val

def check_server():
    """Vérifie que le serveur FastAPI est lancé."""
    try:
        r = requests.get("http://localhost:8000/health", timeout=3)
        if r.status_code != 200:
            print("ERREUR : Le serveur API ne répond pas correctement.")
            exit(1)
    except Exception:
        print("ERREUR : Le serveur FastAPI n'est pas lancé ou inaccessible.")
        print("Démarrez le backend avant d'exécuter ce script.")
        exit(1)

def send_post_request() -> float:
    """
    Envoie une requête POST à l'API pour simuler la consommation d'énergie.
    :return: L'énergie consommée en kgCO2.
    """
    res = requests.post(API_URL, params=payload)
    if res.status_code != 200:
        raise Exception(f"Erreur lors de l'appel à l'API : {res.status_code} - {res.text}")
    data = res.json()
    if "co2_emissions" not in data:
        raise Exception("La réponse de l'API ne contient pas 'co2_emissions'.")
    return data["co2_emissions"]

def run_users_test(nb_users: int, use_cache: bool = False) -> float:
    """
    Exécute un test avec un nombre donné d'utilisateurs simulés.
    :param nb_users: Nombre d'utilisateurs à simuler.
    :param use_cache: Indique si le cache doit être utilisé (optionnel).
    :return: L'énergie totale consommée en kgCO2.
    """
    payload["use_cache"] = use_cache  # Ajouter un paramètre pour le cache si nécessaire

    results = []
    threads = []

    def thread_func():
        try:
            val = send_post_request()
            results.append(val)
        except Exception as e:
            print(f"Erreur dans un thread : {e}")

    tracker = EmissionsTracker(measure_power_secs=1, save_to_file=False, log_level="warning")
    tracker.start()

    for _ in range(nb_users):
        thread = threading.Thread(target=thread_func)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    co2_energy = sum(results)
    co2_energy += tracker.stop()
    return co2_energy

if __name__ == "__main__":
    print("# Test énergie backend API\n")
    print("Vérification du serveur...")
    check_server()

    print("Test avec 10 utilisateurs/minute...")
    co2_energy_10 = run_users_test(10)
    print(f"10 utilisateurs/minute : {sci(co2_energy_10)} kgCO2")

    print("Test avec 100 utilisateurs/minute...")
    co2_energy_100 = run_users_test(100)
    print(f"100 utilisateurs/minute : {sci(co2_energy_100)} kgCO2")

    print("Test avec 1000 utilisateurs/minute...")
    co2_energy_1000 = run_users_test(1000)
    print(f"1000 utilisateurs/minute : {sci(co2_energy_1000)} kgCO2")

    print("Test avec 1000 utilisateurs/minute + cache...")
    co2_energy_1000_cache = run_users_test(1000, use_cache=True)
    print(f"1000 utilisateurs/minute + cache : {sci(co2_energy_1000_cache)} kgCO2")

    header = ["Testcase", "Énergie (kgCO2)"]
    data = [
        ["10 utilisateurs/minute", f"{sci(co2_energy_10)}"],
        ["100 utilisateurs/minute", f"{sci(co2_energy_100)}"],
        ["1000 utilisateurs/minute", f"{sci(co2_energy_1000)}"],
        ["1000 utilisateurs/minute + cache", f"{sci(co2_energy_1000_cache)}"]
    ]
    print("\nRésultats :")
    print(tabulate(data, headers=header, tablefmt="github"))
