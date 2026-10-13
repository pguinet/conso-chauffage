"""
Génération du site statique des rapports.

Une page par saison (statistiques, graphiques, relevés), une page de
comparaison et une page d'accueil, reliées par une navigation commune.
Plotly.js est écrit une seule fois à côté des pages au lieu d'être
embarqué dans chacune.
"""

from datetime import datetime
from html import escape
from pathlib import Path
from typing import List, Optional

import plotly.graph_objects as go
from plotly.offline import get_plotlyjs

from src.models import Saison
from .graphiques import (
    figure_comparaison_saisons,
    figure_indicateurs_dju,
    figure_rendement_saison,
    figure_rendements_compares,
)
from .tableau import (
    generer_rapport_comparaison_csv,
    generer_rapport_saison_csv,
    html_stats_saison,
    html_tableau_comparaison,
    html_tableau_releves,
)

PLOTLY_JS = "plotly.min.js"
PAGE_ACCUEIL = "index.html"
PAGE_COMPARAISON = "comparaison.html"
CSV_COMPARAISON = "rapport_comparaison.csv"

# Fichiers produits par l'ancienne génération (une page par graphique)
ANCIENS_FICHIERS = ("rapport_*.html", "graphique_*.html")

CSS = """
    * { box-sizing: border-box; }
    body { font-family: Arial, sans-serif; margin: 0; background-color: #f5f5f5; color: #333; }
    a { color: #0056b3; }
    .nav { background-color: #007bff; display: flex; flex-wrap: wrap; align-items: center;
           gap: 4px 20px; padding: 10px 20px; position: sticky; top: 0; z-index: 10; }
    .nav a, .nav summary { color: white; text-decoration: none; font-weight: bold; cursor: pointer; }
    .nav a:hover, .nav summary:hover { text-decoration: underline; }
    .nav a[aria-current="page"] { border-bottom: 2px solid white; }
    .nav .marque { font-size: 1.15em; margin-right: 10px; }
    .menu { position: relative; }
    .menu summary { list-style: none; }
    .menu summary::-webkit-details-marker { display: none; }
    .menu ul { position: absolute; left: 0; top: 100%; margin: 8px 0 0; padding: 6px 0;
               list-style: none; background: white; border-radius: 6px; min-width: 140px;
               box-shadow: 0 4px 12px rgba(0,0,0,0.2); max-height: 70vh; overflow-y: auto; }
    .menu ul a { color: #333; display: block; padding: 6px 16px; font-weight: normal; }
    .menu ul a[aria-current="page"] { font-weight: bold; border-bottom: none; background: #e7f3ff; }
    .container { max-width: 1200px; margin: 20px auto; background-color: white; padding: 20px;
                 border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    h1 { border-bottom: 3px solid #007bff; padding-bottom: 10px; margin-top: 0; }
    h2 { margin-top: 35px; }
    .info { background-color: #e7f3ff; padding: 10px 15px; border-radius: 5px; margin: 20px 0; }
    .pager { display: flex; justify-content: space-between; gap: 10px; margin: 10px 0 20px; }
    .pager a { text-decoration: none; font-weight: bold; }
    .table-scroll { overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    th { background-color: #007bff; color: white; padding: 12px; text-align: left; }
    td { padding: 10px; border-bottom: 1px solid #ddd; }
    tr:hover { background-color: #f5f5f5; }
    .number { text-align: right; }
    .stats, .cartes { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                      gap: 15px; margin: 20px 0; }
    .stat-card, .carte { background-color: #f8f9fa; padding: 15px; border-radius: 5px;
                         border-left: 4px solid #007bff; }
    .stat-label { font-size: 0.9em; color: #666; margin-bottom: 5px; }
    .stat-value { font-size: 1.5em; font-weight: bold; }
    .carte { display: block; text-decoration: none; color: inherit; }
    .carte:hover { background-color: #e7f3ff; }
    .carte strong { font-size: 1.2em; color: #0056b3; }
    .carte span { display: block; color: #666; margin-top: 5px; }
    .carte.en-cours { border-left-color: #28a745; }
    .vide { color: #666; font-style: italic; }
    .bouton { display: inline-block; padding: 8px 14px; background: #6c757d; color: white;
              border-radius: 4px; text-decoration: none; }
    .footer { text-align: center; color: #666; font-size: 0.9em; margin: 20px; }
"""


