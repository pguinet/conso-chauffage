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
                'rendement_moyen': {'y_min': 100, 'y_max': None},
                'conso_totale_gaz': {'y_min': 30000, 'y_max': None},
                'conso_par_dju': {'y_min': 15, 'y_max': None},
                'calories_par_dju': {'y_min': 0, 'y_max': None}
            },
            'echelles_saison': {
                'rendement': {'y_min': 80, 'y_max': None},
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
