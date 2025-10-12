#!/usr/bin/env python3
"""Script de test pour vérifier la récupération automatique des DJU."""

import sys
from pathlib import Path
from datetime import date, timedelta
import os
from dotenv import load_dotenv

# Ajouter le répertoire courant au PYTHONPATH
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

# Charger .env (optionnel)
env_file = BASE_DIR / '.env'
if env_file.exists():
    load_dotenv(env_file)
    print("✅ Fichier .env trouvé et chargé")
else:
    print("ℹ️  Fichier .env non trouvé (utilisation des valeurs par défaut)")

print()
print("=" * 60)
print("Configuration actuelle :")
print("=" * 60)

station = os.getenv('METEO_STATION', 'Le Bourget')
base_temp = os.getenv('DJU_BASE_TEMP', '18.0')

print(f"📍 METEO_STATION: {station}")
print(f"🌡️  DJU_BASE_TEMP: {base_temp}°C")
print(f"🌐 Source des données: Open-Meteo API (gratuit, sans clé)")

print()
print("=" * 60)
print("Test de récupération des DJU :")
print("=" * 60)

try:
    from src.services import DJUFetcher

    fetcher = DJUFetcher(station=station)

    # Test sur une période récente de 7 jours
    date_fin = date.today() - timedelta(days=1)
    date_debut = date_fin - timedelta(days=7)

    print(f"\n🔍 Test de récupération des DJU du {date_debut} au {date_fin}...")
    print()

    dju = fetcher.get_dju_period(date_debut, date_fin, float(base_temp))

    if dju is not None:
        print(f"✅ Succès ! DJU calculé: {dju}")
        print()
        print("💡 Les données proviennent de Open-Meteo API")
        print("   (API gratuite avec données historiques depuis 1940)")
    else:
        print("❌ Échec de la récupération des DJU")
        print("   Vérifiez votre connexion internet")

except Exception as e:
    print(f"❌ Erreur lors du test: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("Résumé :")
print("=" * 60)
print("✅ L'application utilise Open-Meteo API")
print("   • Gratuit et sans clé API")
print("   • Données historiques complètes")
print("   • Fiable et rapide")
print()
print("📍 Station: Le Bourget (48.9694°N, 2.4414°E)")
print()
