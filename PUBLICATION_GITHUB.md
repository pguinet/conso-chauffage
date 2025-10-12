# Guide de Publication sur GitHub

## Prérequis

1. **Compte GitHub** : Créez un compte sur https://github.com si ce n'est pas déjà fait
2. **Git installé** : Vérifiez avec `git --version`
   - Si non installé : `sudo zypper install git` (openSUSE) ou `sudo apt install git` (Ubuntu/Debian)
3. **Configuration Git** (première fois uniquement) :
   ```bash
   git config --global user.name "Votre Nom"
   git config --global user.email "votre.email@example.com"
   ```

## Étape 1 : Vérifier les fichiers à publier

### Fichiers qui SERONT publiés :
- ✅ Code source (`src/`)
- ✅ Scripts (`scripts/`, `run.py`, `start.sh`, etc.)
- ✅ Configuration (`config/graphiques.yaml`)
- ✅ Documentation (`README.md`, `CLAUDE.md`, etc.)
- ✅ Données d'exemple (`data/saisons.yaml`)
- ✅ Fichiers de configuration (`.env.example`, `requirements.txt`)

### Fichiers qui NE SERONT PAS publiés (grâce au .gitignore) :
- ❌ Environnement virtuel (`venv/`)
- ❌ Fichier `.env` (contient vos clés personnelles)
- ❌ Cache DJU (`data/dju_cache.json`)
- ❌ Rapports générés (`output/*.html`, `output/*.csv`)
- ❌ Fichiers Python compilés (`__pycache__/`, `*.pyc`)

## Étape 2 : Initialiser le dépôt Git

```bash
cd /home/pascal/github/conso-chauffage

# Initialiser Git
git init

# Vérifier le statut
git status
```

## Étape 3 : Créer le premier commit

```bash
# Ajouter tous les fichiers (sauf ceux dans .gitignore)
git add .

# Vérifier les fichiers ajoutés
git status

# Créer le commit initial
git commit -m "Initial commit: Application de suivi de consommation de chaudière

- Modèles de données (Saison, Releve)
- Calculs de rendement avec conversion MWh -> kWh
- Interface web Flask avec formulaires de saisie
- Récupération automatique des DJU via Open-Meteo API
- Génération de rapports HTML et CSV
- Graphiques interactifs avec échelles configurables
- Configuration des échelles dans config/graphiques.yaml
- Documentation complète"
```

## Étape 4 : Créer le dépôt sur GitHub

### Option A : Via l'interface web GitHub (recommandé)

1. Allez sur https://github.com
2. Cliquez sur le bouton **"+"** en haut à droite → **"New repository"**
3. Remplissez les informations :
   - **Repository name** : `conso-chauffage` (ou autre nom)
   - **Description** : "Application de suivi de consommation et rendement de chaudière de copropriété"
   - **Public** ou **Private** : Choisissez selon vos besoins
   - ⚠️ **NE PAS cocher** "Initialize with README" (nous avons déjà un README)
   - **NE PAS ajouter** .gitignore ou license (nous les avons déjà)
4. Cliquez sur **"Create repository"**

### Option B : Via GitHub CLI (si installé)

```bash
gh repo create conso-chauffage --public --source=. --remote=origin
```

## Étape 5 : Connecter et pousser le code

Après avoir créé le dépôt sur GitHub, vous verrez des instructions. Utilisez celles-ci :

```bash
# Ajouter l'origine distante (remplacez VOTRE_USERNAME)
git remote add origin https://github.com/VOTRE_USERNAME/conso-chauffage.git

# Renommer la branche en 'main' (standard GitHub)
git branch -M main

# Pousser le code sur GitHub
git push -u origin main
```

## Étape 6 : Vérifier la publication

1. Allez sur https://github.com/VOTRE_USERNAME/conso-chauffage
2. Vérifiez que tous les fichiers sont présents
3. Vérifiez que le README.md s'affiche correctement

## Configuration recommandée du dépôt GitHub

### Description

Ajoutez une description courte et des topics :

**Description** :
```
Application de suivi de consommation et rendement de chaudière de copropriété avec calculs DJU automatiques
```

**Topics** :
```
python flask plotly heating energy-efficiency dju building-management
```

### README Badges (optionnel)

Vous pouvez ajouter des badges en haut du README.md :

