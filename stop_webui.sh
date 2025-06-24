#!/bin/bash
# Script d'arrêt pour l'interface web

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}Arrêt de l'interface web...${NC}"

# Trouver et arrêter les processus simple_webui.py
PIDS=$(pgrep -f "simple_webui.py")

if [ -z "$PIDS" ]; then
    echo -e "${YELLOW}Aucune interface web en cours d'exécution${NC}"
    exit 0
fi

echo -e "${YELLOW}Processus trouvés: $PIDS${NC}"

# Arrêt gracieux
for PID in $PIDS; do
    echo -e "${YELLOW}Arrêt du processus $PID...${NC}"
    kill $PID
    
    # Attendre un peu
    sleep 2
    
    # Vérifier si le processus est encore en vie
    if kill -0 $PID 2>/dev/null; then
        echo -e "${RED}Processus $PID ne répond pas, arrêt forcé...${NC}"
        kill -9 $PID
    fi
done

# Vérification finale
sleep 1
REMAINING=$(pgrep -f "simple_webui.py")
if [ -z "$REMAINING" ]; then
    echo -e "${GREEN}✅ Interface web arrêtée avec succès${NC}"
else
    echo -e "${RED}❌ Certains processus sont encore actifs: $REMAINING${NC}"
    exit 1
fi
