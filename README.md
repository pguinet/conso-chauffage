# Application de Suivi de Consommation de Chaudière

Application Python pour suivre la consommation et le rendement d'une chaudière de copropriété sur plusieurs saisons de chauffe.

## Fonctionnalités

- **Gestion des saisons de chauffe** : Créez et gérez plusieurs saisons (ex: 2024-2025)
- **Relevés de données** : Enregistrez les index de gaz, calories produites et DJU (Degrés Jours Unifiés)
- **Récupération automatique des DJU** : Calcul automatique via l'API Open-Meteo (gratuit, sans clé)
- **Calculs automatiques** :
  - Consommation de gaz par DJU
  - Calories produites par DJU
  - Rendement de la chaudière
- **Rapports détaillés** : Génération de rapports HTML et CSV par saison
- **Graphiques interactifs** : Visualisation de l'évolution du rendement et des indicateurs
- **Comparaison inter-saisons** : Comparez les performances entre différentes saisons
- **Cache intelligent** : Mise en cache des DJU pour limiter les appels API

## Architecture

```
conso-chauffage/
├── data/
│   ├── saisons.yaml              # Données stockées en YAML
│   └── dju_cache.json            # Cache des DJU (auto-généré)
├── src/
│   ├── models/                   # Modèles de données (Saison, Releve)
│   ├── calculs/                  # Moteur de calcul du rendement
│   ├── rapports/                 # Génération de rapports et graphiques
│   ├── services/                 # Services (DJU fetcher, cache)
│   │   ├── dju_fetcher.py
│   │   └── dju_cache.py
│   ├── web/                      # Application web Flask
│   │   ├── app.py
│   │   └── templates/
│   └── data_manager.py           # Gestion du stockage YAML
├── scripts/
│   └── generate_all_reports.py  # Script de génération des rapports
├── output/                       # Rapports générés
├── .github/workflows/            # GitHub Actions
├── .env.example                  # Exemple de configuration
└── requirements.txt
```

## Installation

### Prérequis

- Python 3.9 ou supérieur
- pip
- venv (inclus avec Python)

### Installation Rapide

**⚠️ Important :** Utilisez un environnement virtuel pour éviter les conflits avec les paquets système.

```bash
# 1. Créer l'environnement virtuel
python -m venv venv

# 2. Activer l'environnement virtuel
source venv/bin/activate  # Linux/macOS
# OU
venv\Scripts\activate     # Windows

# 3. Installer les dépendances
pip install -r requirements.txt
```

**📚 Documentation :**
- **[DEMARRAGE_RAPIDE.md](DEMARRAGE_RAPIDE.md)** : Guide ultra-simplifié en 3 étapes
- **[INSTALL.md](INSTALL.md)** : Guide détaillé avec dépannage
- **[CORRECTIONS.md](CORRECTIONS.md)** : Liste des corrections apportées
- **[LISEZMOI.txt](LISEZMOI.txt)** : Aide rapide format texte

## Utilisation

### Démarrage Rapide

**Méthode 1 : Script automatique (recommandé)**

Sur Linux/macOS :
```bash
./start.sh
```

Sur Windows :
```bash
start.bat
```

Le script gère automatiquement :
- Création du venv si nécessaire
- Activation du venv
- Installation des dépendances
- Lancement de l'application

**Méthode 2 : Avec run.py**

```bash
# 1. Activer l'environnement virtuel
source venv/bin/activate  # Linux/macOS
# ou venv\Scripts\activate sur Windows

# 2. Lancer avec run.py (depuis la racine)
python run.py
```

**Méthode 3 : Manuel (développeurs)**

```bash
# 1. Activer l'environnement virtuel
source venv/bin/activate

# 2. Définir PYTHONPATH et lancer
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python src/web/app.py
```

Ouvrez votre navigateur à l'adresse : **http://localhost:5000**

**Fonctionnalités :**
- ✅ Création de nouvelles saisons
- ✅ Ajout de relevés avec calcul automatique des DJU
- ✅ Visualisation des données
- ✅ Génération de rapports HTML et CSV
- ✅ Graphiques interactifs

### Génération de rapports en ligne de commande

Pour générer tous les rapports automatiquement :

```bash
# Activer l'environnement virtuel si ce n'est pas déjà fait
source venv/bin/activate  # Linux/macOS
# ou venv\Scripts\activate sur Windows

# Générer les rapports
python scripts/generate_all_reports.py
```

Les rapports seront générés dans le dossier `output/`.

### Désactiver l'environnement virtuel

Quand vous avez terminé :

```bash
deactivate
```

### 3. Initialisation avec des données d'exemple

Si vous démarrez sans données, vous pouvez :
- Utiliser le bouton "Créer des Données d'Exemple" dans l'interface web
- Ou créer manuellement le fichier `data/saisons.yaml`

