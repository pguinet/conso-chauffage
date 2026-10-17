# Application de Suivi de Consommation de Chaudière

## Contexte

Application pour suivre la consommation et le rendement d'une chaudière dans une copropriété.

### Fonctionnalités métier

- **Saisons de chauffe** : Une saison peut commencer dès le 1er septembre et se terminer le 30 juin de l'année suivante. Les dates de début et de fin ne sont pas fixées.
- **Relevés irréguliers** : À intervalles non réguliers, certaines données techniques sont relevées :
  - Date du relevé
  - Index compteur gaz
  - Index compteur calories
  - DJU (Degrés Jours Unifiés) sur la période concernée (Le Bourget)
- **Calculs automatiques** : À chaque relevé (sauf le premier de la saison), calcul de :
  - Consommation de gaz par DJU
  - Calories produites par DJU
  - Rendement de la chaudière

### Livrables

- Rapport (tableau) par saison reprenant les informations saisies et calculées
- Graphique du rendement par saison (tenant compte du caractère non régulier des saisies)
- Tableau et graphiques de comparaison entre saisons

### Contraintes techniques

- Exécution en local et via GitHub Actions
- Stockage des données en format texte simple (YAML)
- Interface web pour la saisie et la génération des documents

## Architecture Implémentée

### Stack Technique

- **Langage** : Python 3.9+
- **Framework Web** : Flask 3.0.0
- **Stockage** : YAML (PyYAML 6.0.1)
- **Graphiques** : Plotly 5.18.0
- **Serveur Production** : Gunicorn 21.2.0

### Structure du Projet

```
conso-chauffage/
├── data/
│   └── saisons.yaml              # Données stockées en YAML
├── src/
│   ├── models/
│   │   ├── saison.py            # Modèle Saison
│   │   └── releve.py            # Modèle Relevé
│   ├── calculs/
│   │   └── rendement.py         # Logique de calcul
│   ├── rapports/
│   │   ├── tableau.py           # Génération tableaux HTML/CSV
│   │   ├── graphiques.py        # Génération graphiques Plotly
│   │   └── site.py              # Site statique des rapports (navigation commune)
│   ├── web/
│   │   ├── app.py               # Application Flask
│   │   ├── templates/           # Templates HTML
│   │   │   ├── base.html
│   │   │   ├── index.html
│   │   │   ├── saison_detail.html
│   │   │   ├── nouvelle_saison.html
│   │   │   ├── nouveau_releve.html
│   │   │   └── comparaison.html
│   │   └── static/              # CSS/JS (inline dans templates)
│   └── data_manager.py          # Gestion stockage YAML
├── scripts/
│   └── generate_all_reports.py # Script CLI de génération
├── output/                      # Rapports générés
├── .github/workflows/
│   └── generate-reports.yml    # Workflow GitHub Actions
├── requirements.txt
├── README.md
└── CLAUDE.md
```

### Modules Principaux

#### 1. Modèles de Données (`src/models/`)

**`Releve`** (releve.py)
- Attributs : date, index_gaz, index_calories, dju
- Valeurs calculées (propriétés, jamais stockées) : conso_gaz, conso_gaz_par_dju, calories_produites, calories_par_dju, rendement
- Rendement `None` (non mesurable) si aucune calorie n'a été comptée sur la période (compteur absent ou période trop courte pour sa résolution de 1 MWh)
- Méthode `calculer_indicateurs()` : relie le relevé au précédent ; les indicateurs sont calculés à la volée
- Conversion dict/objet pour sérialisation YAML : seules les 4 données saisies sont écrites, les valeurs calculées d'anciens fichiers sont ignorées

**`Saison`** (saison.py)
- Attributs : nom, date_debut, date_fin, liste de relevés
- Méthode `ajouter_releve()` : insère un relevé à sa place chronologique (un relevé oublié peut être ajouté après coup)
- Méthode `get_duree_jours()` : durée de la saison (None si en cours)
- Méthodes statistiques : rendement_moyen, conso_totale, calories_totales, dju_total
- `get_rendement_moyen()` : moyenne pondérée par la consommation de gaz (Σ calories / Σ énergie gaz) sur les périodes mesurables
- Gestion saison en cours (date_fin = None)

#### 2. Moteur de Calculs (`src/calculs/`)

