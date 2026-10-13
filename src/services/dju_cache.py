"""Système de cache pour les DJU afin de limiter les appels API."""

import json
from pathlib import Path
from datetime import date, datetime
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class DJUCache:
    """
    Cache local pour stocker les DJU récupérés et éviter les appels API répétés.

    Le cache est persisté dans un fichier JSON.
    """

    def __init__(self, cache_file: Optional[Path] = None):
        """
        Initialise le cache DJU.

        Args:
            cache_file: Chemin du fichier de cache (défaut: data/dju_cache.json)
        """
        if cache_file is None:
            cache_file = Path(__file__).parent.parent.parent / 'data' / 'dju_cache.json'

        self.cache_file = Path(cache_file)
        self.cache: Dict[str, dict] = self._load_cache()

    def _load_cache(self) -> Dict[str, dict]:
        """
        Charge le cache depuis le fichier.

        Returns:
            Dictionnaire du cache
        """
        if not self.cache_file.exists():
            logger.info("Fichier de cache DJU non trouvé, création d'un nouveau cache")
            return {}

        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                logger.info(f"Cache DJU chargé: {len(cache_data)} entrées")
                return cache_data
        except json.JSONDecodeError as e:
            logger.error(f"Erreur lors du chargement du cache: {e}")
            return {}
        except Exception as e:
            logger.error(f"Erreur inattendue lors du chargement du cache: {e}")
            return {}

    def _save_cache(self) -> None:
        """Sauvegarde le cache dans le fichier."""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)

            logger.info(f"Cache DJU sauvegardé: {len(self.cache)} entrées")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du cache: {e}")

    def _make_key(self, date_debut: date, date_fin: date, base_temp: float) -> str:
        """
        Crée une clé unique pour le cache.

        Args:
            date_debut: Date de début
            date_fin: Date de fin
            base_temp: Température de base

        Returns:
            Clé de cache
        """
        return f"{date_debut.isoformat()}_{date_fin.isoformat()}_{base_temp}"

    def get(
        self,
        date_debut: date,
        date_fin: date,
        base_temp: float = 18.0
    ) -> Optional[float]:
        """
        Récupère les DJU depuis le cache.

        Args:
            date_debut: Date de début de la période
            date_fin: Date de fin de la période
            base_temp: Température de base

        Returns:
            DJU si trouvé en cache, sinon None
        """
        key = self._make_key(date_debut, date_fin, base_temp)

        if key in self.cache:
            entry = self.cache[key]
            dju = entry.get('dju')
            cached_date = entry.get('cached_at')

            logger.info(f"DJU trouvé en cache: {dju} (mis en cache le {cached_date})")
            return dju

        logger.debug(f"DJU non trouvé en cache pour la période {date_debut} à {date_fin}")
        return None

    def set(
        self,
        date_debut: date,
        date_fin: date,
        dju: float,
        base_temp: float = 18.0
    ) -> None:
        """
        Stocke les DJU dans le cache.

        Args:
            date_debut: Date de début de la période
            date_fin: Date de fin de la période
            dju: Valeur DJU à cacher
            base_temp: Température de base
        """
        key = self._make_key(date_debut, date_fin, base_temp)

        self.cache[key] = {
            'date_debut': date_debut.isoformat(),
            'date_fin': date_fin.isoformat(),
            'base_temp': base_temp,
            'dju': dju,
            'cached_at': datetime.now().isoformat()
        }

        self._save_cache()
        logger.info(f"DJU ajouté au cache: {dju} pour {date_debut} à {date_fin}")

    def clear(self) -> None:
        """Vide complètement le cache."""
        self.cache = {}
        self._save_cache()
        logger.info("Cache DJU vidé")

    def remove(
        self,
        date_debut: date,
        date_fin: date,
        base_temp: float = 18.0
    ) -> bool:
        """
        Supprime une entrée spécifique du cache.

        Args:
            date_debut: Date de début
            date_fin: Date de fin
            base_temp: Température de base

        Returns:
            True si l'entrée a été supprimée, False sinon
        """
        key = self._make_key(date_debut, date_fin, base_temp)

        if key in self.cache:
            del self.cache[key]
            self._save_cache()
            logger.info(f"Entrée cache supprimée pour {date_debut} à {date_fin}")
            return True

        return False

    def get_cache_stats(self) -> dict:
        """
        Retourne des statistiques sur le cache.

        Returns:
            Dictionnaire avec les statistiques
        """
        if not self.cache:
            return {
                'total_entries': 0,
                'cache_file': str(self.cache_file),
                'cache_size_bytes': 0
            }

        cache_size = 0
        if self.cache_file.exists():
            cache_size = self.cache_file.stat().st_size

        return {
            'total_entries': len(self.cache),
            'cache_file': str(self.cache_file),
            'cache_size_bytes': cache_size,
            'cache_size_kb': round(cache_size / 1024, 2)
        }

    def get_or_fetch(
        self,
        date_debut: date,
        date_fin: date,
        fetch_function,
        base_temp: float = 18.0
    ) -> Optional[float]:
        """
        Récupère depuis le cache ou fait un fetch si nécessaire.

        Args:
            date_debut: Date de début
            date_fin: Date de fin
            fetch_function: Fonction à appeler si pas en cache (doit retourner float ou None)
            base_temp: Température de base

        Returns:
            DJU ou None
        """
        # Essayer de récupérer depuis le cache
        dju = self.get(date_debut, date_fin, base_temp)

        if dju is not None:
            return dju

        # Pas en cache, faire le fetch
        logger.info("DJU non en cache, appel de la fonction de fetch")
        dju = fetch_function(date_debut, date_fin, base_temp)

        # Mettre en cache si succès
        if dju is not None:
            self.set(date_debut, date_fin, dju, base_temp)

        return dju
