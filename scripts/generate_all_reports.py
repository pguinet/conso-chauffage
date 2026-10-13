#!/usr/bin/env python3
"""Script pour générer le site des rapports (pages HTML, graphiques et CSV)."""

from pathlib import Path
import sys

# Ajouter le répertoire parent au path pour pouvoir importer les modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_manager import DataManager  # noqa: E402
from src.rapports import generer_site  # noqa: E402


def main():
    """Génère le site des rapports dans output/."""
    print("=" * 60)
    print("Génération des rapports de consommation de chaudière")
    print("=" * 60)

    base_dir = Path(__file__).parent.parent
    data_file = base_dir / 'data' / 'saisons.yaml'
    output_dir = base_dir / 'output'

    if not data_file.exists():
        print(f"❌ Fichier de données introuvable: {data_file}")
        print("Veuillez créer le fichier data/saisons.yaml avec vos données.")
        sys.exit(1)

    print(f"\n📂 Chargement des données depuis {data_file}")
    saisons = DataManager(data_file).charger_donnees()

    if not saisons:
        print("❌ Aucune saison trouvée dans le fichier de données.")
        sys.exit(1)

    print(f"✅ {len(saisons)} saison(s) chargée(s)")

    print("\n📊 Génération du site...")
    fichiers = generer_site(saisons, output_dir)
    for fichier in fichiers:
        print(f"  ✅ {fichier.name}")

    print("\n" + "=" * 60)
    print(f"✅ {len(fichiers)} fichiers générés dans: {output_dir}")
    print(f"   Point d'entrée : {output_dir / 'index.html'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
