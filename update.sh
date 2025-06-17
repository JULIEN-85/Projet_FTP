#!/bin/bash

# Script de mise à jour du système de transfert de photos
# Met à jour le code, les dépendances et la configuration si nécessaire

set -e

# Configuration
PROJECT_DIR="/home/pi/photo-ftp"
CURRENT_DIR=$(pwd)
BACKUP_DIR="/home/pi/photo-ftp-backups"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Mise à jour du Système de Transfert de Photos ===${NC}"
echo ""

# Vérification des privilèges
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}Ce script ne doit PAS être exécuté en tant que root${NC}"
   echo "Utilisez: ./update.sh"
   exit 1
fi

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "main.py" ] || [ ! -f "webui.py" ]; then
    echo -e "${RED}Erreur: Ce script doit être exécuté depuis le répertoire contenant les fichiers du projet${NC}"
    exit 1
fi

# Créer une sauvegarde avant mise à jour
echo -e "${YELLOW}1. Création d'une sauvegarde avant mise à jour...${NC}"
if [ -f "backup.sh" ]; then
    chmod +x backup.sh
    ./backup.sh
else
    echo -e "${YELLOW}Script de sauvegarde non trouvé, création d'une sauvegarde manuelle...${NC}"
    mkdir -p "${BACKUP_DIR}"
    BACKUP_NAME="pre-update-backup_$(date +%Y%m%d_%H%M%S)"
    cp -r "${PROJECT_DIR}" "${BACKUP_DIR}/${BACKUP_NAME}"
    echo -e "${GREEN}✓${NC} Sauvegarde créée: ${BACKUP_DIR}/${BACKUP_NAME}"
fi

# Arrêter les services
echo -e "${YELLOW}2. Arrêt des services...${NC}"
sudo systemctl stop photo-ftp.service 2>/dev/null || echo "Service photo-ftp non actif"
sudo systemctl stop photo-ftp-web.service 2>/dev/null || echo "Service photo-ftp-web non actif"
echo -e "${GREEN}✓${NC} Services arrêtés"

# Mise à jour du système
echo -e "${YELLOW}3. Mise à jour du système...${NC}"
sudo apt update
sudo apt upgrade -y gphoto2 libgphoto2-dev python3 python3-pip
echo -e "${GREEN}✓${NC} Système mis à jour"

# Mise à jour de l'environnement Python
echo -e "${YELLOW}4. Mise à jour de l'environnement Python...${NC}"
cd "${PROJECT_DIR}"

# Sauvegarder les dépendances actuelles
if [ -f "venv/lib/python*/site-packages" ]; then
    pip freeze > old_requirements.txt
fi

# Activer l'environnement virtuel
source venv/bin/activate

# Mise à jour pip
pip install --upgrade pip

# Mise à jour des dépendances
if [ -f "requirements.txt" ]; then
    pip install --upgrade -r requirements.txt
    echo -e "${GREEN}✓${NC} Dépendances Python mises à jour"
else
    echo -e "${YELLOW}!${NC} Fichier requirements.txt non trouvé"
fi

# Vérifier les changements de configuration
echo -e "${YELLOW}5. Vérification de la configuration...${NC}"

# Sauvegarder l'ancienne config
if [ -f "config.json" ]; then
    cp config.json config.json.backup
fi

# Comparer avec config.example.json si disponible
if [ -f "config.example.json" ] && [ -f "config.json" ]; then
    echo "Vérification des nouvelles options de configuration..."
    
    # Script Python pour fusionner les configurations
    python3 << 'EOF'
import json
import sys

try:
    # Charger la configuration actuelle
    with open('config.json', 'r') as f:
        current_config = json.load(f)
    
    # Charger l'exemple de configuration
    with open('config.example.json', 'r') as f:
        example_config = json.load(f)
    
    # Fonction pour fusionner récursivement
    def merge_configs(current, example):
        merged = current.copy()
        for key, value in example.items():
            if key.startswith('_'):  # Ignorer les commentaires
                continue
            if key not in merged:
                merged[key] = value
                print(f"Nouvelle option ajoutée: {key}")
            elif isinstance(value, dict) and isinstance(merged[key], dict):
                merged[key] = merge_configs(merged[key], value)
        return merged
    
    # Fusionner les configurations
    new_config = merge_configs(current_config, example_config)
    
    # Sauvegarder si des changements ont été détectés
    if new_config != current_config:
        with open('config.json.new', 'w') as f:
            json.dump(new_config, f, indent=4)
        print("Configuration mise à jour sauvegardée dans config.json.new")
        print("Vérifiez les changements et renommez le fichier si nécessaire")
    else:
        print("Configuration à jour")