**Coefficients** (réglables dans `config/calculs.yaml`) :
- Gaz : `coefficient_kwh_par_m3` = coefficient de conversion de la facture (PCS × correction pression/température). Valeur actuelle : 13,7 kWh/m³, calculée avec la pression de comptage confirmée de 300 mbar (correction ≈ 1,222) et un PCS de 11,2 kWh/m³(n) (`a_confirmer: false`). Avec l'ancienne valeur de 10 kWh/m³, les rendements dépassaient 100 % (116 à 134 %) car le compteur de la chaufferie est sous pression
- Compteur calories : `kwh_par_unite` = 1000 (1 unité = 1 MWh)
- Tant que `a_confirmer` vaut `true`, les rapports et l'appli web affichent une mise en garde « Rendement indicatif » (les comparaisons entre saisons restent valables : le coefficient est un facteur commun)

**Fonctions** :
- `calculer_rendement()` : (calories / énergie_gaz) × 100
- `calculer_conso_par_dju()` : consommation / dju
- `calculer_calories_par_dju()` : calories / dju
- `comparer_saisons()` : statistiques comparatives
- `analyser_tendance_rendement()` : analyse min/max/moyenne/tendance

#### 3. Génération de Rapports (`src/rapports/`)

**Tableaux** (tableau.py)
- `generer_rapport_saison_csv()` : Export CSV avec délimiteur `;`
- `generer_rapport_saison_html()` : Rapport HTML stylisé avec statistiques
- `generer_rapport_comparaison_csv()` : Comparaison toutes saisons en CSV
- `generer_rapport_comparaison_html()` : Tableau comparatif HTML
- `html_stats_saison()`, `html_tableau_releves()`, `html_tableau_comparaison()` : fragments HTML partagés avec le site

**Graphiques** (graphiques.py)
- `generer_graphique_rendement_saison()` : Évolution du rendement avec moyenne
- `generer_graphique_complet_saison()` : 3 graphiques (rendement, conso/DJU, cal/DJU)
- `generer_graphique_comparaison_saisons()` : 4 graphiques comparatifs (bars)
- `generer_graphique_rendements_compares()` : Courbes de rendement superposées
- Fonctions `figure_*()` : construisent les figures, utilisées par les `generer_*()` (fichier autonome, appli web) et par le site
- `figure_indicateurs_dju()` : conso/DJU et cal./DJU, disponible même sans compteur calories

