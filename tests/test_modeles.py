"""Tests des modèles : seules les données saisies sont stockées, le reste est calculé."""

from datetime import date

import pytest

from src.models.releve import Releve
from src.models.saison import Saison

pytestmark = pytest.mark.usefixtures("coefficient_gaz_10")

CHAMPS_SAISIS = {"date", "index_gaz", "index_calories", "dju"}


def saison_exemple():
    return Saison.from_dict({
        "nom": "2025-2026",
        "date_debut": "2025-09-29",
        "date_fin": "2026-05-27",
        "releves": [
            {"date": "2025-09-29", "index_gaz": 0.0, "index_calories": 0.0, "dju": 0.0},
            # Valeurs calculées périmées, telles qu'on en trouvait dans l'ancien YAML
            {"date": "2025-10-30", "index_gaz": 1000.0, "index_calories": 12.0, "dju": 100.0,
             "conso_gaz": 999.0, "rendement": 0.0},
            {"date": "2025-12-02", "index_gaz": 3000.0, "index_calories": 34.0, "dju": 200.0},
        ],
    })


def test_serialisation_ne_contient_que_les_donnees_saisies():
    data = saison_exemple().to_dict()

    assert all(set(r) == CHAMPS_SAISIS for r in data["releves"])


def test_valeurs_stockees_ignorees_au_chargement():
    r = saison_exemple().releves[1]

    assert r.conso_gaz == 1000.0
    assert r.rendement == pytest.approx(120.0)


def test_aller_retour_dict():
    saison = saison_exemple()

    copie = Saison.from_dict(saison.to_dict())

    assert [r.rendement for r in copie.releves] == [r.rendement for r in saison.releves]


def test_indicateurs_suivent_les_donnees_saisies():
    saison = saison_exemple()
    r = saison.releves[2]

    r.dju = 400.0
    saison.releves[1].index_gaz = 2000.0

    assert r.conso_gaz == 1000.0
    assert r.conso_gaz_par_dju == pytest.approx(2.5)


def test_premier_releve_sans_indicateurs():
    r = saison_exemple().releves[0]

    assert (r.conso_gaz, r.calories_produites, r.rendement) == (None, None, None)


def test_releve_isole_sans_indicateurs():
    r = Releve(date(2026, 1, 1), 100.0, 1.0, 50.0)

    assert r.conso_gaz is None
    assert r.conso_gaz_par_dju is None


def test_ajout_d_un_releve_oublie_dans_l_ordre_chronologique():
    saison = saison_exemple()

    saison.ajouter_releve(Releve(date(2025, 11, 15), 2000.0, 22.0, 50.0))

    dates = [r.date_releve for r in saison.releves]
    assert dates == sorted(dates)
    assert saison.releves[2].conso_gaz == 1000.0
    assert saison.releves[3].conso_gaz == 1000.0


def test_duree_saison_terminee():
    assert saison_exemple().get_duree_jours() == 240


def test_duree_saison_en_cours():
    assert Saison(nom="x", date_debut=date(2026, 10, 15)).get_duree_jours() is None