except Exception as e:
    print(f"Erreur lors de la vérification de la configuration: {e}")
EOF

fi

echo -e "${GREEN}✓${NC} Configuration vérifiée"

# Mise à jour des services systemd
echo -e "${YELLOW}6. Mise à jour des services systemd...${NC}"

# Sauvegarder les anciens services
sudo cp /etc/systemd/system/photo-ftp.service /etc/systemd/system/photo-ftp.service.backup 2>/dev/null || true
sudo cp /etc/systemd/system/photo-ftp-web.service /etc/systemd/system/photo-ftp-web.service.backup 2>/dev/null || true

# Installer les nouveaux services
if [ -f "photo-ftp.service" ]; then
    sudo cp photo-ftp.service /etc/systemd/system/
fi
if [ -f "photo-ftp-web.service" ]; then
    sudo cp photo-ftp-web.service /etc/systemd/system/
fi

# Recharger systemd
sudo systemctl daemon-reload
echo -e "${GREEN}✓${NC} Services systemd mis à jour"

# Mise à jour des permissions
echo -e "${YELLOW}7. Mise à jour des permissions...${NC}"
chmod +x main.py webui.py
chmod +x *.sh 2>/dev/null || true
sudo chown -R pi:pi "${PROJECT_DIR}"
echo -e "${GREEN}✓${NC} Permissions mises à jour"

# Test de l'installation
echo -e "${YELLOW}8. Test de l'installation mise à jour...${NC}"
if [ -f "test_system.py" ]; then
    python3 test_system.py --quiet || echo "Quelques tests ont échoué, mais la mise à jour peut continuer"
else
    echo "Script de test non trouvé, test manuel recommandé"
fi

# Redémarrage des services
echo -e "${YELLOW}9. Redémarrage des services...${NC}"
sudo systemctl start photo-ftp-web.service
echo -e "${GREEN}✓${NC} Interface web redémarrée"

# Le service principal sera démarré manuellement via l'interface web
echo -e "${YELLOW}!${NC} Le service principal doit être redémarré manuellement via l'interface web"

# Nettoyage
echo -e "${YELLOW}10. Nettoyage...${NC}"
deactivate 2>/dev/null || true

# Supprimer les fichiers temporaires de plus de 7 jours
find /tmp -name "photo-*" -type f -mtime +7 -delete 2>/dev/null || true

echo -e "${GREEN}✓${NC} Nettoyage terminé"

# Résumé
echo ""
echo -e "${GREEN}=== Mise à jour terminée avec succès ===${NC}"
echo ""
echo -e "${BLUE}Changements effectués:${NC}"
echo "- Système et paquets mis à jour"
echo "- Environnement Python mis à jour"
echo "- Configuration vérifiée"
echo "- Services systemd mis à jour"
echo "- Permissions corrigées"
echo ""
echo -e "${BLUE}Prochaines étapes:${NC}"
echo "1. Vérifiez la configuration si un fichier config.json.new a été créé"
echo "2. Accédez à l'interface web: http://$(hostname -I | awk '{print $1}'):8080"
echo "3. Testez les connexions (appareil photo et FTP)"
echo "4. Redémarrez le service principal si nécessaire"
echo ""
echo -e "${YELLOW}Note:${NC} Une sauvegarde a été créée avant la mise à jour"
echo -e "${YELLOW}Note:${NC} Redémarrage du système recommandé: sudo reboot"

# Optionnel: afficher les logs récents
read -p "Voulez-vous afficher les logs récents pour vérifier le bon fonctionnement? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Logs récents de l'interface web:${NC}"
    journalctl -u photo-ftp-web.service -n 20 --no-pager || echo "Aucun log disponible"
fi

echo ""
echo -e "${GREEN}Mise à jour terminée!${NC}"
