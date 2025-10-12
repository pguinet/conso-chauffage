#!/usr/bin/env python3
"""Script de test pour vérifier que tous les imports fonctionnent."""

import sys
from pathlib import Path

# Ajouter le répertoire courant au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

print("🔍 Test des imports...")
print()

try:
    print("1. Import des modèles...", end=" ")
    from src.models import Saison, Releve
    print("✅")
except Exception as e:
    print(f"❌ {e}")
    sys.exit(1)

try:
    print("2. Import du data manager...", end=" ")
    from src.data_manager import DataManager
    print("✅")
except Exception as e:
    print(f"❌ {e}")
    sys.exit(1)

try:
    print("3. Import des calculs...", end=" ")
    from src.calculs import calculer_rendement
    print("✅")
except Exception as e:
    print(f"❌ {e}")
    sys.exit(1)

try:
    print("4. Import des rapports...", end=" ")
    from src.rapports import generer_rapport_saison_html
    print("✅")
except Exception as e:
    print(f"❌ {e}")
    sys.exit(1)

try:
    print("5. Import des services DJU...", end=" ")
    from src.services import DJUFetcher, DJUCache
    print("✅")
except Exception as e:
    print(f"❌ {e}")
    sys.exit(1)

try:
    print("6. Import Flask (requis)...", end=" ")
    import flask
    print("✅")
except Exception as e:
    print(f"❌ {e}")
    print()
    print("⚠️  Flask n'est pas installé. Installez les dépendances :")
    print("    pip install -r requirements.txt")
    sys.exit(1)

try:
    print("7. Import de l'application Flask...", end=" ")
    from src.web.app import app
    print("✅")
except Exception as e:
    print(f"❌ {e}")
    sys.exit(1)

print()
print("=" * 60)
print("✅ Tous les imports fonctionnent correctement !")
print("=" * 60)
print()
print("Pour lancer l'application :")
print("  python run.py")
print()
