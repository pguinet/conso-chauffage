"""Tests du site statique des rapports."""

from datetime import date
from html.parser import HTMLParser
from pathlib import Path

import pytest

from src.models.releve import Releve
from src.models.saison import Saison
from src.rapports.site import generer_site


def saison(nom, annee, releves, terminee=True):
    s = Saison(nom=nom, date_debut=date(annee, 10, 1),
               date_fin=date(annee + 1, 5, 1) if terminee else None)
    for jour, gaz, cal, dju in releves:
        s.ajouter_releve(Releve(date(annee, 10, 1) + jour, gaz, cal, dju))
    return s


@pytest.fixture
def saisons():
    from datetime import timedelta as j
    return [
        # Sans compteur calories : rendement non mesurable
        saison("2012-2013", 2012, [(j(0), 0.0, 0.0, 0.0), (j(30), 1000.0, 0.0, 300.0)]),
        saison("2013-2014", 2013, [(j(0), 0.0, 0.0, 0.0), (j(30), 1000.0, 12.0, 300.0),
                                   (j(60), 2500.0, 30.0, 400.0)]),
        # Saison en cours sans relevé
        saison("2014-2015", 2014, [], terminee=False),
    ]


class Liens(HTMLParser):
    def __init__(self):
        super().__init__()
        self.liens = []

    def handle_starttag(self, tag, attrs):
        for nom, valeur in attrs:
            if nom in ("href", "src"):
                self.liens.append(valeur)


def liens(chemin: Path):
    parser = Liens()
    parser.feed(chemin.read_text(encoding="utf-8"))
    return parser.liens


@pytest.fixture
def site(tmp_path, saisons):
    generer_site(saisons, tmp_path)
    return tmp_path


def test_pages_generees(site):
    noms = {p.name for p in site.iterdir()}

    assert {"index.html", "comparaison.html", "plotly.min.js", "rapport_comparaison.csv",
            "saison_2012-2013.html", "saison_2013-2014.html", "saison_2014-2015.html",
            "rapport_2013-2014.csv"} <= noms


def test_aucun_lien_casse(site):
    for page in site.glob("*.html"):
        for lien in liens(page):
            assert (site / lien).exists(), f"{page.name} -> {lien}"


def test_navigation_commune_sur_toutes_les_pages(site):
    attendus = {"index.html", "comparaison.html", "saison_2012-2013.html",
                "saison_2013-2014.html", "saison_2014-2015.html"}
    for page in site.glob("*.html"):
        assert attendus <= set(liens(page)), page.name


def test_saison_precedente_et_suivante(site):
    contenu = (site / "saison_2013-2014.html").read_text(encoding="utf-8")

    assert "← 2012-2013" in contenu
    assert "2014-2015 →" in contenu
    assert "←" not in (site / "saison_2012-2013.html").read_text(encoding="utf-8")


def test_plotly_partage_et_non_embarque(site):
    for page in site.glob("*.html"):
        assert page.stat().st_size < 200_000, page.name
    assert "plotly.min.js" in liens(site / "saison_2013-2014.html")


def test_saison_sans_calories(site):
    contenu = (site / "saison_2012-2013.html").read_text(encoding="utf-8")

    assert "Rendement non mesurable" in contenu
    assert "Consommation et calories par DJU" in contenu


def test_saison_sans_releve(site):
    contenu = (site / "saison_2014-2015.html").read_text(encoding="utf-8")

    assert "Pas encore assez de relevés" in contenu


def test_anciens_fichiers_supprimes(tmp_path, saisons):
    (tmp_path / "graphique_complet_2013-2014.html").write_text("ancien")
    (tmp_path / "rapport_2013-2014.html").write_text("ancien")
    (tmp_path / "notes.txt").write_text("à garder")

    generer_site(saisons, tmp_path)

    assert not (tmp_path / "graphique_complet_2013-2014.html").exists()
    assert not (tmp_path / "rapport_2013-2014.html").exists()
    assert (tmp_path / "notes.txt").exists()


def test_avertissement_tant_que_le_coefficient_est_a_confirmer(site):
    for page in ("index.html", "saison_2013-2014.html", "comparaison.html"):
        assert "Rendement indicatif" in (site / page).read_text(encoding="utf-8"), page


def test_pas_d_avertissement_une_fois_confirme(tmp_path, saisons, monkeypatch):
    import src.config
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "calculs.yaml").write_text(
        "gaz:\n  coefficient_kwh_par_m3: 13.0\n  a_confirmer: false\n", encoding="utf-8")
    monkeypatch.setattr(src.config, "_config", src.config.Config(tmp_path / "config"))

    generer_site(saisons, tmp_path / "site")

    assert "Rendement indicatif" not in (tmp_path / "site" / "index.html").read_text(encoding="utf-8")
