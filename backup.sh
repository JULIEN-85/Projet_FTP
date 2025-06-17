#!/bin/bash

# Script de sauvegarde pour le système de transfert de photos
# Sauvegarde la configuration, les logs et optionnellement les photos

set -e

# Configuration
BACKUP_DIR="/home/pi/photo-ftp-backups"
PROJECT_DIR="/home/pi/photo-ftp"
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="photo-ftp-backup_${DATE}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Sauvegarde du Système de Transfert de Photos ===${NC}"
echo -e "Date: $(date)"
echo -e "Destination: ${BACKUP_PATH}"
echo ""

# Créer le répertoire de sauvegarde
echo -e "${YELLOW}1. Création du répertoire de sauvegarde...${NC}"
mkdir -p "${BACKUP_PATH}"

# Sauvegarder la configuration
echo -e "${YELLOW}2. Sauvegarde de la configuration...${NC}"
if [ -f "${PROJECT_DIR}/config.json" ]; then
    cp "${PROJECT_DIR}/config.json" "${BACKUP_PATH}/"
    echo -e "${GREEN}✓${NC} Configuration sauvegardée"
else
    echo -e "${RED}✗${NC} Fichier de configuration non trouvé"
fi

# Sauvegarder les logs
echo -e "${YELLOW}3. Sauvegarde des logs...${NC}"
if [ -d "${PROJECT_DIR}/logs" ]; then
    cp -r "${PROJECT_DIR}/logs" "${BACKUP_PATH}/"
    echo -e "${GREEN}✓${NC} Logs sauvegardés"
else
    echo -e "${RED}✗${NC} Dossier de logs non trouvé"
fi

# Sauvegarder les services systemd
echo -e "${YELLOW}4. Sauvegarde des services systemd...${NC}"
mkdir -p "${BACKUP_PATH}/systemd"
if [ -f "/etc/systemd/system/photo-ftp.service" ]; then
    sudo cp "/etc/systemd/system/photo-ftp.service" "${BACKUP_PATH}/systemd/"
    echo -e "${GREEN}✓${NC} Service photo-ftp.service sauvegardé"
fi
if [ -f "/etc/systemd/system/photo-ftp-web.service" ]; then
    sudo cp "/etc/systemd/system/photo-ftp-web.service" "${BACKUP_PATH}/systemd/"
    echo -e "${GREEN}✓${NC} Service photo-ftp-web.service sauvegardé"
fi

# Sauvegarder les informations système
echo -e "${YELLOW}5. Sauvegarde des informations système...${NC}"
mkdir -p "${BACKUP_PATH}/system_info"

# Version du système
uname -a > "${BACKUP_PATH}/system_info/uname.txt"
lsb_release -a > "${BACKUP_PATH}/system_info/os_version.txt" 2>/dev/null || true

# Packages installés
dpkg -l | grep -E "(gphoto|python|flask)" > "${BACKUP_PATH}/system_info/packages.txt" || true

# Configuration réseau
ip addr show > "${BACKUP_PATH}/system_info/network.txt"

# Informations USB
lsusb > "${BACKUP_PATH}/system_info/usb_devices.txt"

# Status des services
systemctl status photo-ftp.service > "${BACKUP_PATH}/system_info/service_status.txt" 2>/dev/null || true
systemctl status photo-ftp-web.service >> "${BACKUP_PATH}/system_info/service_status.txt" 2>/dev/null || true

echo -e "${GREEN}✓${NC} Informations système sauvegardées"

# Optionnel: sauvegarder les photos temporaires
read -p "Voulez-vous sauvegarder les photos temporaires? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}6. Sauvegarde des photos temporaires...${NC}"
    if [ -d "/tmp/photos" ] && [ "$(ls -A /tmp/photos)" ]; then
        cp -r "/tmp/photos" "${BACKUP_PATH}/temp_photos"
        PHOTO_COUNT=$(find "${BACKUP_PATH}/temp_photos" -type f | wc -l)
        echo -e "${GREEN}✓${NC} ${PHOTO_COUNT} photos temporaires sauvegardées"
    else
        echo -e "${YELLOW}!${NC} Aucune photo temporaire trouvée"
    fi
fi

# Créer un fichier de métadonnées
echo -e "${YELLOW}7. Création des métadonnées...${NC}"
cat > "${BACKUP_PATH}/backup_info.txt" << EOF
=== Sauvegarde Système Photo Transfer ===
Date de création: $(date)
Système: $(uname -a)
Version OS: $(lsb_release -d | cut -f2)
Utilisateur: $(whoami)
Répertoire source: ${PROJECT_DIR}
Taille de sauvegarde: $(du -sh "${BACKUP_PATH}" | cut -f1)

