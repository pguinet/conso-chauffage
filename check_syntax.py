#!/usr/bin/env python3
"""Script de vérification de la syntaxe de tous les fichiers Python."""

import sys
from pathlib import Path
import py_compile

def check_syntax(directory):
    """Vérifie la syntaxe de tous les fichiers Python dans un répertoire."""
    errors = []
    checked = 0

    for py_file in Path(directory).rglob('*.py'):
        # Ignorer le venv
        if 'venv' in str(py_file) or '__pycache__' in str(py_file):
            continue

        try:
            py_compile.compile(py_file, doraise=True)
            checked += 1
            print(f"✅ {py_file}")
        except py_compile.PyCompileError as e:
            errors.append((py_file, str(e)))
            print(f"❌ {py_file}: {e}")

    print(f"\n{'='*60}")
    print(f"Fichiers vérifiés : {checked}")

    if errors:
        print(f"❌ Erreurs trouvées : {len(errors)}")
        for file, error in errors:
            print(f"  - {file}: {error}")
        return 1
    else:
        print("✅ Aucune erreur de syntaxe trouvée !")
        return 0

if __name__ == '__main__':
    directory = sys.argv[1] if len(sys.argv) > 1 else 'src'
    sys.exit(check_syntax(directory))
