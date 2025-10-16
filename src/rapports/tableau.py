"""Module de génération de rapports sous forme de tableaux."""

import csv
from pathlib import Path
from typing import List
from datetime import datetime
from src.models import Saison
from src.calculs import comparer_saisons


def generer_rapport_saison_csv(saison: Saison, output_path: Path) -> None:
    """
    Génère un rapport CSV pour une saison.

    Args:
        saison: La saison à exporter
        output_path: Chemin du fichier CSV de sortie
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')

        # En-tête
        writer.writerow([
            'Date',
            'Index Gaz (m³)',
            'Index Calories',
            'DJU',
            'Conso Gaz (m³)',
            'Conso Gaz/DJU',
            'Calories Produites',
            'Calories/DJU',
            'Rendement (%)'
        ])

        # Données
        for releve in saison.releves:
            writer.writerow([
                releve.date_releve.strftime('%Y-%m-%d'),
                f"{releve.index_gaz:.2f}",
                f"{releve.index_calories:.2f}",
                f"{releve.dju:.1f}",
                f"{releve.conso_gaz:.2f}" if releve.conso_gaz is not None else "",
                f"{releve.conso_gaz_par_dju:.4f}" if releve.conso_gaz_par_dju is not None else "",
                f"{releve.calories_produites:.2f}" if releve.calories_produites is not None else "",
                f"{releve.calories_par_dju:.4f}" if releve.calories_par_dju is not None else "",
                f"{releve.rendement:.2f}" if releve.rendement is not None else ""
            ])


def generer_rapport_saison_html(saison: Saison, output_path: Path) -> None:
    """
    Génère un rapport HTML pour une saison.

    Args:
        saison: La saison à exporter
        output_path: Chemin du fichier HTML de sortie
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Calcul des statistiques avec gestion des valeurs None
    conso_totale = saison.get_conso_totale_gaz()
    conso_totale_str = f"{conso_totale:.2f}" if conso_totale is not None else "-"

    calories_totales = saison.get_calories_totales()
    calories_totales_str = f"{calories_totales:.2f}" if calories_totales is not None else "-"

    dju_total = saison.get_dju_total()
    dju_total_str = f"{dju_total:.1f}" if dju_total is not None else "-"

    rendement_moyen = saison.get_rendement_moyen()
    rendement_moyen_str = f"{rendement_moyen:.2f}" if rendement_moyen is not None else "-"

    duree_jours = saison.get_duree_jours()
    duree_str = f"{duree_jours} jours" if duree_jours is not None else "En cours"

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport Saison {saison.nom}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
        }}
        .info {{
            background-color: #e7f3ff;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th {{
            background-color: #007bff;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .number {{
            text-align: right;
        }}
        .footer {{
            margin-top: 30px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-card {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #007bff;
        }}
        .stat-label {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }}
        .stat-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Rapport Saison {saison.nom}</h1>

        <div class="info">
            <p><strong>Période:</strong> Du {saison.date_debut.strftime('%d/%m/%Y')}
            {'au ' + saison.date_fin.strftime('%d/%m/%Y') if saison.date_fin else '(en cours)'}</p>
            <p><strong>Durée:</strong> {duree_str}</p>
            <p><strong>Nombre de relevés:</strong> {len(saison.releves)}</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-label">Consommation Totale Gaz</div>
                <div class="stat-value">{conso_totale_str} m³</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Calories Totales Produites</div>
                <div class="stat-value">{calories_totales_str}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">DJU Total</div>
                <div class="stat-value">{dju_total_str}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Rendement Moyen</div>
                <div class="stat-value">{rendement_moyen_str}%</div>
            </div>
        </div>

        <h2>Relevés Détaillés</h2>
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th class="number">Index Gaz (m³)</th>
                    <th class="number">Index Calories</th>
                    <th class="number">DJU</th>
                    <th class="number">Conso Gaz (m³)</th>
                    <th class="number">Conso/DJU</th>
                    <th class="number">Calories Prod.</th>
                    <th class="number">Cal./DJU</th>
                    <th class="number">Rendement (%)</th>
                </tr>
            </thead>
            <tbody>
"""

    for releve in saison.releves:
        # Gestion des valeurs None pour tous les champs
        date_str = releve.date_releve.strftime('%d/%m/%Y') if releve.date_releve else '-'
        index_gaz_str = f"{releve.index_gaz:.2f}" if releve.index_gaz is not None else '-'
        index_calories_str = f"{releve.index_calories:.2f}" if releve.index_calories is not None else '-'
        dju_str = f"{releve.dju:.1f}" if releve.dju is not None else '-'
        conso_gaz_str = f"{releve.conso_gaz:.2f}" if releve.conso_gaz is not None else '-'
        conso_par_dju_str = f"{releve.conso_gaz_par_dju:.4f}" if releve.conso_gaz_par_dju is not None else '-'
        cal_prod_str = f"{releve.calories_produites:.2f}" if releve.calories_produites is not None else '-'
        cal_par_dju_str = f"{releve.calories_par_dju:.4f}" if releve.calories_par_dju is not None else '-'
        rendement_str = f"{releve.rendement:.2f}" if releve.rendement is not None else '-'

        html += f"""                <tr>
                    <td>{date_str}</td>
                    <td class="number">{index_gaz_str}</td>
                    <td class="number">{index_calories_str}</td>
                    <td class="number">{dju_str}</td>
                    <td class="number">{conso_gaz_str}</td>
                    <td class="number">{conso_par_dju_str}</td>
                    <td class="number">{cal_prod_str}</td>
                    <td class="number">{cal_par_dju_str}</td>
                    <td class="number">{rendement_str}</td>
                </tr>
