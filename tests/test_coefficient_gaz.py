"""Le coefficient de conversion du gaz (kWh/m³) est réglable dans config/calculs.yaml."""

from datetime import date

import pytest

import src.config
from src.calculs.rendement import calculer_rendement
from src.config import Config
from src.models.releve import Releve
from src.models.saison import Saison


@pytest.fixture
def config(tmp_path, monkeypatch):
    def avec(contenu=None):
        if contenu is not None:
            (tmp_path / "calculs.yaml").write_text(contenu, encoding="utf-8")
        cfg = Config(tmp_path)
        monkeypatch.setattr(src.config, "_config", cfg)
        return cfg
    return avec


def rendement_periode():
    saison = Saison(nom="test", date_debut=date(2026, 1, 1))
    saison.ajouter_releve(Releve(date(2026, 1, 1), 0.0, 0.0, 0.0))
    saison.ajouter_releve(Releve(date(2026, 2, 1), 1000.0, 12.0, 300.0))
    return saison.releves[1].rendement


def test_valeurs_par_defaut_sans_fichier(config):
    cfg = config()

    assert cfg.get_coefficient_gaz() == 13.5
    assert cfg.coefficient_gaz_a_confirmer() is True
    # 12 MWh pour 1000 m³ × 13,5 kWh
    assert rendement_periode() == pytest.approx(12000 / 13500 * 100)


def test_coefficient_configure(config):
    config("gaz:\n  coefficient_kwh_par_m3: 12.0\n  a_confirmer: false\n")

    assert rendement_periode() == pytest.approx(100.0)
    assert calculer_rendement(12.0, 1000.0) == pytest.approx(100.0)
    assert src.config.get_config().coefficient_gaz_a_confirmer() is False


def test_unite_compteur_calories_configuree(config):
    config("gaz:\n  coefficient_kwh_par_m3: 10.0\ncompteur_calories:\n  kwh_par_unite: 500.0\n")

    assert rendement_periode() == pytest.approx(60.0)


@pytest.mark.parametrize("valeur", ["0", "-3", "abc"])
def test_coefficient_invalide_refuse(config, valeur):
    cfg = config(f"gaz:\n  coefficient_kwh_par_m3: {valeur}\n")

    with pytest.raises(ValueError):
        cfg.get_coefficient_gaz()


def test_fichier_du_depot_estimation_a_confirmer():
    cfg = Config()

    assert cfg.get_coefficient_gaz() == 13.5
    assert cfg.coefficient_gaz_a_confirmer() is True
