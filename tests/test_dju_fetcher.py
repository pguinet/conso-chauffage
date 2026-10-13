"""Tests du calcul des DJU."""

from datetime import date, timedelta

import pytest

from src.services.dju_fetcher import DJUFetcher


class FakeFetcher(DJUFetcher):
    """Fetcher hors ligne : la température d'un jour vaut 10 + son numéro dans le mois."""

    def __init__(self):
        super().__init__()
        self.appels = []

    def _fetch_temperatures_open_meteo(self, date_debut, date_fin):
        self.appels.append((date_debut, date_fin))
        jours = (date_fin - date_debut).days + 1
        return [10.0 + (date_debut + timedelta(days=i)).day for i in range(jours)]


def test_debut_periode_est_le_lendemain():
    assert DJUFetcher.debut_periode(date(2026, 4, 22)) == date(2026, 4, 23)


def test_calcul_ignore_temperatures_au_dessus_de_la_base():
    assert DJUFetcher.calculate_dju_from_temperatures([10.0, 20.0, None, 17.5]) == 8.5


def test_depuis_dernier_releve_exclut_le_jour_du_releve_precedent():
    fetcher = FakeFetcher()

    fetcher.get_dju_depuis_dernier_releve(date(2026, 4, 1), date(2026, 4, 3))

    assert fetcher.appels == [(date(2026, 4, 2), date(2026, 4, 3))]


def test_dju_par_releves_un_seul_appel_et_pas_de_double_comptage():
    fetcher = FakeFetcher()
    dates = [date(2026, 4, 1), date(2026, 4, 3), date(2026, 4, 6)]

    resultats = fetcher.get_dju_par_releves(dates)

    # Températures : 12, 13 (02-03/04) puis 14, 15, 16 (04-06/04)
    assert resultats == [6.0 + 5.0, 4.0 + 3.0 + 2.0]
    assert fetcher.appels == [(date(2026, 4, 2), date(2026, 4, 6))]


def test_dju_par_releves_coherent_avec_calcul_unitaire():
    dates = [date(2026, 4, 1), date(2026, 4, 3), date(2026, 4, 6)]

    groupes = FakeFetcher().get_dju_par_releves(dates)
    unitaires = [
        FakeFetcher().get_dju_depuis_dernier_releve(a, b)
        for a, b in zip(dates, dates[1:])
    ]

    assert groupes == unitaires


@pytest.mark.parametrize("dates", [[], [date(2026, 4, 1)]])
def test_dju_par_releves_sans_periode(dates):
    assert FakeFetcher().get_dju_par_releves(dates) == []


def test_dju_par_releves_refuse_dates_non_croissantes():
    dates = [date(2026, 4, 3), date(2026, 4, 3)]

    assert FakeFetcher().get_dju_par_releves(dates) is None


def test_dju_par_releves_donnees_incompletes():
    class Incomplet(DJUFetcher):
        def _fetch_temperatures_open_meteo(self, date_debut, date_fin):
            return [10.0]

    assert Incomplet().get_dju_par_releves([date(2026, 4, 1), date(2026, 4, 5)]) is None