"""

    html += f"""            </tbody>
        </table>

        <div class="footer">
            <p>Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
        </div>
    </div>
</body>
</html>
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)


def generer_rapport_comparaison_csv(saisons: List[Saison], output_path: Path) -> None:
    """
    Génère un rapport CSV comparant plusieurs saisons.

    Args:
        saisons: Liste des saisons à comparer
        output_path: Chemin du fichier CSV de sortie
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    comparaison = comparer_saisons(saisons)

    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')

        # En-tête
        writer.writerow([
            'Saison',
            'Date Début',
            'Date Fin',
            'Durée (jours)',
            'Statut',
            'Nb Relevés',
            'Conso Totale Gaz (m³)',
            'Calories Totales',
            'DJU Total',
            'Conso/DJU',
            'Cal./DJU',
            'Rendement Moyen (%)',
            'Rendement Global (%)'
        ])

        # Données
        for nom_saison, stats in comparaison.items():
            writer.writerow([
                stats['nom'],
                stats['date_debut'].strftime('%Y-%m-%d'),
                stats['date_fin'].strftime('%Y-%m-%d') if stats['date_fin'] else 'En cours',
                stats['duree_jours'] if stats['duree_jours'] is not None else '',
                'En cours' if stats['en_cours'] else 'Terminée',
                stats['nombre_releves'],
                f"{stats['conso_totale_gaz']:.2f}",
                f"{stats['calories_totales']:.2f}",
                f"{stats['dju_total']:.1f}",
                f"{stats['conso_par_dju']:.4f}",
                f"{stats['calories_par_dju']:.4f}",
                f"{stats['rendement_moyen']:.2f}" if stats['rendement_moyen'] is not None else "",
                f"{stats['rendement_global']:.2f}" if stats['rendement_global'] is not None else ""
            ])


def generer_rapport_comparaison_html(saisons: List[Saison], output_path: Path) -> None:
    """
    Génère un rapport HTML comparant plusieurs saisons.

    Args:
        saisons: Liste des saisons à comparer
        output_path: Chemin du fichier HTML de sortie
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    comparaison = comparer_saisons(saisons)

    html = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comparaison des Saisons</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #28a745;
            padding-bottom: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th {
            background-color: #28a745;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }
        td {
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .number {
            text-align: right;
        }
        .en-cours {
            color: #28a745;
            font-weight: bold;
        }
        .terminee {
            color: #6c757d;
        }
        .footer {
            margin-top: 30px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Comparaison des Saisons de Chauffe</h1>

        <table>
            <thead>
                <tr>
                    <th>Saison</th>
                    <th>Période</th>
                    <th class="number">Durée (j)</th>
                    <th>Statut</th>
                    <th class="number">Relevés</th>
                    <th class="number">Conso Gaz (m³)</th>
                    <th class="number">DJU Total</th>
                    <th class="number">Conso/DJU</th>
                    <th class="number">Rendement Moyen</th>
                    <th class="number">Rendement Global</th>
                </tr>
            </thead>
            <tbody>
"""

    for nom_saison, stats in comparaison.items():
        statut_class = 'en-cours' if stats['en_cours'] else 'terminee'
        statut_text = 'En cours' if stats['en_cours'] else 'Terminée'
        periode = f"{stats['date_debut'].strftime('%d/%m/%Y')} - "
        periode += stats['date_fin'].strftime('%d/%m/%Y') if stats['date_fin'] else 'En cours'

        duree_str = str(stats['duree_jours']) if stats['duree_jours'] is not None else '-'
        rendement_moyen_str = f"{stats['rendement_moyen']:.2f}%" if stats['rendement_moyen'] is not None else '-'
        rendement_global_str = f"{stats['rendement_global']:.2f}%" if stats['rendement_global'] is not None else '-'

        html += f"""                <tr>
                    <td><strong>{stats['nom']}</strong></td>
                    <td>{periode}</td>
                    <td class="number">{duree_str}</td>
                    <td class="{statut_class}">{statut_text}</td>
                    <td class="number">{stats['nombre_releves']}</td>
                    <td class="number">{stats['conso_totale_gaz']:.2f}</td>
                    <td class="number">{stats['dju_total']:.1f}</td>
                    <td class="number">{stats['conso_par_dju']:.4f}</td>
                    <td class="number">{rendement_moyen_str}</td>
                    <td class="number">{rendement_global_str}</td>
                </tr>
"""

    html += f"""            </tbody>
        </table>

        <div class="footer">
            <p>Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
        </div>
    </div>
</body>
</html>
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