def page_saison(nom: str) -> str:
    """Nom du fichier de la page d'une saison."""
    return f"saison_{nom}.html"


def csv_saison(nom: str) -> str:
    """Nom du fichier CSV d'une saison."""
    return f"rapport_{nom}.csv"


def _graphique(fig: go.Figure) -> str:
    """Graphique Plotly sous forme de fragment HTML, sans embarquer plotly.js."""
    return fig.to_html(
        full_html=False,
        include_plotlyjs=False,
        config={'responsive': True, 'displaylogo': False}
    )


def _navigation(saisons: List[Saison], page_courante: str) -> str:
    """Barre de navigation commune à toutes les pages."""
    def lien(href: str, texte: str) -> str:
        courant = ' aria-current="page"' if href == page_courante else ''
        return f'<a href="{escape(href)}"{courant}>{escape(texte)}</a>'

    liens_saisons = "".join(
        f"<li>{lien(page_saison(s.nom), s.nom)}</li>" for s in reversed(saisons)
    )
    return f"""<nav class="nav">
    <a class="marque" href="{PAGE_ACCUEIL}">Suivi chaudière</a>
    {lien(PAGE_ACCUEIL, "Accueil")}
    {lien(PAGE_COMPARAISON, "Comparaison")}
    <details class="menu"><summary>Saisons ▾</summary><ul>{liens_saisons}</ul></details>
</nav>"""


def _page(titre: str, contenu: str, saisons: List[Saison], fichier: str, plotly: bool) -> str:
    """Page HTML complète avec navigation et pied de page."""
    script = f'    <script src="{PLOTLY_JS}"></script>\n' if plotly else ''
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(titre)} – Suivi chaudière</title>
{script}    <style>{CSS}    </style>
</head>
<body>
{_navigation(saisons, fichier)}
<main class="container">
{contenu}
</main>
<div class="footer">Rapports générés le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</div>
</body>
</html>
"""


def _periode(saison: Saison) -> str:
    debut = saison.date_debut.strftime('%d/%m/%Y')
    if saison.date_fin is None:
        return f"Depuis le {debut} (en cours)"
    return f"Du {debut} au {saison.date_fin.strftime('%d/%m/%Y')}"


def _contenu_saison(saison: Saison, precedente: Optional[Saison], suivante: Optional[Saison]) -> str:
    """Contenu de la page d'une saison."""
    nom = escape(saison.nom)
    pager = '<div class="pager">'
    pager += (f'<a href="{escape(page_saison(precedente.nom))}">← {escape(precedente.nom)}</a>'
              if precedente else '<span></span>')
    pager += (f'<a href="{escape(page_saison(suivante.nom))}">{escape(suivante.nom)} →</a>'
              if suivante else '<span></span>')
    pager += '</div>'

    duree = saison.get_duree_jours()
    html = f"""{pager}
<h1>Saison {nom}</h1>
<div class="info">{_periode(saison)}{f" · {duree} jours" if duree is not None else ""} · {len(saison.releves)} relevé(s)</div>
"""
    if len(saison.releves) < 2:
        return html + '<p class="vide">Pas encore assez de relevés pour calculer des indicateurs.</p>\n'

    html += html_stats_saison(saison)

    html += "<h2>Rendement</h2>\n"
    if any(r.rendement is not None for r in saison.releves):
        html += _graphique(figure_rendement_saison(saison))
    else:
        html += '<p class="vide">Rendement non mesurable : aucune calorie comptée sur la saison.</p>\n'

    figure_dju = figure_indicateurs_dju(saison)
    if figure_dju is not None:
        html += "<h2>Consommation et calories par DJU</h2>\n" + _graphique(figure_dju)

    html += f"""<h2>Relevés</h2>
<p><a class="bouton" href="{escape(csv_saison(saison.nom))}" download>Télécharger le CSV</a></p>
<div class="table-scroll">
{html_tableau_releves(saison)}</div>
"""
    return html


