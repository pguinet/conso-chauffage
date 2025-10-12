"""Module de génération de rapports et graphiques."""

from .tableau import (
    generer_rapport_saison_csv,
    generer_rapport_saison_html,
    generer_rapport_comparaison_csv,
    generer_rapport_comparaison_html
)

from .graphiques import (
    generer_graphique_rendement_saison,
    generer_graphique_complet_saison,
    generer_graphique_comparaison_saisons,
    generer_graphique_rendements_compares
)

__all__ = [
    'generer_rapport_saison_csv',
    'generer_rapport_saison_html',
    'generer_rapport_comparaison_csv',
    'generer_rapport_comparaison_html',
    'generer_graphique_rendement_saison',
    'generer_graphique_complet_saison',
    'generer_graphique_comparaison_saisons',
    'generer_graphique_rendements_compares'
]
