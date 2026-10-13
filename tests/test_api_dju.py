"""Tests de la route POST /api/dju/calculate."""

from datetime import date

import pytest

from src.services.dju_cache import DJUCache
from src.web import app as app_module


@pytest.fixture
def client(tmp_path, monkeypatch):
    appels = []

    def faux_get_dju_period(date_debut, date_fin, base_temp=18.0):
        appels.append((date_debut, date_fin))
        return 42.0

    monkeypatch.setattr(app_module, "dju_cache", DJUCache(tmp_path / "cache.json"))
    monkeypatch.setattr(app_module.dju_fetcher, "get_dju_period", faux_get_dju_period)
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as c:
        c.appels = appels
        yield c


def test_periode_commence_le_lendemain_du_dernier_releve(client):
    reponse = client.post("/api/dju/calculate", json={
        "date_dernier_releve": "2026-03-25",
        "date_releve": "2026-04-22",
    })

    data = reponse.get_json()
    assert reponse.status_code == 200
    assert data["dju"] == 42.0
    assert data["date_debut"] == "2026-03-26"
    assert client.appels == [(date(2026, 3, 26), date(2026, 4, 22))]


def test_second_appel_servi_par_le_cache(client):
    corps = {"date_dernier_releve": "2026-03-25", "date_releve": "2026-04-22"}

    client.post("/api/dju/calculate", json=corps)
    data = client.post("/api/dju/calculate", json=corps).get_json()

    assert data["cached"] is True
    assert len(client.appels) == 1


def test_parametres_manquants(client):
    reponse = client.post("/api/dju/calculate", json={"date_releve": "2026-04-22"})

    assert reponse.status_code == 400


def test_date_anterieure_refusee(client):
    reponse = client.post("/api/dju/calculate", json={
        "date_dernier_releve": "2026-04-22",
        "date_releve": "2026-04-22",
    })

    assert reponse.status_code == 400
    assert client.appels == []
