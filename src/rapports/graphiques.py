"""Module de génération de graphiques pour les rapports."""

from pathlib import Path
from typing import List, Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.models import Saison
from src.calculs import comparer_saisons
from src.config import get_config


def figure_rendement_saison(saison: Saison) -> go.Figure:
    """Construit le graphique d'évolution du rendement d'une saison."""
    # Filtrer les relevés avec rendement calculé
    releves_avec_rendement = [r for r in saison.releves if r.rendement is not None]

    if not releves_avec_rendement:
        # Créer un graphique vide avec message
        fig = go.Figure()
        fig.add_annotation(
            text="Pas de données de rendement disponibles",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20)
        )
        fig.update_layout(
            title=f"Évolution du Rendement - Saison {saison.nom}",
            xaxis_title="Date",
            yaxis_title="Rendement (%)"
        )
        return fig

    dates = [r.date_releve for r in releves_avec_rendement]
    rendements = [r.rendement for r in releves_avec_rendement]

    # Créer le graphique avec Plotly
    fig = go.Figure()

    # Ligne de rendement
    fig.add_trace(go.Scatter(
        x=dates,
        y=rendements,
        mode='lines+markers',
        name='Rendement',
        line=dict(color='#007bff', width=3),
        marker=dict(size=8)
    ))

    # Ligne de rendement moyen
    rendement_moyen = saison.get_rendement_moyen()
    if rendement_moyen:
        fig.add_trace(go.Scatter(
            x=[dates[0], dates[-1]],
            y=[rendement_moyen, rendement_moyen],
            mode='lines',
            name=f'Rendement moyen ({rendement_moyen:.2f}%)',
            line=dict(color='red', width=2, dash='dash')
        ))

    # Récupérer la configuration des échelles
    config = get_config()
    echelle = config.get_echelle_saison('rendement')
    params = config.get_parametres_graphiques()

    # Mise en forme
    fig.update_layout(
        title=f"Évolution du Rendement - Saison {saison.nom}",
        xaxis_title="Date",
        yaxis_title="Rendement (%)",
        hovermode='x unified',
        template='plotly_white',
        height=params.get('hauteur_graphique', 500),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # Appliquer les échelles configurées
    fig.update_yaxes(range=[echelle['y_min'], echelle['y_max']])

    return fig


def generer_graphique_rendement_saison(saison: Saison, output_path: Path) -> None:
    """
    Génère un graphique du rendement pour une saison.

    Args:
        saison: La saison à visualiser
        output_path: Chemin du fichier HTML de sortie
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure_rendement_saison(saison).write_html(output_path)


def figure_indicateurs_dju(saison: Saison) -> Optional[go.Figure]:
    """
    Construit les graphiques de consommation et de calories par DJU d'une saison.

    Contrairement au rendement, la consommation par DJU reste mesurable
    sans compteur calories.

    Returns:
        La figure, ou None si aucune période n'a d'indicateurs
    """
    releves = [r for r in saison.releves if r.conso_gaz_par_dju is not None]
    if not releves:
        return None

    dates = [r.date_releve for r in releves]
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Consommation de Gaz par DJU', 'Calories Produites par DJU'),
        vertical_spacing=0.15
    )
    fig.add_trace(go.Scatter(
        x=dates, y=[r.conso_gaz_par_dju for r in releves],
        mode='lines+markers', name='Conso/DJU',
        line=dict(color='#28a745', width=2), marker=dict(size=6)
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=dates, y=[r.calories_par_dju for r in releves],
        mode='lines+markers', name='Cal./DJU',
        line=dict(color='#ffc107', width=2), marker=dict(size=6)
    ), row=2, col=1)

    config = get_config()
    echelle_conso_dju = config.get_echelle_saison('conso_gaz_par_dju')
    echelle_cal_dju = config.get_echelle_saison('calories_par_dju')
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="m³/DJU", range=[echelle_conso_dju['y_min'], echelle_conso_dju['y_max']], row=1, col=1)
    fig.update_yaxes(title_text="Cal./DJU", range=[echelle_cal_dju['y_min'], echelle_cal_dju['y_max']], row=2, col=1)
    fig.update_layout(height=650, showlegend=False, template='plotly_white', hovermode='x unified')
    return fig


def figure_complete_saison(saison: Saison) -> go.Figure:
    """Construit les graphiques rendement, conso/DJU et cal./DJU d'une saison."""
    releves_avec_calculs = [r for r in saison.releves if r.rendement is not None]

    if not releves_avec_calculs:
        return figure_rendement_saison(saison)

    dates = [r.date_releve for r in releves_avec_calculs]

    # Créer des sous-graphiques
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=(
            'Rendement de la Chaudière',
            'Consommation de Gaz par DJU',
            'Calories Produites par DJU'
        ),
        vertical_spacing=0.1
    )

    # Graphique 1: Rendement
    rendements = [r.rendement for r in releves_avec_calculs]
    fig.add_trace(
        go.Scatter(
            x=dates, y=rendements,
            mode='lines+markers',
            name='Rendement',
            line=dict(color='#007bff', width=2),
            marker=dict(size=6)
        ),
        row=1, col=1
    )

    # Graphique 2: Consommation gaz par DJU
    conso_par_dju = [r.conso_gaz_par_dju for r in releves_avec_calculs]
    fig.add_trace(
        go.Scatter(
            x=dates, y=conso_par_dju,
            mode='lines+markers',
            name='Conso/DJU',
            line=dict(color='#28a745', width=2),
            marker=dict(size=6)
        ),
        row=2, col=1
    )

    # Graphique 3: Calories par DJU
    calories_par_dju = [r.calories_par_dju for r in releves_avec_calculs]
    fig.add_trace(
        go.Scatter(
            x=dates, y=calories_par_dju,
            mode='lines+markers',
            name='Cal./DJU',
            line=dict(color='#ffc107', width=2),
            marker=dict(size=6)
        ),
        row=3, col=1
    )

    # Récupérer la configuration des échelles
    config = get_config()
    echelle_rendement = config.get_echelle_saison('rendement')
    echelle_conso_dju = config.get_echelle_saison('conso_gaz_par_dju')
    echelle_cal_dju = config.get_echelle_saison('calories_par_dju')

    # Mise en forme
    fig.update_xaxes(title_text="Date", row=3, col=1)
    fig.update_yaxes(title_text="Rendement (%)", range=[echelle_rendement['y_min'], echelle_rendement['y_max']], row=1, col=1)
    fig.update_yaxes(title_text="m³/DJU", range=[echelle_conso_dju['y_min'], echelle_conso_dju['y_max']], row=2, col=1)
    fig.update_yaxes(title_text="Cal./DJU", range=[echelle_cal_dju['y_min'], echelle_cal_dju['y_max']], row=3, col=1)

    fig.update_layout(
        title_text=f"Indicateurs de Performance - Saison {saison.nom}",
        height=900,
        showlegend=False,
        template='plotly_white',
        hovermode='x unified'
    )

    return fig


