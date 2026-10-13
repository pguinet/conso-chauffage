#!/usr/bin/env python3
"""
Recalcule les DJU de tous les relevés depuis Open-Meteo.

Pour chaque relevé (sauf le premier de la saison), la période va du lendemain
du relevé précédent au jour du relevé inclus. Les indicateurs dépendant des
DJU sont ensuite recalculés.

Usage :
    python scripts/recalculer_dju.py            # affiche les écarts sans rien écrire
    python scripts/recalculer_dju.py --ecrire   # met à jour data/saisons.yaml
"""

import argparse
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.data_manager import DataManager  # noqa: E402
from src.services import DJUFetcher  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--ecrire", action="store_true", help="enregistrer les nouveaux DJU")
    parser.add_argument("--fichier", type=Path, default=BASE_DIR / "data" / "saisons.yaml")
    args = parser.parse_args()

    data_manager = DataManager(args.fichier)
    data_manager.charger_donnees()
    fetcher = DJUFetcher(timeout=30)

    print(f"{'Saison':<11} {'Relevés':>7} {'DJU avant':>10} {'DJU après':>10} {'Écart':>7}")
    for saison in data_manager.saisons:
        releves = sorted(saison.releves, key=lambda r: r.date_releve)
        nouveaux = fetcher.get_dju_par_releves([r.date_releve for r in releves])
        if nouveaux is None:
            print(f"Échec pour la saison {saison.nom}, aucune donnée modifiée.", file=sys.stderr)
            return 1

        avant = sum(r.dju for r in releves[1:])
        apres = sum(nouveaux)
        ecart = (apres - avant) / avant * 100 if avant else 0.0
        print(f"{saison.nom:<11} {len(releves):>7} {avant:>10.1f} {apres:>10.1f} {ecart:>6.1f}%")

        for releve, dju in zip(releves[1:], nouveaux):
            releve.dju = dju
        saison.releves = releves
        saison.recalculer_tous_les_indicateurs()

    if args.ecrire:
        data_manager.sauvegarder_donnees()
        print(f"\n{args.fichier} mis à jour.")
    else:
        print("\nSimulation : relancer avec --ecrire pour enregistrer.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