=== Contenu de la sauvegarde ===
$(find "${BACKUP_PATH}" -type f | sort)

=== Services actifs ===
$(systemctl is-active photo-ftp.service 2>/dev/null || echo "Service photo-ftp non actif")
$(systemctl is-active photo-ftp-web.service 2>/dev/null || echo "Service photo-ftp-web non actif")
EOF

echo -e "${GREEN}✓${NC} Métadonnées créées"

# Créer une archive
echo -e "${YELLOW}8. Création de l'archive...${NC}"
cd "${BACKUP_DIR}"
tar -czf "${BACKUP_NAME}.tar.gz" "${BACKUP_NAME}"
ARCHIVE_SIZE=$(du -sh "${BACKUP_NAME}.tar.gz" | cut -f1)

# Supprimer le dossier temporaire
rm -rf "${BACKUP_NAME}"

echo -e "${GREEN}✓${NC} Archive créée: ${BACKUP_NAME}.tar.gz (${ARCHIVE_SIZE})"

# Nettoyage des anciennes sauvegardes (garder les 5 plus récentes)
echo -e "${YELLOW}9. Nettoyage des anciennes sauvegardes...${NC}"
cd "${BACKUP_DIR}"
ls -t photo-ftp-backup_*.tar.gz | tail -n +6 | xargs -r rm -f
REMAINING_BACKUPS=$(ls photo-ftp-backup_*.tar.gz | wc -l)
echo -e "${GREEN}✓${NC} ${REMAINING_BACKUPS} sauvegardes conservées"

# Résumé
echo ""
echo -e "${GREEN}=== Sauvegarde terminée avec succès ===${NC}"
echo -e "Archive: ${GREEN}${BACKUP_DIR}/${BACKUP_NAME}.tar.gz${NC}"
echo -e "Taille: ${GREEN}${ARCHIVE_SIZE}${NC}"
echo ""
echo -e "${BLUE}Pour restaurer cette sauvegarde:${NC}"
echo -e "cd ${BACKUP_DIR}"
echo -e "tar -xzf ${BACKUP_NAME}.tar.gz"
echo -e "cd ${BACKUP_NAME}"
echo -e "# Puis restaurer manuellement les fichiers nécessaires"
echo ""

# Optionnel: envoyer la sauvegarde par FTP
read -p "Voulez-vous envoyer la sauvegarde sur le serveur FTP configuré? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}10. Envoi de la sauvegarde par FTP...${NC}"
    
    if [ -f "${PROJECT_DIR}/config.json" ]; then
        # Extraire les informations FTP de la configuration
        FTP_SERVER=$(python3 -c "import json; print(json.load(open('${PROJECT_DIR}/config.json'))['ftp']['server'])" 2>/dev/null || echo "")
        FTP_USER=$(python3 -c "import json; print(json.load(open('${PROJECT_DIR}/config.json'))['ftp']['username'])" 2>/dev/null || echo "")
        
        if [ ! -z "$FTP_SERVER" ] && [ ! -z "$FTP_USER" ]; then
            echo "Envoi vers ${FTP_SERVER} avec l'utilisateur ${FTP_USER}..."
            # Script Python pour upload FTP
            python3 << EOF
import json
import ftplib
import os

try:
    with open('${PROJECT_DIR}/config.json', 'r') as f:
        config = json.load(f)
    
    ftp = ftplib.FTP()
    ftp.connect(config['ftp']['server'], config['ftp']['port'])
    ftp.login(config['ftp']['username'], config['ftp']['password'])
    
    if config['ftp']['passive_mode']:
        ftp.set_pasv(True)
    
    # Créer un dossier backups s'il n'existe pas
    try:
        ftp.mkd('backups')
    except:
        pass
    
    ftp.cwd('backups')
    
    # Upload du fichier
    with open('${BACKUP_DIR}/${BACKUP_NAME}.tar.gz', 'rb') as f:
        ftp.storbinary('STOR ${BACKUP_NAME}.tar.gz', f)
    
    ftp.quit()
    print("✓ Sauvegarde envoyée avec succès sur le serveur FTP")
    
except Exception as e:
    print(f"✗ Erreur lors de l'envoi FTP: {e}")
EOF
        else
            echo -e "${RED}✗${NC} Configuration FTP incomplète"
        fi
    else
        echo -e "${RED}✗${NC} Fichier de configuration non trouvé"
    fi
fi

echo ""
echo -e "${BLUE}=== Sauvegarde complète terminée ===${NC}"
