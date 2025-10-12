#!/usr/bin/env python3
"""Script pour recalculer tous les rendements avec la conversion MWh -> kWh."""

import sys
from pathlib import Path

# Ajouter le répertoire courant au PYTHONPATH
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from src.data_manager import DataManager

# Charger les données
data_manager = DataManager(BASE_DIR / 'data' / 'saisons.yaml')
data_manager.charger_donnees()

print("=" * 70)
print("Recalcul des rendements avec conversion MWh -> kWh")
print("=" * 70)
print()

total_releves = 0
releves_recalcules = 0

for saison in data_manager.saisons:
    print(f"Saison {saison.nom}:")
    
    for i, releve in enumerate(saison.releves):
        total_releves += 1
        
        if i == 0:
            # Premier relevé, pas de calcul
            continue
        
        if releve.dju == 0:
            # Relevé de référence, pas de calcul
            continue
        
        # Recalculer avec le relevé précédent
        releve_precedent = saison.releves[i - 1]
        
        # Sauvegarder l'ancien rendement
        ancien_rendement = releve.rendement
        
        # Recalculer les indicateurs avec la nouvelle formule
        releve.calculer_indicateurs(releve_precedent)
        
        # Afficher si changement significatif
        if ancien_rendement is not None and releve.rendement is not None:
            diff = releve.rendement - ancien_rendement
            if abs(diff) > 0.01:  # Différence > 0.01%
                print(f"  {releve.date_releve}: {ancien_rendement:.2f}% -> {releve.rendement:.2f}% ({diff:+.2f}%)")
                releves_recalcules += 1

print()
print("=" * 70)
print(f"Recalcul terminé :")
print(f"  - Total de relevés: {total_releves}")
print(f"  - Relevés recalculés: {releves_recalcules}")
print("=" * 70)
print()

# Sauvegarder
print("Sauvegarde des données...")
data_manager.sauvegarder_donnees()
print("✅ Données sauvegardées dans data/saisons.yaml")
print()
print("💡 Les nouveaux rendements devraient être entre 70% et 90%")
