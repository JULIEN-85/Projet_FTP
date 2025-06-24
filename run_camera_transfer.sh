#!/bin/bash
# Script pour le transfert robuste depuis un appareil photo vers FTP

# Couleurs pour une meilleure lisibilité
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Transfert Robuste Caméra → FTP ===${NC}"
echo

# Vérifications préliminaires
echo -e "${YELLOW}Vérification des prérequis...${NC}"

# Vérifier que Python est installé
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}Python3 n'est pas installé!${NC}"
    echo "Installez-le avec: sudo apt install python3"
    exit 1
fi

# Vérifier que lftp est installé
if ! command -v lftp &>/dev/null; then
    echo -e "${YELLOW}lftp n'est pas installé. Installation...${NC}"
    sudo apt install -y lftp
    if [ $? -ne 0 ]; then
        echo -e "${RED}Impossible d'installer lftp. Installez-le manuellement:${NC}"
        echo "sudo apt install lftp"
        exit 1
    fi
fi

# Vérifier que gphoto2 est installé
if ! command -v gphoto2 &>/dev/null; then
    echo -e "${YELLOW}gphoto2 n'est pas installé. Installation...${NC}"
    sudo apt install -y gphoto2
    if [ $? -ne 0 ]; then
        echo -e "${RED}Impossible d'installer gphoto2. Installez-le manuellement:${NC}"
        echo "sudo apt install gphoto2"
        exit 1
    fi
fi

# Vérifier que le dossier de destination existe
PHOTO_PATH=$(grep -o '"download_path"[[:space:]]*:[[:space:]]*"[^"]*"' config.json | sed 's/"download_path"[[:space:]]*:[[:space:]]*"\([^"]*\)"/\1/')
if [ -z "$PHOTO_PATH" ]; then
    PHOTO_PATH="/tmp/photos"
fi

if [ ! -d "$PHOTO_PATH" ]; then
    echo -e "${YELLOW}Création du dossier $PHOTO_PATH${NC}"
    mkdir -p "$PHOTO_PATH"
fi

# Options
PURGE=0

# Traiter les options
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -p|--purge) PURGE=1 ;;
        -h|--help) echo "Usage: $0 [-p|--purge] [-h|--help]"; exit 0 ;;
        *) echo "Option inconnue: $1"; exit 1 ;;
    esac
    shift
done

# Purger si demandé
if [ $PURGE -eq 1 ]; then
    echo -e "${YELLOW}Purge des photos existantes...${NC}"
    rm -f "$PHOTO_PATH"/*
    echo -e "${GREEN}Purge terminée${NC}"
fi

# Arrêter les processus qui pourraient interférer
echo -e "${YELLOW}Arrêt des processus pouvant interférer...${NC}"
pkill -f gphoto2 || true
pkill -f gvfs-gphoto2-volume-monitor || true
sleep 1

# Lancer le script Python
echo -e "${BLUE}Démarrage du script de transfert...${NC}"
cd /home/server01/projet_ftp/Projet_FTP
python3 robust_camera_transfer.py $([ $PURGE -eq 1 ] && echo "--purge")

# Vérifier le résultat
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Transfert terminé avec succès!${NC}"
    echo
    echo -e "${YELLOW}Photos restantes dans $PHOTO_PATH:${NC}"
    find "$PHOTO_PATH" -type f | wc -l
else
    echo -e "${RED}Des erreurs se sont produites pendant le transfert.${NC}"
    echo "Consultez les logs pour plus d'informations."
    echo
    echo -e "${YELLOW}Dernières lignes du log:${NC}"
    tail -5 logs/robust_transfer.log
fi

echo
echo -e "${BLUE}=== Fin du processus ===${NC}"
