"""Module de calcul pour les indicateurs de performance de la chaudière."""

from typing import List, Dict
from src.models import Saison


# Constantes de conversion
M3_GAZ_VERS_KWH = 10.0  # 1 m³ de gaz ≈ 10 kWh (valeur typique)
CALORIE_COMPTEUR_VERS_KWH = 1000.0  # 1 unité compteur calories = 1 MWh = 1000 kWh


def calculer_rendement(calories_produites: float, gaz_consomme: float) -> float:
    """
    Calcule le rendement de la chaudière.

    Args:
        calories_produites: Calories produites (en MWh)
        gaz_consomme: Gaz consommé (en m³)

    Returns:
        Le rendement en pourcentage
    """
    if gaz_consomme <= 0:
        return 0.0

    energie_gaz_kwh = gaz_consomme * M3_GAZ_VERS_KWH
    calories_kwh = calories_produites * CALORIE_COMPTEUR_VERS_KWH  # Conversion MWh -> kWh
    rendement = (calories_kwh / energie_gaz_kwh) * 100

    return rendement


def calculer_conso_par_dju(consommation: float, dju: float) -> float:
    """
    Calcule la consommation par DJU.

    Args:
        consommation: Consommation de gaz (en m³)
        dju: Degrés Jours Unifiés

    Returns:
        Consommation par DJU
    """
    if dju <= 0:
        return 0.0
    return consommation / dju


def calculer_calories_par_dju(calories: float, dju: float) -> float:
    """
    Calcule les calories produites par DJU.

    Args:
        calories: Calories produites
        dju: Degrés Jours Unifiés

    Returns:
        Calories par DJU
    """
    if dju <= 0:
        return 0.0
    return calories / dju


def comparer_saisons(saisons: List[Saison]) -> Dict[str, Dict]:
    """
    Compare plusieurs saisons entre elles.

    Args:
        saisons: Liste des saisons à comparer

    Returns:
        Dictionnaire avec les statistiques de comparaison
    """
    comparaison = {}

    for saison in saisons:
        stats = {
            'nom': saison.nom,
            'date_debut': saison.date_debut,
            'date_fin': saison.date_fin,
            'duree_jours': saison.get_duree_jours(),
            'en_cours': saison.est_en_cours(),
            'nombre_releves': len(saison.releves),
            'conso_totale_gaz': saison.get_conso_totale_gaz(),
            'calories_totales': saison.get_calories_totales(),
            'dju_total': saison.get_dju_total(),
            'rendement_moyen': saison.get_rendement_moyen()
        }

        # Calculs supplémentaires
        if stats['dju_total'] > 0:
            stats['conso_par_dju'] = stats['conso_totale_gaz'] / stats['dju_total']
            stats['calories_par_dju'] = stats['calories_totales'] / stats['dju_total']
        else:
            stats['conso_par_dju'] = 0.0
            stats['calories_par_dju'] = 0.0

        # Rendement global de la saison, sur les seules périodes mesurables
        # (calories comptées) pour rester cohérent avec le rendement moyen
        mesures = [r for r in saison.releves if r.rendement is not None]
        gaz_mesure = sum(r.conso_gaz for r in mesures)
        if gaz_mesure > 0:
            stats['rendement_global'] = calculer_rendement(
                sum(r.calories_produites for r in mesures),
                gaz_mesure
            )
        else:
            stats['rendement_global'] = None

        comparaison[saison.nom] = stats

    return comparaison


def analyser_tendance_rendement(saison: Saison) -> Dict:
    """
    Analyse la tendance du rendement sur une saison.

    Args:
        saison: La saison à analyser

    Returns:
        Dictionnaire avec les statistiques de tendance
    """
    rendements = [r.rendement for r in saison.releves if r.rendement is not None]

    if not rendements:
        return {
            'min': None,
            'max': None,
            'moyenne': None,
            'ecart_type': None,
            'tendance': None
        }

    moyenne = sum(rendements) / len(rendements)
    min_rendement = min(rendements)
    max_rendement = max(rendements)

    # Calcul de l'écart-type
    if len(rendements) > 1:
        variance = sum((r - moyenne) ** 2 for r in rendements) / len(rendements)
        ecart_type = variance ** 0.5
    else:
        ecart_type = 0.0

    # Analyse de tendance simple (premier vs dernier tiers)
    if len(rendements) >= 3:
        tiers = len(rendements) // 3
        premier_tiers = sum(rendements[:tiers]) / tiers
        dernier_tiers = sum(rendements[-tiers:]) / tiers

        if dernier_tiers > premier_tiers + 1:
            tendance = "amélioration"
        elif dernier_tiers < premier_tiers - 1:
            tendance = "dégradation"
        else:
            tendance = "stable"
    else:
        tendance = "données insuffisantes"

    return {
        'min': min_rendement,
        'max': max_rendement,
        'moyenne': moyenne,
        'ecart_type': ecart_type,
        'tendance': tendance
    }
