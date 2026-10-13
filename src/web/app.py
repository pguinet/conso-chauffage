"""Application web Flask pour la saisie et la visualisation des données."""

import sys
from pathlib import Path
from datetime import date, datetime
import os
import logging
from dotenv import load_dotenv

# Ajouter le répertoire parent au PYTHONPATH
BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

# Charger les variables d'environnement depuis .env
load_dotenv(BASE_DIR / '.env')

from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from src.data_manager import DataManager
from src.models import Saison, Releve
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
from src.services import DJUFetcher, DJUCache

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'conso-chauffage-secret-key-2024'

# Initialiser le gestionnaire de données (BASE_DIR déjà défini plus haut)
data_manager = DataManager(BASE_DIR / 'data' / 'saisons.yaml')

# Initialiser le service DJU
dju_cache = DJUCache(BASE_DIR / 'data' / 'dju_cache.json')
dju_fetcher = DJUFetcher(
    api_key=os.getenv('METEO_API_KEY'),
    station=os.getenv('METEO_STATION', 'Le Bourget')
)


@app.before_request
def recharger_donnees():
    """
    Relit le fichier YAML à chaque requête.

    Évite d'afficher des données périmées et, surtout, d'écraser à la
    prochaine sauvegarde les modifications faites hors de l'application.
    """
    data_manager.charger_donnees()


# Context processor pour rendre la date disponible dans tous les templates
@app.context_processor
def inject_now():
    """Injecte la date/heure actuelle dans tous les templates."""
    return {'now': datetime.now()}


@app.route('/')
def index():
    """Page d'accueil avec liste des saisons."""
    saisons = data_manager.get_toutes_saisons()
    return render_template('index.html', saisons=saisons)


@app.route('/saison/<nom>')
def saison_detail(nom):
    """Page de détail d'une saison."""
    saison = data_manager.get_saison(nom)
    if not saison:
        flash(f"Saison '{nom}' introuvable", 'error')
        return redirect(url_for('index'))
    return render_template('saison_detail.html', saison=saison)


@app.route('/saison/nouvelle', methods=['GET', 'POST'])
def nouvelle_saison():
    """Création d'une nouvelle saison."""
    if request.method == 'POST':
        nom = request.form['nom']
        date_debut_str = request.form['date_debut']

        # Vérifier si la saison existe déjà
        if data_manager.get_saison(nom):
            flash(f"Une saison '{nom}' existe déjà", 'error')
            return redirect(url_for('nouvelle_saison'))

        date_debut = datetime.strptime(date_debut_str, '%Y-%m-%d').date()

        saison = Saison(nom=nom, date_debut=date_debut)
        data_manager.ajouter_saison(saison)

        flash(f"Saison '{nom}' créée avec succès", 'success')
        return redirect(url_for('saison_detail', nom=nom))

    return render_template('nouvelle_saison.html')


@app.route('/saison/<nom>/terminer', methods=['POST'])
def terminer_saison(nom):
    """Terminer une saison en cours."""
    saison = data_manager.get_saison(nom)
    if not saison:
        flash(f"Saison '{nom}' introuvable", 'error')
        return redirect(url_for('index'))

    date_fin_str = request.form.get('date_fin')
    if date_fin_str:
        saison.date_fin = datetime.strptime(date_fin_str, '%Y-%m-%d').date()
        data_manager.sauvegarder_donnees()
        flash(f"Saison '{nom}' terminée", 'success')
    else:
        flash("Date de fin manquante", 'error')

    return redirect(url_for('saison_detail', nom=nom))


