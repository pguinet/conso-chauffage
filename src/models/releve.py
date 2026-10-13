"""Modèle pour un relevé de données de chaudière."""

from datetime import date
from typing import Optional


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

        # Valeurs calculées (initialisées à None)
        self.conso_gaz: Optional[float] = None
        self.conso_gaz_par_dju: Optional[float] = None
        self.calories_produites: Optional[float] = None
        self.calories_par_dju: Optional[float] = None
        self.rendement: Optional[float] = None

    def calculer_indicateurs(self, releve_precedent: 'Releve') -> None:
        """
        Calcule les indicateurs par rapport au relevé précédent.

        Args:
            releve_precedent: Le relevé précédent pour calculer les différences
        """
        if self.dju == 0:
            # Pas de calcul si DJU = 0 (premier relevé de référence)
            return

        # Consommation de gaz
        self.conso_gaz = self.index_gaz - releve_precedent.index_gaz
        self.conso_gaz_par_dju = self.conso_gaz / self.dju

        # Calories produites
        self.calories_produites = self.index_calories - releve_precedent.index_calories
        self.calories_par_dju = self.calories_produites / self.dju

        # Rendement (en %)
        # 1 m³ de gaz = 10 kWh (approximation)
        # 1 unité compteur calories = 1 MWh = 1000 kWh
        energie_gaz_kwh = self.conso_gaz * 10
        calories_kwh = self.calories_produites * 1000  # Conversion MWh -> kWh
        # Sans calories comptées (compteur absent ou période trop courte pour
        # sa résolution de 1 MWh), le rendement n'est pas mesurable.
        if energie_gaz_kwh > 0 and calories_kwh > 0:
            self.rendement = (calories_kwh / energie_gaz_kwh) * 100
        else:
            self.rendement = None

    def to_dict(self) -> dict:
        """Convertit le relevé en dictionnaire."""
        return {
            'date': self.date_releve.isoformat(),
            'index_gaz': self.index_gaz,
            'index_calories': self.index_calories,
            'dju': self.dju,
            'conso_gaz': self.conso_gaz,
            'conso_gaz_par_dju': self.conso_gaz_par_dju,
            'calories_produites': self.calories_produites,
            'calories_par_dju': self.calories_par_dju,
            'rendement': self.rendement
        }

    @staticmethod
    def from_dict(data: dict) -> 'Releve':
        """Crée un relevé à partir d'un dictionnaire."""
        if isinstance(data['date'], str):
            date_releve = date.fromisoformat(data['date'])
        else:
            date_releve = data['date']

        releve = Releve(
            date_releve=date_releve,
            index_gaz=float(data['index_gaz']),
            index_calories=float(data['index_calories']),
            dju=float(data['dju'])
        )

        # Restaurer les valeurs calculées si elles existent
        releve.conso_gaz = data.get('conso_gaz')
        releve.conso_gaz_par_dju = data.get('conso_gaz_par_dju')
        releve.calories_produites = data.get('calories_produites')
        releve.calories_par_dju = data.get('calories_par_dju')
        releve.rendement = data.get('rendement')

        return releve

    def __repr__(self) -> str:
        return f"Releve(date={self.date_releve}, gaz={self.index_gaz}, calories={self.index_calories}, dju={self.dju})"