def generer_graphique_complet_saison(saison: Saison, output_path: Path) -> None:
    """
    Génère un graphique complet avec plusieurs indicateurs pour une saison.

    Args:
        saison: La saison à visualiser
        output_path: Chemin du fichier HTML de sortie
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure_complete_saison(saison).write_html(output_path)


def figure_comparaison_saisons(saisons: List[Saison]) -> go.Figure:
    """Construit les graphiques en barres comparant les saisons."""
    comparaison = comparer_saisons(saisons)

    # Préparer les données
    noms = []
    conso_totales = []
    dju_totaux = []
    rendements_moyens = []
    conso_par_dju = []

    for nom_saison, stats in comparaison.items():
        noms.append(stats['nom'])
        conso_totales.append(stats['conso_totale_gaz'])
        dju_totaux.append(stats['dju_total'])
        rendements_moyens.append(stats['rendement_moyen'] if stats['rendement_moyen'] else 0)
        conso_par_dju.append(stats['conso_par_dju'])

    # Créer des sous-graphiques
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Rendement Moyen par Saison',
            'Consommation Totale de Gaz',
            'DJU Total par Saison',
            'Consommation par DJU'
        ),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "bar"}]]
    )

    # Graphique 1: Rendement moyen
    fig.add_trace(
        go.Bar(x=noms, y=rendements_moyens, name='Rendement Moyen',
               marker_color='#007bff'),
        row=1, col=1
    )

    # Graphique 2: Consommation totale
    fig.add_trace(
        go.Bar(x=noms, y=conso_totales, name='Conso Totale',
               marker_color='#28a745'),
        row=1, col=2
    )

    # Graphique 3: DJU total
    fig.add_trace(
        go.Bar(x=noms, y=dju_totaux, name='DJU Total',
               marker_color='#ffc107'),
        row=2, col=1
    )

    # Graphique 4: Consommation par DJU
    fig.add_trace(
        go.Bar(x=noms, y=conso_par_dju, name='Conso/DJU',
               marker_color='#dc3545'),
        row=2, col=2
    )

    # Récupérer la configuration des échelles
    config = get_config()
    echelle_rendement = config.get_echelle_comparaison('rendement_moyen')
    echelle_conso_totale = config.get_echelle_comparaison('conso_totale_gaz')
    echelle_conso_dju = config.get_echelle_comparaison('conso_par_dju')

    # Mise en forme
    fig.update_yaxes(title_text="Rendement (%)", range=[echelle_rendement['y_min'], echelle_rendement['y_max']], row=1, col=1)
    fig.update_yaxes(title_text="Gaz (m³)", range=[echelle_conso_totale['y_min'], echelle_conso_totale['y_max']], row=1, col=2)
    fig.update_yaxes(title_text="DJU", row=2, col=1)
    fig.update_yaxes(title_text="m³/DJU", range=[echelle_conso_dju['y_min'], echelle_conso_dju['y_max']], row=2, col=2)

    fig.update_layout(
        title_text="Comparaison des Saisons de Chauffe",
        height=800,
        showlegend=False,
        template='plotly_white'
    )

    return fig


def generer_graphique_comparaison_saisons(saisons: List[Saison], output_path: Path) -> None:
    """
    Génère un graphique comparant plusieurs saisons.

    Args:
        saisons: Liste des saisons à comparer
        output_path: Chemin du fichier HTML de sortie
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure_comparaison_saisons(saisons).write_html(output_path)


