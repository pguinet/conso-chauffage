#!/usr/bin/env python3
"""Script pour générer tous les rapports et graphiques."""

from pathlib import Path
import sys

# Ajouter le répertoire parent au path pour pouvoir importer les modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_manager import DataManager
from src.rapports import (
    generer_rapport_saison_html,
    generer_rapport_saison_csv,
    generer_rapport_comparaison_html,
    generer_rapport_comparaison_csv,
    generer_graphique_rendement_saison,
    generer_graphique_complet_saison,
    generer_graphique_comparaison_saisons,
    generer_graphique_rendements_compares
)


def main():
    """Génère tous les rapports et graphiques."""
    print("=" * 60)
    print("Génération des rapports de consommation de chaudière")
    print("=" * 60)

    # Initialiser le gestionnaire de données
    base_dir = Path(__file__).parent.parent
    data_file = base_dir / 'data' / 'saisons.yaml'
    output_dir = base_dir / 'output'

    if not data_file.exists():
        print(f"❌ Fichier de données introuvable: {data_file}")
        print("Veuillez créer le fichier data/saisons.yaml avec vos données.")
        sys.exit(1)

    # Créer le répertoire de sortie
    output_dir.mkdir(exist_ok=True)

    # Charger les données
    print(f"\n📂 Chargement des données depuis {data_file}")
    data_manager = DataManager(data_file)
    saisons = data_manager.charger_donnees()

    if not saisons:
        print("❌ Aucune saison trouvée dans le fichier de données.")
        sys.exit(1)

    print(f"✅ {len(saisons)} saison(s) chargée(s)")

    # Générer les rapports pour chaque saison
    print("\n📊 Génération des rapports par saison...")
    for saison in saisons:
        print(f"\n  Saison: {saison.nom}")

        # Rapport HTML
        html_path = output_dir / f"rapport_{saison.nom}.html"
        generer_rapport_saison_html(saison, html_path)
        print(f"    ✅ Rapport HTML: {html_path.name}")

        # Rapport CSV
        csv_path = output_dir / f"rapport_{saison.nom}.csv"
        generer_rapport_saison_csv(saison, csv_path)
        print(f"    ✅ Rapport CSV: {csv_path.name}")

        # Graphiques (seulement si des relevés avec calculs existent)
        if len([r for r in saison.releves if r.rendement is not None]) > 0:
            # Graphique de rendement
            graph_rendement_path = output_dir / f"graphique_rendement_{saison.nom}.html"
            generer_graphique_rendement_saison(saison, graph_rendement_path)
            print(f"    ✅ Graphique rendement: {graph_rendement_path.name}")

            # Graphique complet
            graph_complet_path = output_dir / f"graphique_complet_{saison.nom}.html"
            generer_graphique_complet_saison(saison, graph_complet_path)
            print(f"    ✅ Graphique complet: {graph_complet_path.name}")
        else:
            print(f"    ⚠️  Pas assez de données pour générer les graphiques")

    # Générer les rapports de comparaison
    if len(saisons) > 1:
        print("\n📈 Génération des rapports de comparaison...")

        # Rapport de comparaison HTML
        comp_html_path = output_dir / "rapport_comparaison.html"
        generer_rapport_comparaison_html(saisons, comp_html_path)
        print(f"  ✅ Rapport comparaison HTML: {comp_html_path.name}")

        # Rapport de comparaison CSV
        comp_csv_path = output_dir / "rapport_comparaison.csv"
        generer_rapport_comparaison_csv(saisons, comp_csv_path)
        print(f"  ✅ Rapport comparaison CSV: {comp_csv_path.name}")

        # Graphique de comparaison
        graph_comp_path = output_dir / "graphique_comparaison.html"
        generer_graphique_comparaison_saisons(saisons, graph_comp_path)
        print(f"  ✅ Graphique comparaison: {graph_comp_path.name}")

        # Graphique des rendements comparés
        graph_rend_path = output_dir / "graphique_rendements_compares.html"
        generer_graphique_rendements_compares(saisons, graph_rend_path)
        print(f"  ✅ Graphique rendements comparés: {graph_rend_path.name}")
    else:
        print("\n⚠️  Une seule saison disponible, pas de comparaison possible")

    # Créer une page index.html
    print("\n📄 Génération de la page d'index...")
    index_path = output_dir / "index.html"
    generer_page_index(saisons, output_dir, index_path)
    print(f"  ✅ Page d'index: {index_path.name}")

    print("\n" + "=" * 60)
    print(f"✅ Tous les rapports ont été générés dans: {output_dir}")
    print("=" * 60)


def generer_page_index(saisons, output_dir, index_path):
    """Génère une page d'index HTML listant tous les rapports."""
    from datetime import datetime

    html = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapports Consommation Chaudière</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #007bff;
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
        }
        h2 {
            color: #333;
            margin-top: 30px;
        }
        .saison-section {
            margin: 20px 0;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 5px;
            border-left: 4px solid #007bff;
        }
        .links {
            margin: 10px 0;
        }
        a {
            display: inline-block;
            margin: 5px 10px 5px 0;
            padding: 8px 15px;
            background-color: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 4px;
        }
        a:hover {
            background-color: #0056b3;
        }
        .comparison-section {
            margin: 30px 0;
            padding: 20px;
            background-color: #e7f3ff;
            border-radius: 5px;
            border-left: 4px solid #28a745;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Rapports de Consommation de Chaudière</h1>
        <p>Rapports générés automatiquement pour le suivi de la consommation et du rendement de la chaudière.</p>

        <h2>Rapports par Saison</h2>
"""

    for saison in saisons:
        statut = "En cours" if saison.est_en_cours() else "Terminée"
        html += f"""
        <div class="saison-section">
            <h3>Saison {saison.nom} ({statut})</h3>
            <p><strong>Période:</strong> {saison.date_debut.strftime('%d/%m/%Y')}"""

        if saison.date_fin:
            html += f" - {saison.date_fin.strftime('%d/%m/%Y')}"

        html += f"""</p>
            <p><strong>Relevés:</strong> {len(saison.releves)}</p>
            <div class="links">
                <a href="rapport_{saison.nom}.html">Rapport HTML</a>
                <a href="rapport_{saison.nom}.csv">Télécharger CSV</a>
"""

        if len([r for r in saison.releves if r.rendement is not None]) > 0:
            html += f"""                <a href="graphique_rendement_{saison.nom}.html">Graphique Rendement</a>
                <a href="graphique_complet_{saison.nom}.html">Graphiques Complets</a>
"""

        html += """            </div>
        </div>
"""

    if len(saisons) > 1:
        html += """
        <div class="comparison-section">
            <h2>Comparaison des Saisons</h2>
            <p>Comparez les différentes saisons de chauffe entre elles.</p>
            <div class="links">
                <a href="rapport_comparaison.html">Rapport Comparaison HTML</a>
                <a href="rapport_comparaison.csv">Télécharger CSV Comparaison</a>
                <a href="graphique_comparaison.html">Graphiques de Comparaison</a>
                <a href="graphique_rendements_compares.html">Rendements Comparés</a>
            </div>
        </div>
"""

    html += f"""
        <div class="footer">
            <p>Rapports générés le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
        </div>
    </div>
</body>
</html>
"""

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)


if __name__ == '__main__':
    main()
