@echo off
REM Script de démarrage pour Windows

echo === Application Suivi Chaudiere ===
echo.

REM Vérifier si venv existe
if not exist "venv\" (
    echo [AVERTISSEMENT] Environnement virtuel non trouve.
    echo Creation de l'environnement virtuel...
    python -m venv venv

    if errorlevel 1 (
        echo [ERREUR] Impossible de creer l'environnement virtuel
        echo Verifiez que Python est installe correctement
        pause
        exit /b 1
    )

    echo [OK] Environnement virtuel cree
    echo.
)

REM Activer l'environnement virtuel
echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo [ERREUR] Impossible d'activer l'environnement virtuel
    pause
    exit /b 1
)

REM Vérifier si les dépendances sont installées
python -c "import flask" 2>nul
if errorlevel 1 (
    echo [AVERTISSEMENT] Dependances non installees.
    echo Installation des dependances...
    pip install -r requirements.txt

    if errorlevel 1 (
        echo [ERREUR] Impossible d'installer les dependances
        pause
        exit /b 1
    )

    echo [OK] Dependances installees
    echo.
)

REM Lancer l'application
echo [OK] Demarrage de l'application...
echo.

python run.py

pause
