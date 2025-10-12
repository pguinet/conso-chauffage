#!/usr/bin/env python
"""
Script de lancement de l'application web.
Lance l'application depuis la racine du projet.
"""

import sys
from pathlib import Path

# Ajouter le répertoire courant au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

# Importer et lancer l'application
from src.web.app import app, data_manager

if __name__ == '__main__':
    # Charger les données au démarrage
    data_manager.charger_donnees()

    print("=" * 60)
    print("Application de Suivi de Consommation de Chaudière")
    print("=" * 60)
    print()
    print("🌐 Accédez à l'application sur : http://localhost:5000")
    print("⏹️  Appuyez sur Ctrl+C pour arrêter")
    print()

    app.run(debug=True, host='0.0.0.0', port=5000)
