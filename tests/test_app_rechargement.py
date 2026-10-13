"""L'application doit relire le fichier YAML et ne pas écraser les modifications externes."""

from datetime import date

import pytest

from src.data_manager import DataManager
from src.models.releve import Releve
from src.models.saison import Saison
from src.web import app as app_module


@pytest.fixture
def fichier(tmp_path, monkeypatch):
    chemin = tmp_path / "saisons.yaml"
    dm = DataManager(chemin)
    saison = Saison(nom="2025-2026", date_debut=date(2025, 9, 29))
    saison.ajouter_releve(Releve(date(2025, 9, 29), 100.0, 1.0, 0.0))
    dm.saisons = [saison]
    dm.sauvegarder_donnees()

    app_dm = DataManager(chemin)
    app_dm.charger_donnees()
    monkeypatch.setattr(app_module, "data_manager", app_dm)
    app_module.app.config["TESTING"] = True
    return chemin


def modifier_dju_hors_appli(chemin):
    dm = DataManager(chemin)
    dm.charger_donnees()
    dm.saisons[0].releves[0].dju = 99.0
    dm.sauvegarder_donnees()


def test_creation_saison_conserve_les_modifications_externes(fichier):
    modifier_dju_hors_appli(fichier)

    with app_module.app.test_client() as client:
        client.post("/saison/nouvelle", data={"nom": "2026-2027", "date_debut": "2026-10-15"})

    dm = DataManager(fichier)
    dm.charger_donnees()
    assert [s.nom for s in dm.saisons] == ["2025-2026", "2026-2027"]
    assert dm.saisons[0].releves[0].dju == 99.0


def test_lecture_affiche_les_donnees_a_jour(fichier):
    modifier_dju_hors_appli(fichier)

    with app_module.app.test_client() as client:
        client.get("/")

    assert app_module.data_manager.saisons[0].releves[0].dju == 99.0


@pytest.mark.parametrize("url", ["/", "/saison/2025-2026", "/comparaison"])
def test_avertissement_rendement_dans_l_appli(fichier, url):
    with app_module.app.test_client() as client:
        page = client.get(url).get_data(as_text=True)

    assert "Rendement indicatif" in page
