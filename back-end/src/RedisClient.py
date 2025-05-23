import os
from typing import Optional, Union, List

import redis


class RedisClient:
    """
    Classe pour gérer la connexion et les opérations de base avec un serveur Redis.

    Attributs :
        host (str): Adresse du serveur Redis.
        port (int): Port du serveur Redis.
        password (str): Mot de passe pour se connecter au serveur Redis.
        client (redis.Redis): Instance du client Redis.
    """

    host: str
    port: int
    client: Optional[redis.Redis]

    def __init__(
            self,
            host: str = "redis",
            port: int = 6379
    ) -> None:
        """
        Initialise le client Redis avec les paramètres donnés ou les variables d'environnement.

        :param host: Adresse du serveur Redis (par défaut depuis l'env ou la valeur passée)
        :param port: Port du serveur Redis (par défaut 6379)
        """
        self.host = os.getenv('REDIS_HOST', host)
        self.port = int(os.getenv('REDIS_PORT', port))
        self.client = None
        self._connect()

    def _connect(self) -> None:
        """
        Établit la connexion avec le serveur Redis.
        Affiche un message de succès ou d'erreur selon le résultat.
        """
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                decode_responses=True
            )
            self.client.ping()  # test de connexion
        except redis.RedisError as e:
            self.client = None
            raise ConnectionError(f"Erreur de connexion à Redis: {e}")

    def set(self, key: str, value: Union[str, int, float, List], ex: Optional[int] = None) -> bool:
        """
        Définit une clé avec une valeur dans Redis, avec expiration optionnelle.

        :param key: Clé à définir
        :param value: Valeur à stocker (str, int, float, ou liste)
        :param ex: Durée d'expiration en secondes (optionnel)
        :return: True si l'opération réussit, sinon False
        :raises ConnectionError: Si le client n'est pas connecté
        """
        if self.client:
            return self.client.set(name=key, value=value, ex=ex)
        raise ConnectionError("Client Redis non connecté.")

    def get(self, key: str) -> Optional[str]:
        """
        Récupère la valeur associée à une clé dans Redis.

        :param key: Clé à rechercher
        :return: Valeur associée à la clé ou None si non trouvée
        :raises ConnectionError: Si le client n'est pas connecté
        """
        if self.client:
            return self.client.get(name=key)
        raise ConnectionError("Client Redis non connecté.")

    def delete(self, key: str) -> int:
        """
        Supprime une clé de Redis.

        :param key: Clé à supprimer
        :return: Nombre de clés supprimées (0 ou 1)
        :raises ConnectionError: Si le client n'est pas connecté
        """
        if self.client:
            return self.client.delete(key)
        raise ConnectionError("Client Redis non connecté.")

    def exists(self, key: str) -> bool:
        """
        Vérifie si une clé existe dans Redis.

        :param key: Clé à vérifier
        :return: True si la clé existe, sinon False
        :raises ConnectionError: Si le client n'est pas connecté
        """
        if self.client:
            return self.client.exists(key) == 1
        raise ConnectionError("Client Redis non connecté.")

    def close(self) -> None:
        """
        Ferme la connexion avec le serveur Redis.
        """
        if self.client:
            self.client.close()
            print("Connexion Redis fermée.")
        else:
            print("Client Redis non connecté.")
