"""Module de calculs pour les indicateurs de performance."""

from .rendement import (
    calculer_rendement,
    calculer_conso_par_dju,
    calculer_calories_par_dju,
    comparer_saisons,
    analyser_tendance_rendement
)

__all__ = [
    'calculer_rendement',
    'calculer_conso_par_dju',
    'calculer_calories_par_dju',
    'comparer_saisons',
    'analyser_tendance_rendement'
]
