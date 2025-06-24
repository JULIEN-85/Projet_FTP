#!/bin/bash
# Script de démarrage pour l'interface web du système de transfert photo

# Couleurs pour l'affichage
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Démarrage Interface Web Photo Transfer ===${NC}"
echo

# Répertoire du projet
PROJECT_DIR="/home/server01/projet_ftp/Projet_FTP"
cd "$PROJECT_DIR"

# Vérifier si l'interface web est déjà en cours d'exécution
if pgrep -f "simple_webui.py" > /dev/null; then
    echo -e "${YELLOW}L'interface web est déjà en cours d'exécution${NC}"
    echo -e "${GREEN}Accès via: http://$(hostname -I | awk '{print $1}'):8080${NC}"
    echo -e "${GREEN}Ou via: http://127.0.0.1:8080${NC}"
    exit 0
fi

# Vérifier que les fichiers nécessaires existent
if [ ! -f "simple_webui.py" ]; then
    echo -e "${RED}Erreur: simple_webui.py non trouvé dans $PROJECT_DIR${NC}"
    exit 1
fi

if [ ! -f "config.json" ]; then
    echo -e "${RED}Erreur: config.json non trouvé${NC}"
    exit 1
fi

# Créer le répertoire de logs s'il n'existe pas
mkdir -p logs

# Vérifier l'environnement virtuel
if [ -d "venv" ]; then
    echo -e "${YELLOW}Activation de l'environnement virtuel...${NC}"
    source venv/bin/activate
else
    echo -e "${YELLOW}Aucun environnement virtuel trouvé, utilisation de Python global${NC}"
fi

# Vérifier que Flask est installé
if ! python3 -c "import flask" 2>/dev/null; then
    echo -e "${YELLOW}Installation de Flask...${NC}"
    pip3 install flask
fi

# Démarrer l'interface web
echo -e "${YELLOW}Démarrage de l'interface web...${NC}"

# Option pour démarrage en arrière-plan
if [ "$1" = "-d" ] || [ "$1" = "--daemon" ]; then
    echo -e "${YELLOW}Démarrage en mode daemon...${NC}"
    nohup python3 simple_webui.py > logs/webui.log 2>&1 &
    WEBUI_PID=$!
    
    # Attendre un peu et vérifier que le processus est toujours en vie
    sleep 2
    if kill -0 $WEBUI_PID 2>/dev/null; then
        echo -e "${GREEN}✅ Interface web démarrée en arrière-plan (PID: $WEBUI_PID)${NC}"
    else
        echo -e "${RED}❌ Échec du démarrage en daemon${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}Démarrage en mode interactif (Ctrl+C pour arrêter)${NC}"
    python3 simple_webui.py
fi

echo
echo -e "${GREEN}🌐 Interface web accessible via:${NC}"
echo -e "${GREEN}   http://$(hostname -I | awk '{print $1}'):8080${NC}"
echo -e "${GREEN}   http://127.0.0.1:8080${NC}"
echo
echo -e "${BLUE}Fonctionnalités disponibles:${NC}"
echo "   - Configuration FTP/FTPS"
echo "   - Upload manuel de photos"
echo "   - Surveillance des transferts"
echo "   - Gestion des logs"
echo "   - Test de connexion"