**Site statique** (site.py)
- `generer_site()` : `index.html` (une carte par saison), `saison_<nom>.html` (stats, graphiques, relevés, CSV, liens saison précédente/suivante), `comparaison.html` (tableau + graphiques), CSV
- Barre de navigation commune (Accueil, Comparaison, menu Saisons)
- `plotly.min.js` écrit une seule fois à côté des pages (site d'environ 4 Mo au lieu de 100 Mo)
- Supprime les fichiers de l'ancienne génération (`rapport_*.html`, `graphique_*.html`)

#### 4. Interface Web (`src/web/`)

**Application Flask** (app.py)

Routes principales :
- `/` : Liste des saisons
- `/saison/<nom>` : Détail d'une saison
- `/saison/nouvelle` : Formulaire création saison
- `/saison/<nom>/releve/nouveau` : Formulaire ajout relevé
- `/comparaison` : Page de comparaison
- `/rapports/saison/<nom>/html|csv` : Génération rapports
- `/graphiques/saison/<nom>/rendement|complet` : Génération graphiques
- `/init-exemple` : Création données d'exemple

Le fichier YAML est relu avant chaque requête (`before_request`) : les modifications faites hors de l'application ne sont jamais écrasées.

**Templates HTML**
- `base.html` : Template de base avec navigation et styles CSS
- `index.html` : Liste des saisons avec statistiques
- `saison_detail.html` : Détail saison avec tableau de relevés
- `nouvelle_saison.html` : Formulaire création saison
- `nouveau_releve.html` : Formulaire saisie relevé avec aide contextuelle
- `comparaison.html` : Page de comparaison inter-saisons

#### 5. Gestion des Données (`src/data_manager.py`)

**`DataManager`**
- `charger_donnees()` : Lecture du fichier YAML
- `sauvegarder_donnees()` : Écriture du fichier YAML
- `ajouter_saison()` : Ajout d'une saison
- `ajouter_releve_a_saison()` : Ajout d'un relevé
- `get_saison()` : Récupération par nom
- `get_saison_en_cours()` : Récupération saison active
- `creer_fichier_exemple()` : Génération de données de test

#### 6. Script CLI (`scripts/generate_all_reports.py`)

- Chargement des données depuis `data/saisons.yaml`
- Génération du site des rapports via `generer_site()` (point d'entrée : `output/index.html`)
- Affichage de la progression en console

#### 7. GitHub Actions (`.github/workflows/generate-reports.yml`)

**Déclencheurs** :
- Workflow manuel (`workflow_dispatch`)
- Push sur `master` modifiant `data/saisons.yaml` ou `config/`
- Planification mensuelle (1er du mois)

**Actions** :
- Installation Python et dépendances
- Génération des rapports via script CLI
- Upload des rapports comme artifacts (90 jours)
- Déploiement sur GitHub Pages, à la racine du site : https://pguinet.github.io/conso-chauffage/

### Format de Données (YAML)

```yaml
saisons:
  - nom: "2024-2025"
    date_debut: "2024-09-15"
    date_fin: null  # null si en cours
    releves:
      - date: "2024-09-15"
        index_gaz: 125430.0
        index_calories: 456780.0
        dju: 0.0  # Premier relevé = 0
      - date: "2024-10-20"
        index_gaz: 128950.0
        index_calories: 462340.0
        dju: 145.0
```

### Utilisation

**Installation et configuration de l'environnement virtuel Python** :
```bash
# Créer le venv (une seule fois)
python3 -m venv venv

# Activer le venv (à faire à chaque session)
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

**IMPORTANT pour Claude** : Toujours activer le venv Python avec `source venv/bin/activate` avant d'exécuter des commandes Python (scripts, Flask, etc.).

**Démarrage de l'interface web** :
```bash
source venv/bin/activate
python src/web/app.py
# Accès : http://localhost:5000
```

**Génération des rapports en CLI** :
```bash
source venv/bin/activate
python scripts/generate_all_reports.py
# Sortie : output/
```

## Récupération Automatique des DJU (✅ Implémenté)

### Service DJU Fetcher

**Module** : `src/services/dju_fetcher.py`

**Fonctionnalités** :
- Récupération automatique des températures via **Open-Meteo API** (gratuit, sans clé)
- Calcul des DJU à partir des températures moyennes journalières
- Formule : DJU = Σ (18°C - température_moyenne) pour chaque jour où temp < 18°C
- Période : du lendemain du dernier relevé au jour du relevé inclus
- Coordonnées Le Bourget : 48.9694°N, 2.4414°E

**API utilisée** : [Open-Meteo Archive API](https://archive-api.open-meteo.com)
- Données historiques depuis 1940
- Gratuit et sans limitation
- Pas de clé API requise

### Cache DJU

**Module** : `src/services/dju_cache.py`

**Fonctionnalités** :
- Stockage local des DJU dans `data/dju_cache.json`
- Évite les appels API répétés pour les mêmes périodes
- Clé de cache : `date_debut_date_fin_base_temp` (période réellement calculée)
- Statistiques du cache disponibles via API

### Intégration Interface Web

**Route API** : `POST /api/dju/calculate`

**Paramètres JSON** :
```json
{
  "date_dernier_releve": "2024-09-15",
  "date_releve": "2024-10-20",
  "base_temp": 18.0
}
```

La période de calcul va du **lendemain** du dernier relevé au jour du relevé inclus :
chaque jour n'est compté qu'une seule fois. Pour recalculer les DJU de tous les relevés
avec cette convention : `python scripts/recalculer_dju.py [--ecrire]`.

**Réponse** :
```json
{
  "success": true,
  "dju": 145.5,
  "source": "Open-Meteo API",
  "cached": false
}
```

**Interface utilisateur** :
- Bouton "🔄 Calculer automatiquement" dans le formulaire de relevé
- JavaScript asynchrone pour l'appel API
- Feedback visuel du statut (en cours, succès, erreur)
- Indication si la valeur provient du cache

### Configuration

**Fichier** : `.env` (optionnel)

```bash
METEO_API_KEY=         # Non requis pour Open-Meteo
METEO_STATION=Le Bourget
DJU_BASE_TEMP=18.0
```

### Extensions Possibles

- ✅ ~~Import automatique des DJU depuis API météo~~ (Implémenté)
- Ajout d'authentification utilisateur
- Export PDF des rapports
- API REST complète pour intégration externe
- Tableau de bord temps réel
- Alertes sur dégradation du rendement
- Support d'autres stations météo
- Configuration de la température de base par saison
