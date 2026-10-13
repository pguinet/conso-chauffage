# Configuration

Ce dossier contient les fichiers de configuration de l'application.

## Fichier `calculs.yaml`

Paramètres du calcul du rendement :

```yaml
gaz:
  coefficient_kwh_par_m3: 13.5   # coefficient de conversion de la facture de gaz (kWh/m³)
  a_confirmer: true              # mise en garde dans les rapports tant que non vérifié
compteur_calories:
  kwh_par_unite: 1000.0          # 1 unité du compteur = 1 MWh
```

Le coefficient de conversion figure sur les factures de gaz (« coefficient de
conversion » ou « coefficient thermique »). Il combine le PCS du gaz et la
correction de pression et de température du compteur. Une fois la valeur
reportée, passer `a_confirmer` à `false`.


## Fichier `graphiques.yaml`

Ce fichier permet de configurer les échelles des axes Y pour tous les graphiques de l'application.

### Structure du fichier

```yaml
echelles_comparaison:
  # Configuration des graphiques de comparaison entre saisons
  rendement_moyen:
    y_min: 70      # Valeur minimale de l'axe Y
    y_max: null     # Valeur maximale (null = automatique)
    
  conso_totale_gaz:
    y_min: 30000
    y_max: null
    
  conso_par_dju:
    y_min: 15
    y_max: null

echelles_saison:
  # Configuration des graphiques d'évolution par saison
  rendement:
    y_min: 60
    y_max: null
    
  conso_gaz_par_dju:
    y_min: 10
    y_max: null

parametres:
  show_grid: true
  hauteur_graphique: 500
  palette: "Plotly"
```

### Métriques disponibles

#### Graphiques de comparaison (`echelles_comparaison`)

- **`rendement_moyen`** : Rendement moyen par saison (%)
- **`conso_totale_gaz`** : Consommation totale de gaz par saison (m³)
- **`conso_par_dju`** : Consommation par DJU (m³/DJU)
- **`calories_par_dju`** : Calories par DJU (MWh/DJU)

#### Graphiques d'évolution par saison (`echelles_saison`)

- **`rendement`** : Rendement par relevé (%)
- **`conso_gaz_par_dju`** : Consommation par DJU par relevé (m³/DJU)
- **`calories_par_dju`** : Calories par DJU par relevé (MWh/DJU)

### Paramètres

- **`y_min`** : Valeur minimale de l'axe Y
  - Si définie, l'axe Y commencera à cette valeur au lieu de 0
  - Utile pour mieux visualiser les variations quand les valeurs absolues sont élevées
  
- **`y_max`** : Valeur maximale de l'axe Y
  - Si `null`, la valeur maximale sera calculée automatiquement
  - Si définie, l'axe Y s'arrêtera à cette valeur

- **`show_grid`** : Afficher la grille sur les graphiques (true/false)

- **`hauteur_graphique`** : Hauteur des graphiques en pixels

- **`palette`** : Palette de couleurs (ex: "Plotly", "Viridis", etc.)

### Exemples d'utilisation

#### Exemple 1 : Zoom sur les rendements

Si vos rendements varient entre 110% et 140%, vous pouvez configurer :

```yaml
echelles_comparaison:
  rendement_moyen:
    y_min: 100
    y_max: 150
```

Cela permet de mieux voir les variations entre saisons au lieu d'avoir un graphique écrasé.

#### Exemple 2 : Visualiser les variations de consommation

Si votre consommation totale varie entre 40000 et 60000 m³ :

```yaml
echelles_comparaison:
  conso_totale_gaz:
    y_min: 30000
    y_max: 70000
```

#### Exemple 3 : Valeurs par défaut (automatique)

Pour revenir au comportement par défaut (axe Y commençant à 0) :

```yaml
echelles_comparaison:
  rendement_moyen:
    y_min: 0
    y_max: null
```

### Modification et application

1. Modifiez le fichier `config/graphiques.yaml`
2. Les modifications seront appliquées automatiquement à la prochaine génération de graphiques
3. Pas besoin de redémarrer l'application web

### Valeurs recommandées

D'après vos données actuelles :

| Métrique | y_min recommandé | Raison |
|----------|------------------|--------|
| `rendement_moyen` | 100 | Vos rendements sont entre 110-140% |
| `conso_totale_gaz` | 30000 | Vos consos sont > 40000 m³ |
| `conso_par_dju` | 15 | Vos valeurs sont entre 17-23 m³/DJU |
| `rendement` (saison) | 80 | Vos rendements relevé sont entre 96-180% |
| `conso_gaz_par_dju` (saison) | 10 | Vos valeurs relevé sont entre 11-55 m³/DJU |

Ces valeurs permettent de mieux visualiser les variations tout en gardant suffisamment d'espace pour les valeurs extrêmes.