def _contenu_comparaison(saisons: List[Saison]) -> str:
    """Contenu de la page de comparaison."""
    return f"""<h1>Comparaison des saisons</h1>
<p><a class="bouton" href="{CSV_COMPARAISON}" download>Télécharger le CSV</a></p>
<div class="table-scroll">
{html_tableau_comparaison(saisons, lien_saison=page_saison)}</div>
<h2>Indicateurs par saison</h2>
{_graphique(figure_comparaison_saisons(saisons))}
<h2>Évolution des rendements</h2>
{_graphique(figure_rendements_compares(saisons))}
"""


def _contenu_accueil(saisons: List[Saison]) -> str:
    """Contenu de la page d'accueil : une carte par saison, la plus récente en tête."""
    cartes = ""
    for saison in reversed(saisons):
        rendement = saison.get_rendement_moyen()
        detail = f"Rendement moyen {rendement:.1f}\u00a0%" if rendement is not None else "Rendement non mesurable"
        if len(saison.releves) < 2:
            detail = "Pas encore d'indicateurs"
        classe = "carte en-cours" if saison.est_en_cours() else "carte"
        cartes += f"""    <a class="{classe}" href="{escape(page_saison(saison.nom))}">
        <strong>{escape(saison.nom)}</strong>
        <span>{_periode(saison)}</span>
        <span>{detail}</span>
    </a>
"""
    return f"""<h1>Suivi de consommation de la chaudière</h1>
<p>{len(saisons)} saison(s) de chauffe. <a href="{PAGE_COMPARAISON}">Comparer les saisons →</a></p>
<div class="cartes">
{cartes}</div>
"""


def generer_site(saisons: List[Saison], output_dir: Path) -> List[Path]:
    """
    Génère le site statique complet des rapports.

    Args:
        saisons: Les saisons à publier
        output_dir: Répertoire de sortie

    Returns:
        La liste des fichiers écrits
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    for motif in ANCIENS_FICHIERS:
        for ancien in output_dir.glob(motif):
            ancien.unlink()

    saisons = sorted(saisons, key=lambda s: s.date_debut)
    fichiers: List[Path] = []

    def ecrire(nom: str, contenu: str) -> None:
        chemin = output_dir / nom
        chemin.write_text(contenu, encoding='utf-8')
        fichiers.append(chemin)

    ecrire(PLOTLY_JS, get_plotlyjs())

    for i, saison in enumerate(saisons):
        precedente = saisons[i - 1] if i > 0 else None
        suivante = saisons[i + 1] if i + 1 < len(saisons) else None
        fichier = page_saison(saison.nom)
        ecrire(fichier, _page(f"Saison {saison.nom}", _contenu_saison(saison, precedente, suivante),
                              saisons, fichier, plotly=True))
        generer_rapport_saison_csv(saison, output_dir / csv_saison(saison.nom))
        fichiers.append(output_dir / csv_saison(saison.nom))

    ecrire(PAGE_COMPARAISON, _page("Comparaison", _contenu_comparaison(saisons),
                                   saisons, PAGE_COMPARAISON, plotly=True))
    generer_rapport_comparaison_csv(saisons, output_dir / CSV_COMPARAISON)
    fichiers.append(output_dir / CSV_COMPARAISON)

    ecrire(PAGE_ACCUEIL, _page("Accueil", _contenu_accueil(saisons),
                               saisons, PAGE_ACCUEIL, plotly=False))
    return fichiers
