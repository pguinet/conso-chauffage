"""Configuration commune des tests."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest  # noqa: E402

import src.config  # noqa: E402


@pytest.fixture
def coefficient_gaz_10(tmp_path, monkeypatch):
    """Configuration fixe (10 kWh/m³, 1 MWh par unité calories), pour des valeurs attendues simples."""
    dossier = tmp_path / "config-10"
    dossier.mkdir()
    (dossier / "calculs.yaml").write_text(
        "gaz:\n  coefficient_kwh_par_m3: 10.0\ncompteur_calories:\n  kwh_par_unite: 1000.0\n",
        encoding="utf-8")
    monkeypatch.setattr(src.config, "_config", src.config.Config(dossier))