def figure_rendements_compares(saisons: List[Saison]) -> go.Figure:
    """Construit les courbes de rendement superposées de plusieurs saisons."""
    fig = go.Figure()

    colors = ['#007bff', '#28a745', '#ffc107', '#dc3545', '#6f42c1', '#fd7e14']

    for idx, saison in enumerate(saisons):
        releves_avec_rendement = [r for r in saison.releves if r.rendement is not None]

        if not releves_avec_rendement:
            continue

        # Utiliser un index relatif (numéro de relevé) plutôt que les dates
        # car les saisons ont des dates différentes
        indices = list(range(1, len(releves_avec_rendement) + 1))
        rendements = [r.rendement for r in releves_avec_rendement]

        color = colors[idx % len(colors)]

        fig.add_trace(go.Scatter(
            x=indices,
            y=rendements,
            mode='lines+markers',
            name=saison.nom,
            line=dict(width=2, color=color),
            marker=dict(size=6)
        ))

    # Récupérer la configuration des échelles
    config = get_config()
    echelle = config.get_echelle_saison('rendement')
    params = config.get_parametres_graphiques()

    fig.update_layout(
        title="Comparaison de l'Évolution des Rendements",
        xaxis_title="Numéro de Relevé",
        yaxis_title="Rendement (%)",
        hovermode='x unified',
        template='plotly_white',
        height=params.get('hauteur_graphique', 600),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )

    # Appliquer les échelles configurées
    fig.update_yaxes(range=[echelle['y_min'], echelle['y_max']])

    return fig


def generer_graphique_rendements_compares(saisons: List[Saison], output_path: Path) -> None:
    """
    Génère un graphique comparant l'évolution des rendements de plusieurs saisons.

    Args:
        saisons: Liste des saisons à comparer
        output_path: Chemin du fichier HTML de sortie
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure_rendements_compares(saisons).write_html(output_path)