```markdown
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
```

## Mises à jour futures

Pour publier des modifications ultérieures :

```bash
# Vérifier les modifications
git status

# Ajouter les fichiers modifiés
git add .

# Créer un commit
git commit -m "Description des modifications"

# Pousser sur GitHub
git push
```

## Licence

Avant de publier, décidez de la licence :

### Option 1 : Projet privé / usage personnel
- Pas de licence nécessaire si le dépôt est privé

### Option 2 : Open Source (recommandé)
Créez un fichier `LICENSE` avec par exemple la licence MIT :

```bash
cat > LICENSE << 'EOFLIC'
MIT License

Copyright (c) 2025 [Votre Nom]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOFLIC
```

Puis ajoutez et commitez :
```bash
git add LICENSE
git commit -m "Add MIT License"
git push
```

## Sécurité : Vérifications finales

### ✅ Checklist avant publication

- [ ] Le fichier `.env` est bien dans `.gitignore` (ne contient pas de clés API)
- [ ] Aucun token, mot de passe ou clé API dans le code
- [ ] Les données sensibles sont dans `data/saisons.yaml` (peut contenir vos vraies données)
- [ ] Le dossier `venv/` est ignoré
- [ ] Les fichiers de cache sont ignorés

### ⚠️ Si vous ne voulez PAS publier vos vraies données

Si `data/saisons.yaml` contient vos vraies données de consommation et que vous préférez ne pas les rendre publiques :

**Option 1 : Données d'exemple**
```bash
# Renommer vos données
mv data/saisons.yaml data/saisons_perso.yaml

# Créer des données d'exemple
python << 'PYEOF'
import yaml
data = {
    'saisons': [
        {
            'nom': '2024-2025',
            'date_debut': '2024-09-15',
            'date_fin': None,
            'releves': [
                {
                    'date': '2024-09-15',
                    'index_gaz': 100000.0,
                    'index_calories': 1000.0,
                    'dju': 0.0,
                    'conso_gaz': None,
                    'conso_gaz_par_dju': None,
                    'calories_produites': None,
                    'calories_par_dju': None,
                    'rendement': None
                }
            ]
        }
    ]
}
with open('data/saisons.yaml', 'w') as f:
    yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
PYEOF

# Ajouter saisons_perso.yaml au .gitignore
echo "data/saisons_perso.yaml" >> .gitignore

git add .
git commit -m "Add example data instead of real data"
git push
```

**Option 2 : Ignorer le fichier de données**
```bash
# Ajouter data/saisons.yaml au .gitignore
echo "data/saisons.yaml" >> .gitignore

git rm --cached data/saisons.yaml
git commit -m "Remove real data from repository"
git push
```

## GitHub Actions (déjà configuré)

Le dépôt contient déjà un workflow GitHub Actions (`.github/workflows/generate-reports.yml`) qui :
- Génère automatiquement les rapports lors des modifications de `data/saisons.yaml`
- Peut être déclenché manuellement
- Sauvegarde les rapports comme artifacts

Pas de configuration supplémentaire nécessaire !

## Support et Contributions

Si vous rendez le projet public et souhaitez accepter des contributions :

1. Ajoutez un fichier `CONTRIBUTING.md`
2. Configurez les "Issues" dans les paramètres du dépôt
3. Créez des templates pour les issues et pull requests

## Ressources

- Documentation Git : https://git-scm.com/doc
- Documentation GitHub : https://docs.github.com
- Tutoriel Git en français : https://git-scm.com/book/fr/v2

## Problèmes courants

### Erreur "remote: Permission denied"
→ Vérifiez vos identifiants GitHub ou utilisez un Personal Access Token

### Erreur "failed to push some refs"
→ Faites d'abord `git pull origin main` puis `git push`

### Le dépôt est trop volumineux
→ Vérifiez que `venv/` et `output/` sont bien ignorés

## Prochaines étapes après publication

1. ⭐ Ajoutez une étoile à votre propre projet (pour le retrouver facilement)
2. 📝 Mettez à jour le README si nécessaire
3. 🏷️ Créez une release (v1.0.0) pour marquer la première version stable
4. 📢 Partagez le lien avec votre copropriété si approprié

---

**Besoin d'aide ?** Consultez la documentation GitHub ou demandez de l'assistance.
