"""Tests du cache DJU."""

from datetime import date

from src.services.dju_cache import DJUCache


def test_cle_stable_entre_deux_instances(tmp_path):
    fichier = tmp_path / "cache.json"
    DJUCache(fichier).set(date(2026, 3, 26), date(2026, 4, 22), 193.5)

    assert DJUCache(fichier).get(date(2026, 3, 26), date(2026, 4, 22)) == 193.5


def test_cle_contient_les_deux_dates(tmp_path):
    cache = DJUCache(tmp_path / "cache.json")

    cle = cache._make_key(date(2026, 3, 26), date(2026, 4, 22), 18.0)

    assert cle == "2026-03-26_2026-04-22_18.0"


def test_periode_absente(tmp_path):
    cache = DJUCache(tmp_path / "cache.json")

    assert cache.get(date(2026, 3, 26), date(2026, 4, 22)) is None
