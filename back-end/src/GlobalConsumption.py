from pydantic import BaseModel

from RedisClient import RedisClient


class DefaultValues(BaseModel):
    """
    Classe pour représenter les valeurs par défaut des attributs de GlobalConsumption.

    Attributs :
        energy_used (float): Valeur par défaut de la consommation d'énergie.
        energy_used_list (list[float]): Liste vide par défaut pour l'historique de consommation d'énergie.
        energy_used_unit (str): Unité par défaut de la consommation d'énergie.
        co2_emissions (float): Valeur par défaut des émissions de CO2.
        co2_emissions_list (list[float]): Liste vide par défaut pour l'historique des émissions de CO2.
        co2_emissions_unit (str): Unité par défaut des émissions de CO2.
    """

    energy_used: float = 0.0
    energy_used_list: list[float] = []
    energy_used_unit: str = "kWh"

    co2_emissions: float = 0.0
    co2_emissions_list: list[float] = []
    co2_emissions_unit: str = "kgCO2"

    separator: str = "|"


class GlobalConsumption:
    """
    Classe pour représenter la consommation globale d'énergie et d'émissions de CO2.

    Attributs :
        energy_used (float): Quantité totale d'énergie consommée.
        energy_used_list (list[float]): Historique des consommations d'énergie.
        energy_used_unit (str): Unité de mesure de l'énergie consommée.
        co2_emissions (float): Quantité totale d'émissions de CO2.
        co2_emissions_list (list[float]): Historique des émissions de CO2.
        co2_emissions_unit (str): Unité de mesure des émissions de CO2.
        redis_client (RedisClient): Client Redis pour la persistance des données.
    """

    energy_used: float
    energy_used_list: list[float]
    energy_used_unit: str

    co2_emissions: float
    co2_emissions_list: list[float]
    co2_emissions_unit: str

    redis_client: RedisClient

    defaultValues: DefaultValues = DefaultValues()

    def __init__(self, energy_used_unit: str = "kWh", co2_emissions_unit: str = "kgCO2") -> None:
        """
        Initialise une nouvelle instance de GlobalConsumption.
        :param energy_used_unit:
        :param co2_emissions_unit:
        """
        self.defaultValues.energy_used_unit = energy_used_unit
        self.defaultValues.co2_emissions_unit = co2_emissions_unit

        self.redis_client = RedisClient()
        self._load_from_redis()

    def _load_from_redis(self) -> None:
        """
        Charge les données de consommation d'énergie et d'émissions de CO2 depuis Redis.
        """
        self.energy_used = float(
            self.redis_client.get("energy_used")
            or self.defaultValues.energy_used
        )
        self.co2_emissions = float(
            self.redis_client.get("co2_emissions")
            or self.defaultValues.co2_emissions
        )
        self.energy_used_list = [
            float(x) for x in (
                (self.redis_client.get("energy_used_list") or "")
                .split(self.defaultValues.separator)
            ) if x
        ] or self.defaultValues.energy_used_list
        self.co2_emissions_list = [
            float(x) for x in (
                (self.redis_client.get("co2_emissions_list") or "")
                .split(self.defaultValues.separator)
            ) if x
        ] or self.defaultValues.co2_emissions_list
        self.energy_used_unit = (
                self.redis_client.get("energy_used_unit")
                or self.defaultValues.energy_used_unit
        )
        self.co2_emissions_unit = (
                self.redis_client.get("co2_emissions_unit")
                or self.defaultValues.co2_emissions_unit
        )
        self.energy_used_list = self.energy_used_list[-10:]
        self.co2_emissions_list = self.co2_emissions_list[-10:]

        self._save_to_redis()

    def _save_to_redis(self) -> None:
        """
        Enregistre les données de consommation d'énergie et d'émissions de CO2 dans Redis.
        """
        self.redis_client.set("energy_used", self.energy_used)
        self.redis_client.set("co2_emissions", self.co2_emissions)
        self.redis_client.set(
            "energy_used_list",
            self.defaultValues.separator.join(map(str, self.energy_used_list))
        )
        self.redis_client.set(
            "co2_emissions_list",
            self.defaultValues.separator.join(map(str, self.co2_emissions_list))
        )
        self.redis_client.set("energy_used_unit", self.energy_used_unit)
        self.redis_client.set("co2_emissions_unit", self.co2_emissions_unit)

    def _save(self) -> None:
        """
        Met à jour les données de consommation d'énergie et d'émissions de CO2 dans Redis avec
        les valeurs par locales.
        """
        self._save_to_redis()
        self._load_from_redis()

    def update(self, energy_used: float, co2_emissions: float) -> None:
        """
        Met à jour la consommation d'énergie et les émissions de CO2.
        :param energy_used: Quantité d'énergie consommée.
        :param co2_emissions: Quantité d'émissions de CO2.
        """
        self.energy_used += energy_used
        self.co2_emissions += co2_emissions
        self.energy_used_list.append(energy_used)
        self.co2_emissions_list.append(co2_emissions)
        self._save()

    def update_list(
            self,
            energy_used: float,
            co2_emissions: float,
            energy_used_list: list[float],
            co2_emissions_list: list[float]
    ) -> None:
        """
        Met à jour la consommation d'énergie et les émissions de CO2 avec des listes.
        :param energy_used: Quantité d'énergie consommée.
        :param co2_emissions: Quantité d'émissions de CO2.
        :param energy_used_list: Liste des consommations d'énergie.
        :param co2_emissions_list: Liste des émissions de CO2.
        """
        self.energy_used += energy_used
        self.co2_emissions += co2_emissions
        self.energy_used_list.extend(energy_used_list)
        self.co2_emissions_list.extend(co2_emissions_list)
        self._save()

    def reset(self) -> None:
        """
        Réinitialise les données de consommation d'énergie et d'émissions de CO2.
        """
        self.energy_used = self.defaultValues.energy_used
        self.co2_emissions = self.defaultValues.co2_emissions
        self.energy_used_list = self.defaultValues.energy_used_list
        self.co2_emissions_list = self.defaultValues.co2_emissions_list
        self._save()

    def __dict__(self) -> dict:
        """
        Retourne un dictionnaire représentant l'état de l'objet.
        :return: Dictionnaire représentant l'état de l'objet.
        """
        return {
            "energy_used": self.energy_used,
            "energy_used_list": self.energy_used_list,
            "energy_used_unit": self.energy_used_unit,
            "co2_emissions": self.co2_emissions,
            "co2_emissions_list": self.co2_emissions_list,
            "co2_emissions_unit": self.co2_emissions_unit,
        }

    def __str__(self):
        """
        Retourne une représentation sous forme de chaîne de caractères de l'objet.
        :return: Représentation sous forme de chaîne de caractères de l'objet.
        """
        return str(self.__dict__())