## Format des données (YAML)

Les données sont stockées dans `data/saisons.yaml` :

```yaml
saisons:
  - nom: "2024-2025"
    date_debut: "2024-09-15"
    date_fin: null  # null si saison en cours
    releves:
      - date: "2024-09-15"
        index_gaz: 125430.0
        index_calories: 456780.0
        dju: 0.0  # 0 pour le premier relevé
      - date: "2024-10-20"
        index_gaz: 128950.0
        index_calories: 462340.0
        dju: 145.0
```

## Calculs effectués

### Rendement de la chaudière
```
Rendement (%) = (Calories produites / Énergie gaz consommée) × 100
```

Avec :
- 1 m³ de gaz ≈ 10 kWh
- 1 unité compteur calories ≈ 1 kWh

### Consommation par DJU
```
Conso/DJU = (Index gaz actuel - Index gaz précédent) / DJU période
```

### Calories par DJU
```
Cal./DJU = (Index calories actuel - Index calories précédent) / DJU période
```

## GitHub Actions

L'application inclut un workflow GitHub Actions (`.github/workflows/generate-reports.yml`) qui :
- Se déclenche manuellement ou automatiquement lors de modifications du fichier de données
- Génère tous les rapports
- Les stocke comme artifacts (disponibles pendant 90 jours)
- (Optionnel) Les publie sur GitHub Pages

## DJU (Degrés Jours Unifiés)

Les DJU mesurent la rigueur de l'hiver et permettent de normaliser les consommations.

### Récupération Automatique

L'application intègre un système de récupération automatique des DJU via **Open-Meteo API** :

**Fonctionnalités :**
- ✅ **Gratuit et sans clé API**
- ✅ **Calcul automatique** depuis le dernier relevé
- ✅ **Cache intelligent** pour limiter les appels API
- ✅ **Données historiques** disponibles depuis 1940

**Utilisation :**
1. Dans le formulaire d'ajout de relevé, saisissez la date du relevé
2. Cliquez sur "🔄 Calculer automatiquement"
3. Les DJU sont récupérés et remplis automatiquement

**Source des données :** Open-Meteo (station Le Bourget - 48.9694°N, 2.4414°E)

### Saisie Manuelle

Vous pouvez aussi saisir manuellement les DJU depuis :
- Météo France
- Sites spécialisés en performance énergétique
- infoclimat.fr

**Convention :** Le premier relevé d'une saison a toujours DJU = 0 (relevé de référence).

### Configuration (Optionnel)

L'application fonctionne directement sans configuration. Si vous souhaitez personnaliser certains paramètres, créez un fichier `.env` :

```bash
cp .env.example .env
```

**Variables disponibles :**
- `METEO_STATION` : Nom de la station (défaut: Le Bourget)
- `DJU_BASE_TEMP` : Température de base pour le calcul des DJU (défaut: 18.0°C)

**Source des données météo :** Open-Meteo API (gratuit, sans clé API requise)

## Exemples de rapports générés

- `rapport_2024-2025.html` : Rapport détaillé d'une saison
- `rapport_2024-2025.csv` : Données exportables
- `graphique_rendement_2024-2025.html` : Évolution du rendement
- `graphique_complet_2024-2025.html` : Tous les indicateurs
- `rapport_comparaison.html` : Comparaison de toutes les saisons
- `graphique_comparaison.html` : Graphiques comparatifs
- `graphique_rendements_compares.html` : Évolution des rendements comparés

## Développement

### Structure des modules

- **models/** : Classes `Saison` et `Releve`
- **calculs/** : Fonctions de calcul du rendement et des indicateurs
- **rapports/** : Génération de tableaux (HTML/CSV) et graphiques (Plotly)
- **services/** : Services externes (DJU fetcher avec Open-Meteo, cache)
- **web/** : Application Flask avec templates HTML
- **data_manager.py** : Gestion du stockage et chargement YAML

### API Endpoints

L'application expose une API REST pour le calcul des DJU :

**POST `/api/dju/calculate`**
```json
{
  "date_debut": "2024-09-15",
  "date_fin": "2024-10-20",
  "base_temp": 18.0
}
```

Réponse :
```json
{
  "success": true,
  "dju": 145.5,
  "source": "Open-Meteo API",
  "cached": false
}
```

**GET `/api/dju/cache/stats`**

Retourne les statistiques du cache DJU

### Ajouter de nouvelles fonctionnalités

1. Modifiez les modèles dans `src/models/`
2. Ajoutez les calculs dans `src/calculs/`
3. Créez les générateurs de rapports dans `src/rapports/`
4. Mettez à jour l'interface web dans `src/web/`

## Licence

Ce projet est libre d'utilisation pour le suivi de consommation de chaudière en copropriété.

## Support

Pour toute question ou problème, veuillez créer une issue sur le dépôt GitHub.
