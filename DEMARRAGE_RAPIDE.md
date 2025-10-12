# 🚀 Démarrage Rapide

Guide ultra-simplifié pour lancer l'application en 3 étapes.

## Première fois (Installation)

```bash
# 1. Créer l'environnement virtuel
python3 -m venv venv

# 2. Activer l'environnement
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt
```

**Windows :** Remplacez `source venv/bin/activate` par `venv\Scripts\activate`

## Utilisation quotidienne

### Méthode automatique (recommandée)

```bash
./start.sh
```

C'est tout ! Le script s'occupe de tout.

### Méthode manuelle

```bash
# 1. Activer l'environnement virtuel
source venv/bin/activate

# 2. Lancer l'application
python run.py
```

### Ensuite...

Ouvrez votre navigateur sur : **http://localhost:5000**

## Arrêter l'application

- Appuyez sur **Ctrl+C** dans le terminal
- Puis tapez `deactivate` pour sortir du venv

## Problèmes courants

### "command not found: python"
Utilisez `python3` au lieu de `python`

### "externally-managed-environment"
C'est normal ! Utilisez venv comme indiqué ci-dessus

### "ModuleNotFoundError: No module named 'flask'"
Vous avez oublié d'activer le venv ou d'installer les dépendances :
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Le venv est-il activé ?
Vous devez voir `(venv)` au début de votre ligne de commande :
```bash
(venv) pascal@machine:~/conso-chauffage$
```

## Vérifier que tout fonctionne

```bash
# Vérifier la syntaxe Python
python3 check_syntax.py

# Tester les imports
python3 -c "import sys; sys.path.insert(0, '.'); from src.models import Saison; print('OK')"
```

## Documentation complète

- **README.md** : Vue d'ensemble
- **INSTALL.md** : Guide d'installation détaillé avec dépannage
- **CLAUDE.md** : Documentation technique et architecture

## Besoin d'aide ?

1. Lisez [INSTALL.md](INSTALL.md) pour plus de détails
2. Vérifiez que Python 3.9+ est installé : `python3 --version`
3. Assurez-vous que le venv est activé avant toute commande
