"""Module de gestion de la configuration de l'application."""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class Config:
    """Gestionnaire de configuration de l'application."""
    
    def __init__(self, config_dir: Path = None):
        """
        Initialise le gestionnaire de configuration.
        
        Args:
            config_dir: Répertoire contenant les fichiers de configuration
        """
        if config_dir is None:
            # Par défaut, utiliser le dossier config à la racine du projet
            self.config_dir = Path(__file__).parent.parent / 'config'
        else:
            self.config_dir = Path(config_dir)
        
        self._graphiques_config = None
        self._calculs_config = None

    def load_calculs_config(self) -> Dict[str, Any]:
        """
        Charge la configuration des calculs (config/calculs.yaml).

        Returns:
            Dictionnaire de configuration, vide si le fichier n'existe pas
        """
        if self._calculs_config is None:
            config_file = self.config_dir / 'calculs.yaml'
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    self._calculs_config = yaml.safe_load(f) or {}
            else:
                self._calculs_config = {}
        return self._calculs_config

    def _valeur_positive(self, section: str, cle: str, defaut: float) -> float:
        valeur = self.load_calculs_config().get(section, {}).get(cle, defaut)
        try:
            valeur = float(valeur)
        except (TypeError, ValueError):
            raise ValueError(f"{section}.{cle} doit être un nombre : {valeur!r}")
        if valeur <= 0:
            raise ValueError(f"{section}.{cle} doit être strictement positif : {valeur}")
        return valeur

    def get_coefficient_gaz(self) -> float:
        """Coefficient de conversion du gaz en kWh par m³ compté (défaut : 13,7)."""
        return self._valeur_positive('gaz', 'coefficient_kwh_par_m3', 13.7)

    def coefficient_gaz_a_confirmer(self) -> bool:
        """Vrai tant que le coefficient du gaz n'a pas été vérifié sur une facture."""
        return bool(self.load_calculs_config().get('gaz', {}).get('a_confirmer', True))

    def get_kwh_par_unite_calories(self) -> float:
        """Énergie d'une unité du compteur calories en kWh (défaut : 1000, soit 1 MWh)."""
        return self._valeur_positive('compteur_calories', 'kwh_par_unite', 1000.0)
    
    def load_graphiques_config(self) -> Dict[str, Any]:
        """
        Charge la configuration des graphiques.
        
        Returns:
            Dictionnaire avec la configuration des graphiques
        """
        if self._graphiques_config is None:
            config_file = self.config_dir / 'graphiques.yaml'
            
            if not config_file.exists():
                # Configuration par défaut si le fichier n'existe pas
                self._graphiques_config = self._get_default_graphiques_config()
            else:
                with open(config_file, 'r', encoding='utf-8') as f:
                    self._graphiques_config = yaml.safe_load(f)
        
        return self._graphiques_config
    
    def get_echelle_comparaison(self, metric: str) -> Dict[str, Optional[float]]:
        """
        Récupère les paramètres d'échelle pour un graphique de comparaison.
        
        Args:
            metric: Nom de la métrique (rendement_moyen, conso_totale_gaz, etc.)
        
        Returns:
            Dictionnaire avec y_min et y_max
        """
        config = self.load_graphiques_config()
        echelles = config.get('echelles_comparaison', {})
        
        default = {'y_min': 0, 'y_max': None}
        return echelles.get(metric, default)
    
    def get_echelle_saison(self, metric: str) -> Dict[str, Optional[float]]:
        """
        Récupère les paramètres d'échelle pour un graphique de saison.
        
        Args:
            metric: Nom de la métrique (rendement, conso_gaz_par_dju, etc.)
        
        Returns:
            Dictionnaire avec y_min et y_max
        """
        config = self.load_graphiques_config()
        echelles = config.get('echelles_saison', {})
        
        default = {'y_min': 0, 'y_max': None}
        return echelles.get(metric, default)
    
    def get_parametres_graphiques(self) -> Dict[str, Any]:
        """
        Récupère les paramètres généraux des graphiques.
        
        Returns:
            Dictionnaire avec les paramètres
        """
        config = self.load_graphiques_config()
        return config.get('parametres', {
            'show_grid': True,
            'hauteur_graphique': 500,
            'palette': 'Plotly'
        })
    
    @staticmethod
    def _get_default_graphiques_config() -> Dict[str, Any]:
        """
        Retourne la configuration par défaut des graphiques.
        
        Returns:
            Configuration par défaut
        """
        return {
            'echelles_comparaison': {
                'rendement_moyen': {'y_min': 70, 'y_max': None},
                'conso_totale_gaz': {'y_min': 30000, 'y_max': None},
                'conso_par_dju': {'y_min': 15, 'y_max': None},
                'calories_par_dju': {'y_min': 0, 'y_max': None}
            },
            'echelles_saison': {
                'rendement': {'y_min': 60, 'y_max': None},
                'conso_gaz_par_dju': {'y_min': 10, 'y_max': None},
                'calories_par_dju': {'y_min': 0, 'y_max': None}
            },
            'parametres': {
                'show_grid': True,
                'hauteur_graphique': 500,
                'palette': 'Plotly'
            }
        }


# Instance globale
_config = Config()


def get_config() -> Config:
    """Retourne l'instance globale de configuration."""
    return _config
