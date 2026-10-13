"""Modèle pour un relevé de données de chaudière."""

from datetime import date
from typing import Optional

from src.config import get_config


class Releve:
    """Représente un relevé de données de la chaudière à une date donnée."""

    def __init__(
        self,
        date_releve: date,
        index_gaz: float,
        index_calories: float,
        dju: float
    ):
        """
        Initialise un relevé.

        Args:
            date_releve: Date du relevé
            index_gaz: Index du compteur de gaz
            index_calories: Index du compteur de calories
            dju: Degrés Jours Unifiés sur la période
        """
        self.date_releve = date_releve
        self.index_gaz = index_gaz
        self.index_calories = index_calories
        self.dju = dju

        # Relevé précédent de la saison, renseigné par Saison : les indicateurs
        # sont calculés à la volée à partir des données saisies.
        self.releve_precedent: Optional['Releve'] = None

    def calculer_indicateurs(self, releve_precedent: Optional['Releve']) -> None:
        """
        Relie ce relevé au précédent, base du calcul des indicateurs.

        Args:
            releve_precedent: Le relevé précédent (None pour le premier de la saison)
        """
        self.releve_precedent = releve_precedent

    def _a_une_periode(self) -> bool:
        """Vrai si le relevé clôt une période (pas le relevé de référence)."""
        return self.releve_precedent is not None and self.dju != 0

    @property
    def conso_gaz(self) -> Optional[float]:
        """Consommation de gaz sur la période (m³)."""
        if not self._a_une_periode():
            return None
        return self.index_gaz - self.releve_precedent.index_gaz

    @property
    def conso_gaz_par_dju(self) -> Optional[float]:
        """Consommation de gaz par DJU (m³/DJU)."""
        if not self._a_une_periode():
            return None
        return self.conso_gaz / self.dju

    @property
    def calories_produites(self) -> Optional[float]:
        """Calories produites sur la période (MWh)."""
        if not self._a_une_periode():
            return None
        return self.index_calories - self.releve_precedent.index_calories

    @property
    def calories_par_dju(self) -> Optional[float]:
        """Calories produites par DJU (MWh/DJU)."""
        if not self._a_une_periode():
            return None
        return self.calories_produites / self.dju

    @property
    def rendement(self) -> Optional[float]:
        """Rendement de la chaudière sur la période (%)."""
        if not self._a_une_periode():
            return None
        config = get_config()
        energie_gaz_kwh = self.conso_gaz * config.get_coefficient_gaz()
        calories_kwh = self.calories_produites * config.get_kwh_par_unite_calories()
        # Sans calories comptées (compteur absent ou période trop courte pour
        # sa résolution de 1 MWh), le rendement n'est pas mesurable.
        if energie_gaz_kwh > 0 and calories_kwh > 0:
            return (calories_kwh / energie_gaz_kwh) * 100
        return None

    def to_dict(self) -> dict:
        """Convertit le relevé en dictionnaire (données saisies uniquement)."""
        return {
            'date': self.date_releve.isoformat(),
            'index_gaz': self.index_gaz,
            'index_calories': self.index_calories,
            'dju': self.dju
        }

    @staticmethod
    def from_dict(data: dict) -> 'Releve':
        """
        Crée un relevé à partir d'un dictionnaire.

        Les valeurs calculées éventuellement présentes (anciens fichiers) sont
        ignorées : elles sont recalculées à partir des données saisies.
        """
        if isinstance(data['date'], str):
            date_releve = date.fromisoformat(data['date'])
        else:
            date_releve = data['date']

        return Releve(
            date_releve=date_releve,
            index_gaz=float(data['index_gaz']),
            index_calories=float(data['index_calories']),
            dju=float(data['dju'])
        )

    def __repr__(self) -> str:
        return f"Releve(date={self.date_releve}, gaz={self.index_gaz}, calories={self.index_calories}, dju={self.dju})"
