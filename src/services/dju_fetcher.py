"""Service de récupération des DJU (Degrés Jours Unifiés)."""

import requests
from datetime import date, timedelta
from typing import Optional, List, Sequence
import logging

logger = logging.getLogger(__name__)


class DJUFetcher:
    """
    Service pour récupérer les DJU depuis différentes sources.

    Supporte plusieurs APIs avec fallback automatique.
    """

    # Température de base pour le calcul des DJU en France
    BASE_TEMP = 18.0

    def __init__(
        self,
        api_key: Optional[str] = None,
        station: str = "Le Bourget",
        timeout: int = 10
    ):
        """
        Initialise le fetcher DJU.

        Args:
            api_key: Clé API pour les services nécessitant une authentification
            station: Nom de la station météo
            timeout: Timeout pour les requêtes HTTP (secondes)
        """
        self.api_key = api_key
        self.station = station
        self.timeout = timeout

    def get_dju_period(
        self,
        date_debut: date,
        date_fin: date,
        base_temp: float = BASE_TEMP
    ) -> Optional[float]:
        """
        Récupère les DJU pour une période donnée.

        Args:
            date_debut: Date de début de la période
            date_fin: Date de fin de la période
            base_temp: Température de base pour le calcul (défaut: 18°C)

        Returns:
            DJU total sur la période, ou None si échec
        """
        # Validation
        if date_fin < date_debut:
            logger.error("La date de fin est antérieure à la date de début")
            return None

        # Utiliser Open-Meteo (API gratuite et fiable)
        dju = self._fetch_and_calculate(date_debut, date_fin, base_temp)
        if dju is not None:
            return dju

        logger.error("Impossible de récupérer les DJU depuis Open-Meteo")
        return None

    def _fetch_and_calculate(
        self,
        date_debut: date,
        date_fin: date,
        base_temp: float
    ) -> Optional[float]:
        """
        Récupère les températures et calcule les DJU.

        Args:
            date_debut: Date de début
            date_fin: Date de fin
            base_temp: Température de base

        Returns:
            DJU calculé ou None
        """
        try:
            temperatures = self._fetch_temperatures_open_meteo(date_debut, date_fin)
            if temperatures:
                return self.calculate_dju_from_temperatures(temperatures, base_temp)
            return None
        except Exception as e:
            logger.error(f"Erreur lors du calcul des DJU: {e}")
            return None

    def _fetch_temperatures_open_meteo(
        self,
        date_debut: date,
        date_fin: date
    ) -> Optional[List[float]]:
        """
        Récupère les températures depuis Open-Meteo (API gratuite sans clé).

        Args:
            date_debut: Date de début
            date_fin: Date de fin

        Returns:
            Liste des températures moyennes journalières
        """
        try:
            # Open-Meteo API - gratuite et sans clé
            # Coordonnées Le Bourget: 48.9694, 2.4414
            url = "https://archive-api.open-meteo.com/v1/archive"

            params = {
                'latitude': 48.9694,
                'longitude': 2.4414,
                'start_date': date_debut.isoformat(),
                'end_date': date_fin.isoformat(),
                'daily': 'temperature_2m_mean',
                'timezone': 'Europe/Paris'
            }

            logger.info(f"Récupération des températures depuis Open-Meteo pour {date_debut} à {date_fin}")
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            if 'daily' in data and 'temperature_2m_mean' in data['daily']:
                temperatures = data['daily']['temperature_2m_mean']
                logger.info(f"Températures récupérées: {len(temperatures)} jours")
                return temperatures
            else:
                logger.error("Données de température non trouvées dans la réponse")
                return None

        except requests.RequestException as e:
            logger.error(f"Erreur HTTP lors de la récupération des températures: {e}")
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des températures: {e}")
            return None

    @staticmethod
    def calculate_dju_from_temperatures(
        temperatures: List[float],
        base_temp: float = BASE_TEMP
    ) -> float:
        """
        Calcule les DJU à partir des températures moyennes journalières.

        Formule: DJU = somme des (base_temp - temp_moyenne)
        pour chaque jour où temp_moyenne < base_temp

        Args:
            temperatures: Liste des températures moyennes journalières (°C)
            base_temp: Température de base (défaut: 18°C)

        Returns:
            DJU total calculé
        """
        dju = 0.0
        for temp in temperatures:
            if temp is not None and temp < base_temp:
                dju += (base_temp - temp)

        return round(dju, 1)

    @staticmethod
    def debut_periode(date_dernier_releve: date) -> date:
        """
        Premier jour de la période couverte par un relevé.

        Le jour du relevé précédent est exclu : il est déjà compté dans
        la période de ce relevé précédent.
        """
        return date_dernier_releve + timedelta(days=1)

    def get_dju_par_releves(
        self,
        dates_releves: Sequence[date],
        base_temp: float = BASE_TEMP
    ) -> Optional[List[float]]:
        """
        Calcule les DJU entre relevés successifs avec un seul appel API.

        Pour chaque relevé à partir du deuxième, la période va du lendemain
        du relevé précédent au jour du relevé inclus.

        Args:
            dates_releves: Dates des relevés, triées par ordre croissant
            base_temp: Température de base

        Returns:
            Liste des DJU (un élément par relevé à partir du deuxième), ou None
        """
        if len(dates_releves) < 2:
            return []
        if any(b <= a for a, b in zip(dates_releves, dates_releves[1:])):
            logger.error("Les dates des relevés doivent être strictement croissantes")
            return None

        debut = self.debut_periode(dates_releves[0])
        temperatures = self._fetch_temperatures_open_meteo(debut, dates_releves[-1])
        nb_jours = (dates_releves[-1] - debut).days + 1
        if not temperatures or len(temperatures) != nb_jours:
            logger.error("Températures manquantes pour la période demandée")
            return None

        resultats = []
        for precedent, courant in zip(dates_releves, dates_releves[1:]):
            i_debut = (self.debut_periode(precedent) - debut).days
            i_fin = (courant - debut).days + 1
            resultats.append(
                self.calculate_dju_from_temperatures(temperatures[i_debut:i_fin], base_temp)
            )
        return resultats

    def get_dju_depuis_dernier_releve(
        self,
        date_dernier_releve: date,
        date_nouveau_releve: date,
        base_temp: float = BASE_TEMP
    ) -> Optional[float]:
        """
        Récupère les DJU depuis le dernier relevé.

        Args:
            date_dernier_releve: Date du dernier relevé
            date_nouveau_releve: Date du nouveau relevé
            base_temp: Température de base

        Returns:
            DJU sur la période ou None
        """
        date_debut = self.debut_periode(date_dernier_releve)

        if date_nouveau_releve <= date_dernier_releve:
            logger.error("La date du nouveau relevé doit être postérieure au dernier relevé")
            return None

        return self.get_dju_period(date_debut, date_nouveau_releve, base_temp)
