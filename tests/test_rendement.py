"""Tests du rendement par relevé et par saison."""

from datetime import date

import pytest

from src.models.releve import Releve
from src.models.saison import Saison


def releve(jour, gaz, calories, dju=10.0):
    return Releve(date_releve=date(2026, 1, jour), index_gaz=gaz, index_calories=calories, dju=dju)


def saison_avec(*releves):
    saison = Saison(nom="test", date_debut=date(2026, 1, 1))
    saison.ajouter_releve(releve(1, 0.0, 0.0, dju=0.0))
    for r in releves:
        saison.ajouter_releve(r)
    return saison


def test_rendement_d_une_periode():
    s = saison_avec(releve(10, 1000.0, 12.0))

    # 12 MWh produits pour 1000 m³ × 10 kWh
    assert s.releves[1].rendement == pytest.approx(120.0)


def test_periode_sans_calories_non_mesurable():
    s = saison_avec(releve(10, 33.0, 0.0))

    assert s.releves[1].rendement is None
    assert s.releves[1].conso_gaz == 33.0


def test_rendement_saison_pondere_par_la_consommation():
    # 120 % sur 3000 m³ puis 100 % sur 1000 m³ : 115 %, pas 110 %
    s = saison_avec(releve(10, 3000.0, 36.0), releve(20, 4000.0, 46.0))

    assert s.get_rendement_moyen() == pytest.approx(115.0)


def test_rendement_saison_ignore_les_periodes_sans_calories():
    s = saison_avec(releve(10, 1000.0, 12.0), releve(20, 1033.0, 12.0))

    assert s.get_rendement_moyen() == pytest.approx(120.0)


def test_rendement_saison_sans_compteur_calories():
    s = saison_avec(releve(10, 1000.0, 0.0), releve(20, 2000.0, 0.0))

    assert s.get_rendement_moyen() is None


def test_rendement_saison_vide():
    assert Saison(nom="vide", date_debut=date(2026, 1, 1)).get_rendement_moyen() is None
