#!/bin/bash
# Script de démarrage de l'application

# Couleurs pour les messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Application Suivi Chaudière ===${NC}"
echo ""

# Vérifier si venv existe
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Environnement virtuel non trouvé.${NC}"
    echo -e "${YELLOW}Création de l'environnement virtuel...${NC}"
    python3 -m venv venv

    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Erreur lors de la création de l'environnement virtuel.${NC}"
        echo -e "${YELLOW}Essayez : sudo apt install python3-venv${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ Environnement virtuel créé${NC}"
    echo ""
fi

# Activer l'environnement virtuel
echo -e "${YELLOW}Activation de l'environnement virtuel...${NC}"
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erreur lors de l'activation de l'environnement virtuel${NC}"
    exit 1
fi

# Vérifier si les dépendances sont installées
if ! python -c "import flask" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Dépendances non installées.${NC}"
    echo -e "${YELLOW}Installation des dépendances...${NC}"
    pip install -r requirements.txt

    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Erreur lors de l'installation des dépendances${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ Dépendances installées${NC}"
    echo ""
fi

# Lancer l'application
echo -e "${GREEN}✅ Démarrage de l'application...${NC}"
echo ""

python run.py
