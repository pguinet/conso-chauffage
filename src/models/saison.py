"""Modèle pour une saison de chauffe."""

from datetime import date
from typing import List, Optional
from .releve import Releve


class Saison:
    """Représente une saison de chauffe complète avec ses relevés."""

    def __init__(
        self,
        nom: str,
        date_debut: date,
        date_fin: Optional[date] = None
    ):
        """
        Initialise une saison de chauffe.

        Args:
            nom: Nom de la saison (ex: "2024-2025")
            date_debut: Date de début de la saison
            date_fin: Date de fin de la saison (None si en cours)
        """
        self.nom = nom
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.releves: List[Releve] = []

    def ajouter_releve(self, releve: Releve) -> None:
        """
        Ajoute un relevé à la saison, à sa place chronologique.

        Un relevé oublié peut donc être ajouté après coup : le relevé suivant
        est alors calculé par rapport à lui.

        Args:
            releve: Le relevé à ajouter
        """
        self.releves.append(releve)
        self.releves.sort(key=lambda r: r.date_releve)
        self.recalculer_tous_les_indicateurs()

    def recalculer_tous_les_indicateurs(self) -> None:
        """Relie chaque relevé à son précédent, base du calcul des indicateurs."""
        precedent = None
        for releve in self.releves:
            releve.calculer_indicateurs(precedent)
            precedent = releve

    def get_rendement_moyen(self) -> Optional[float]:
        """
        Calcule le rendement moyen de la saison.

        Moyenne des rendements pondérée par la consommation de gaz, soit
        Σ calories / Σ énergie gaz, sur les seules périodes mesurables :
        une période courte ne pèse pas autant qu'une période longue.

        Returns:
            Le rendement moyen en %, ou None si pas de données
        """
        mesures = [r for r in self.releves if r.rendement is not None and r.conso_gaz]
        conso_totale = sum(r.conso_gaz for r in mesures)
        if conso_totale <= 0:
            return None
        return sum(r.rendement * r.conso_gaz for r in mesures) / conso_totale

    def get_conso_totale_gaz(self) -> float:
        """
        Calcule la consommation totale de gaz de la saison.

        Returns:
            La consommation totale en m³
        """
        if len(self.releves) < 2:
            return 0.0
        return self.releves[-1].index_gaz - self.releves[0].index_gaz

    def get_calories_totales(self) -> float:
        """
        Calcule le total de calories produites durant la saison.

        Returns:
            Le total de calories produites
        """
        if len(self.releves) < 2:
            return 0.0
        return self.releves[-1].index_calories - self.releves[0].index_calories

    def get_dju_total(self) -> float:
        """
        Calcule le total de DJU de la saison.

        Returns:
            Le total de DJU
        """
        return sum(r.dju for r in self.releves)

    def est_en_cours(self) -> bool:
        """Vérifie si la saison est en cours."""
        return self.date_fin is None

    def get_duree_jours(self) -> Optional[int]:
        """
        Calcule la durée de la saison en jours.

        Returns:
            Le nombre de jours de la saison, ou None si la saison est en cours
        """
        if self.date_fin is None:
            return None
        return (self.date_fin - self.date_debut).days

    def to_dict(self) -> dict:
        """Convertit la saison en dictionnaire."""
        return {
            'nom': self.nom,
            'date_debut': self.date_debut.isoformat(),
            'date_fin': self.date_fin.isoformat() if self.date_fin else None,
            'releves': [r.to_dict() for r in self.releves]
        }

    @staticmethod
    def from_dict(data: dict) -> 'Saison':
        """Crée une saison à partir d'un dictionnaire."""
        date_debut = date.fromisoformat(data['date_debut'])
        date_fin = date.fromisoformat(data['date_fin']) if data.get('date_fin') else None

        saison = Saison(
            nom=data['nom'],
            date_debut=date_debut,
            date_fin=date_fin
        )

        # Ajouter les relevés
        for releve_data in data.get('releves', []):
            saison.releves.append(Releve.from_dict(releve_data))
        saison.recalculer_tous_les_indicateurs()

        return saison

    def __repr__(self) -> str:
        statut = "en cours" if self.est_en_cours() else "terminée"
        return f"Saison({self.nom}, {statut}, {len(self.releves)} relevés)"
