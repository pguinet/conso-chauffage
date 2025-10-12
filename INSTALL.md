# Guide d'Installation Détaillé

Ce guide vous aide à installer et configurer l'application de suivi de consommation de chaudière.

## Problème : "externally-managed-environment"

Si vous rencontrez cette erreur lors de l'installation :
```
error: externally-managed-environment
```

C'est normal sur les distributions Linux modernes (Debian 12+, Ubuntu 23.04+, Fedora 38+, etc.).
La solution recommandée est d'utiliser un **environnement virtuel Python (venv)**.

## Solution : Installation avec venv

### Étape 1 : Cloner ou télécharger le projet

```bash
cd ~/github
git clone <votre-repo>
cd conso-chauffage
```

### Étape 2 : Créer l'environnement virtuel

```bash
python -m venv venv
```

Ou si vous avez plusieurs versions de Python :
```bash
python3 -m venv venv
```

Cela crée un dossier `venv/` dans votre projet (qui est ignoré par git).

### Étape 3 : Activer l'environnement virtuel

**Sur Linux/macOS :**
```bash
source venv/bin/activate
```

**Sur Windows (PowerShell) :**
```bash
venv\Scripts\Activate.ps1
```

**Sur Windows (CMD) :**
```bash
venv\Scripts\activate.bat
```

Vous devriez voir `(venv)` apparaître au début de votre ligne de commande :
```bash
(venv) pascal@machine:~/github/conso-chauffage$
```

### Étape 4 : Installer les dépendances

```bash
pip install -r requirements.txt
```

### Étape 5 : Vérifier l'installation

```bash
pip list
```

Vous devriez voir :
- Flask
- PyYAML
- plotly
- requests
- python-dotenv
- gunicorn

## Utilisation

### Lancer l'application web

**Option 1 : Script automatique (recommandé)**
```bash
./start.sh  # Linux/macOS
# ou start.bat sur Windows
```

**Option 2 : Avec run.py**
```bash
# 1. Activer l'environnement
source venv/bin/activate

# 2. Lancer l'application
python run.py
```

**Option 3 : Manuel**
```bash
# 1. Activer l'environnement
source venv/bin/activate

# 2. Définir PYTHONPATH et lancer
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python src/web/app.py
```

L'application sera accessible sur : http://localhost:5000

### Générer les rapports en CLI

```bash
# Activer l'environnement
source venv/bin/activate

# Générer les rapports
python scripts/generate_all_reports.py
```

### Arrêter l'application

- **Interface web** : Ctrl+C dans le terminal
- **Désactiver venv** : `deactivate`

## Configuration (Optionnel)

### Créer un fichier .env

```bash
cp .env.example .env
nano .env  # ou votre éditeur préféré
```

Modifiez les variables si nécessaire (par défaut, tout fonctionne sans modification).

## Commandes Récapitulatives

### Première installation (une fois)
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### À chaque utilisation
```bash
source venv/bin/activate
python src/web/app.py
# ... utiliser l'application ...
deactivate
```

## Dépannage

### Erreur : command not found: python

Essayez avec `python3` :
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 src/web/app.py
```

### Erreur : Permission denied

Sur Linux, vous pourriez avoir besoin d'installer python3-venv :
```bash
sudo apt install python3-venv  # Debian/Ubuntu
sudo dnf install python3-venv  # Fedora
```

### L'environnement virtuel ne s'active pas

**Sur Windows avec PowerShell**, vous devez peut-être autoriser l'exécution de scripts :
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Comment savoir si venv est activé ?

Vous devez voir `(venv)` au début de votre ligne de commande.

Vous pouvez aussi vérifier :
```bash
which python
# Devrait afficher : .../conso-chauffage/venv/bin/python
```

### Je veux désinstaller les dépendances

Supprimez simplement le dossier venv :
```bash
deactivate  # d'abord désactiver
rm -rf venv
```

Puis recréez-le si nécessaire :
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Alternative : pipx (pour experts)

Si vous voulez installer l'application de manière globale sans polluer le système :

```bash
# Installer pipx
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Installer l'application (nécessite un setup.py)
pipx install .
```

Mais pour un développement actif, **venv reste la solution recommandée**.

## Mise à jour des dépendances

Après un `git pull` qui modifie `requirements.txt` :

```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

## Résumé

✅ **Toujours utiliser venv** pour éviter les conflits avec le système
✅ **Activer venv** avant chaque utilisation
✅ **Désactiver venv** quand vous avez terminé
✅ **Le dossier venv/** est ignoré par git (dans .gitignore)

Bon courage ! 🚀
