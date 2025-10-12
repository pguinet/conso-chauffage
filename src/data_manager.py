"""Module de gestion des données (chargement et sauvegarde)."""

import yaml
from pathlib import Path
from typing import List
from datetime import date
from src.models import Saison, Releve


class DataManager:
    """Gestionnaire de données pour les saisons de chauffe."""

    def __init__(self, data_file: Path = None):
        """
        Initialise le gestionnaire de données.

        Args:
            data_file: Chemin du fichier de données YAML
        """
        if data_file is None:
            data_file = Path(__file__).parent.parent / 'data' / 'saisons.yaml'

        self.data_file = Path(data_file)
        self.saisons: List[Saison] = []

    def charger_donnees(self) -> List[Saison]:
        """
        Charge les données depuis le fichier YAML.

        Returns:
            Liste des saisons chargées
        """
        if not self.data_file.exists():
            self.saisons = []
            return self.saisons

        with open(self.data_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if not data or 'saisons' not in data:
            self.saisons = []
            return self.saisons

        self.saisons = []
        for saison_data in data['saisons']:
            saison = Saison.from_dict(saison_data)
            self.saisons.append(saison)

        return self.saisons

    def sauvegarder_donnees(self) -> None:
        """Sauvegarde les données dans le fichier YAML."""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'saisons': [saison.to_dict() for saison in self.saisons]
        }

        with open(self.data_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    def ajouter_saison(self, saison: Saison) -> None:
        """
        Ajoute une nouvelle saison.

        Args:
            saison: La saison à ajouter
        """
        self.saisons.append(saison)
        self.sauvegarder_donnees()

    def get_saison(self, nom: str) -> Saison:
        """
        Récupère une saison par son nom.

        Args:
            nom: Le nom de la saison

        Returns:
            La saison trouvée, ou None
        """
        for saison in self.saisons:
            if saison.nom == nom:
                return saison
        return None

    def get_saison_en_cours(self) -> Saison:
        """
        Récupère la saison en cours (sans date de fin).

        Returns:
            La saison en cours, ou None
        """
        for saison in self.saisons:
            if saison.est_en_cours():
                return saison
        return None

    def supprimer_saison(self, nom: str) -> bool:
        """
        Supprime une saison.

        Args:
            nom: Le nom de la saison à supprimer

        Returns:
            True si la saison a été supprimée, False sinon
        """
        for i, saison in enumerate(self.saisons):
            if saison.nom == nom:
                self.saisons.pop(i)
                self.sauvegarder_donnees()
                return True
        return False

    def ajouter_releve_a_saison(self, nom_saison: str, releve: Releve) -> bool:
        """
        Ajoute un relevé à une saison existante.

        Args:
            nom_saison: Le nom de la saison
            releve: Le relevé à ajouter

        Returns:
            True si le relevé a été ajouté, False sinon
        """
        saison = self.get_saison(nom_saison)
        if saison:
            saison.ajouter_releve(releve)
            self.sauvegarder_donnees()
            return True
        return False

    def get_toutes_saisons(self) -> List[Saison]:
        """
        Retourne toutes les saisons.

        Returns:
            Liste de toutes les saisons
        """
        return self.saisons

    def creer_fichier_exemple(self) -> None:
        """Crée un fichier de données d'exemple."""
        # Créer une saison d'exemple
        saison_2024 = Saison(
            nom="2024-2025",
            date_debut=date(2024, 9, 15),
            date_fin=None
        )

        # Ajouter des relevés d'exemple
        releve1 = Releve(
            date_releve=date(2024, 9, 15),
            index_gaz=125430.0,
            index_calories=456780.0,
            dju=0.0
        )

        releve2 = Releve(
            date_releve=date(2024, 10, 20),
            index_gaz=128950.0,
            index_calories=462340.0,
            dju=145.0
        )

        releve3 = Releve(
            date_releve=date(2024, 11, 25),
            index_gaz=133200.0,
            index_calories=469800.0,
            dju=220.0
        )

        saison_2024.ajouter_releve(releve1)
        saison_2024.ajouter_releve(releve2)
        saison_2024.ajouter_releve(releve3)

        # Créer une saison terminée d'exemple
        saison_2023 = Saison(
            nom="2023-2024",
            date_debut=date(2023, 9, 10),
            date_fin=date(2024, 6, 25)
        )

        releve_2023_1 = Releve(
            date_releve=date(2023, 9, 10),
            index_gaz=118200.0,
            index_calories=445000.0,
            dju=0.0
        )

        releve_2023_2 = Releve(
            date_releve=date(2023, 10, 15),
            index_gaz=121800.0,
            index_calories=450800.0,
            dju=150.0
        )

        releve_2023_3 = Releve(
            date_releve=date(2023, 12, 10),
            index_gaz=127500.0,
            index_calories=459200.0,
            dju=340.0
        )

        saison_2023.ajouter_releve(releve_2023_1)
        saison_2023.ajouter_releve(releve_2023_2)
        saison_2023.ajouter_releve(releve_2023_3)

        # Sauvegarder
        self.saisons = [saison_2023, saison_2024]
        self.sauvegarder_donnees()