@app.route('/saison/<nom>/releve/nouveau', methods=['GET', 'POST'])
def nouveau_releve(nom):
    """Ajout d'un nouveau relevé à une saison."""
    saison = data_manager.get_saison(nom)
    if not saison:
        flash(f"Saison '{nom}' introuvable", 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        date_releve_str = request.form['date_releve']
        index_gaz = float(request.form['index_gaz'])
        index_calories = float(request.form['index_calories'])
        dju = float(request.form['dju'])

        date_releve = datetime.strptime(date_releve_str, '%Y-%m-%d').date()

        releve = Releve(
            date_releve=date_releve,
            index_gaz=index_gaz,
            index_calories=index_calories,
            dju=dju
        )

        data_manager.ajouter_releve_a_saison(nom, releve)

        flash('Relevé ajouté avec succès', 'success')
        return redirect(url_for('saison_detail', nom=nom))

    return render_template('nouveau_releve.html', saison=saison)


@app.route('/comparaison')
def comparaison():
    """Page de comparaison des saisons."""
    saisons = data_manager.get_toutes_saisons()
    return render_template('comparaison.html', saisons=saisons)


@app.route('/rapports/saison/<nom>/html')
def rapport_saison_html(nom):
    """Génère et affiche le rapport HTML d'une saison."""
    saison = data_manager.get_saison(nom)
    if not saison:
        flash(f"Saison '{nom}' introuvable", 'error')
        return redirect(url_for('index'))

    output_dir = BASE_DIR / 'output'
    output_path = output_dir / f'rapport_{nom}.html'
    generer_rapport_saison_html(saison, output_path)

    return send_file(output_path, mimetype='text/html')


@app.route('/rapports/saison/<nom>/csv')
def rapport_saison_csv(nom):
    """Génère et télécharge le rapport CSV d'une saison."""
    saison = data_manager.get_saison(nom)
    if not saison:
        flash(f"Saison '{nom}' introuvable", 'error')
        return redirect(url_for('index'))

    output_dir = BASE_DIR / 'output'
    output_path = output_dir / f'rapport_{nom}.csv'
    generer_rapport_saison_csv(saison, output_path)

    return send_file(output_path, as_attachment=True, download_name=f'rapport_{nom}.csv')


@app.route('/graphiques/saison/<nom>/rendement')
def graphique_rendement(nom):
    """Génère et affiche le graphique de rendement d'une saison."""
    saison = data_manager.get_saison(nom)
    if not saison:
        flash(f"Saison '{nom}' introuvable", 'error')
        return redirect(url_for('index'))

    output_dir = BASE_DIR / 'output'
    output_path = output_dir / f'graphique_rendement_{nom}.html'
    generer_graphique_rendement_saison(saison, output_path)

    return send_file(output_path, mimetype='text/html')


@app.route('/graphiques/saison/<nom>/complet')
def graphique_complet(nom):
    """Génère et affiche le graphique complet d'une saison."""
    saison = data_manager.get_saison(nom)
    if not saison:
        flash(f"Saison '{nom}' introuvable", 'error')
        return redirect(url_for('index'))

    output_dir = BASE_DIR / 'output'
    output_path = output_dir / f'graphique_complet_{nom}.html'
    generer_graphique_complet_saison(saison, output_path)

    return send_file(output_path, mimetype='text/html')


@app.route('/rapports/comparaison/html')
def rapport_comparaison_html():
    """Génère et affiche le rapport de comparaison HTML."""
    saisons = data_manager.get_toutes_saisons()
    if not saisons:
        flash("Aucune saison disponible", 'error')
        return redirect(url_for('index'))

    output_dir = BASE_DIR / 'output'
    output_path = output_dir / 'rapport_comparaison.html'
    generer_rapport_comparaison_html(saisons, output_path)

    return send_file(output_path, mimetype='text/html')


@app.route('/graphiques/comparaison')
def graphique_comparaison():
    """Génère et affiche le graphique de comparaison des saisons."""
    saisons = data_manager.get_toutes_saisons()
    if not saisons:
        flash("Aucune saison disponible", 'error')
        return redirect(url_for('index'))

    output_dir = BASE_DIR / 'output'
    output_path = output_dir / 'graphique_comparaison.html'
    generer_graphique_comparaison_saisons(saisons, output_path)

    return send_file(output_path, mimetype='text/html')


@app.route('/graphiques/comparaison/rendements')
def graphique_rendements_compares():
    """Génère et affiche le graphique des rendements comparés."""
    saisons = data_manager.get_toutes_saisons()
    if not saisons:
        flash("Aucune saison disponible", 'error')
        return redirect(url_for('index'))

    output_dir = BASE_DIR / 'output'
    output_path = output_dir / 'graphique_rendements_compares.html'
    generer_graphique_rendements_compares(saisons, output_path)

    return send_file(output_path, mimetype='text/html')


@app.route('/init-exemple')
def init_exemple():
    """Initialise des données d'exemple."""
    data_manager.creer_fichier_exemple()
    data_manager.charger_donnees()
    flash("Données d'exemple créées avec succès", 'success')
    return redirect(url_for('index'))


@app.route('/api/dju/calculate', methods=['POST'])
def calculate_dju():
    """
    Calcule automatiquement les DJU depuis le dernier relevé.

    La période va du lendemain du dernier relevé au jour du nouveau relevé
    inclus, pour ne pas compter deux fois le jour du dernier relevé.

    Paramètres JSON attendus:
    - date_dernier_releve: Date du dernier relevé (ISO format)
    - date_releve: Date du nouveau relevé (ISO format)
    - base_temp: Température de base (optionnel, défaut: 18.0)

    Returns:
        JSON avec {dju: float, source: str, cached: bool}
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'error': 'Données JSON manquantes',
                'success': False
            }), 400

        # Récupérer les paramètres
        date_dernier_str = data.get('date_dernier_releve')
        date_releve_str = data.get('date_releve')
        base_temp = float(data.get('base_temp', 18.0))

        if not date_dernier_str or not date_releve_str:
            return jsonify({
                'error': 'date_dernier_releve et date_releve sont requis',
                'success': False
            }), 400

        # Convertir les dates
        date_dernier = datetime.strptime(date_dernier_str, '%Y-%m-%d').date()
        date_fin = datetime.strptime(date_releve_str, '%Y-%m-%d').date()

        if date_fin <= date_dernier:
            return jsonify({
                'error': 'La date du relevé doit être postérieure au dernier relevé',
                'success': False
            }), 400

        date_debut = DJUFetcher.debut_periode(date_dernier)
        date_debut_str = date_debut.isoformat()
        date_fin_str = date_fin.isoformat()

        logger.info(f"Calcul DJU demandé pour {date_debut} à {date_fin}")

        # Vérifier d'abord le cache
        dju_cached = dju_cache.get(date_debut, date_fin, base_temp)

        if dju_cached is not None:
            logger.info(f"DJU trouvé en cache: {dju_cached}")
            return jsonify({
                'success': True,
                'dju': dju_cached,
                'date_debut': date_debut_str,
                'date_fin': date_fin_str,
                'base_temp': base_temp,
                'cached': True,
                'source': 'cache'
            })

        # Pas en cache, faire le fetch
        dju = dju_fetcher.get_dju_period(date_debut, date_fin, base_temp)

        if dju is None:
            return jsonify({
                'error': 'Impossible de récupérer les DJU. Vérifiez les dates et la connexion internet.',
                'success': False,
                'cached': False
            }), 500

        # Mettre en cache
        dju_cache.set(date_debut, date_fin, dju, base_temp)

        logger.info(f"DJU calculé: {dju}")

        return jsonify({
            'success': True,
            'dju': dju,
            'date_debut': date_debut_str,
            'date_fin': date_fin_str,
            'base_temp': base_temp,
            'cached': False,
            'source': 'Open-Meteo API'
        })

    except ValueError as e:
        logger.error(f"Erreur de validation: {e}")
        return jsonify({
            'error': f'Erreur de validation: {str(e)}',
            'success': False
        }), 400
    except Exception as e:
        logger.error(f"Erreur lors du calcul des DJU: {e}")
        return jsonify({
            'error': f'Erreur serveur: {str(e)}',
            'success': False
        }), 500


@app.route('/api/dju/cache/stats')
def dju_cache_stats():
    """Retourne des statistiques sur le cache DJU."""
    stats = dju_cache.get_cache_stats()
    return jsonify(stats)


if __name__ == '__main__':
    # Charger les données au démarrage
    data_manager.charger_donnees()
    app.run(debug=True, host='0.0.0.0', port=5000)
