#!/bin/bash
# Script d'installation du système de transfert caméra vers FTP robuste

# Couleurs pour une meilleure lisibilité
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Installation du Système de Transfert Caméra → FTP ===${NC}"
echo

# Vérifier si l'utilisateur est root
if [ "$(id -u)" != "0" ]; then
    echo -e "${YELLOW}Ce script doit être exécuté en tant que root${NC}"
    echo "Utilisation: sudo $0"
    exit 1
fi

# Chemin du projet
PROJECT_DIR="$(pwd)"
if [ ! -f "$PROJECT_DIR/robust_camera_transfer.py" ]; then
    echo -e "${RED}Ce script doit être exécuté depuis le répertoire du projet.${NC}"
    echo "cd /home/server01/projet_ftp/Projet_FTP && sudo ./install_robust_transfer.sh"
    exit 1
fi

echo -e "${YELLOW}Installation des dépendances...${NC}"
apt update
apt install -y python3 python3-pip gphoto2 lftp

# Installer les dépendances Python
echo -e "${YELLOW}Installation des dépendances Python...${NC}"
pip3 install flask paramiko requests watchdog

# Créer les répertoires nécessaires
echo -e "${YELLOW}Création des répertoires...${NC}"

# Charger le chemin de téléchargement depuis config.json
DOWNLOAD_PATH=$(grep -o '"download_path"[[:space:]]*:[[:space:]]*"[^"]*"' config.json | sed 's/"download_path"[[:space:]]*:[[:space:]]*"\([^"]*\)"/\1/')
if [ -z "$DOWNLOAD_PATH" ]; then
    DOWNLOAD_PATH="/tmp/photos"
fi

mkdir -p "$DOWNLOAD_PATH"
chmod 777 "$DOWNLOAD_PATH"  # Assurer que tout le monde peut écrire

# Créer le service systemd pour le transfert automatique
echo -e "${YELLOW}Configuration du service systemd...${NC}"

cat > /etc/systemd/system/camera-transfer.service << EOF
[Unit]
Description=Service de transfert Caméra → FTP robuste
After=network.target

[Service]
Type=simple
User=$(logname)
Group=$(logname)
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/bin/python3 $PROJECT_DIR/robust_camera_transfer.py
Restart=on-failure
RestartSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Créer un service de surveillance des nouveaux fichiers
cat > /etc/systemd/system/camera-monitor.service << EOF
[Unit]
Description=Surveillance des nouveaux fichiers photos
After=network.target

[Service]
Type=simple
User=$(logname)
Group=$(logname)
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/bin/python3 $PROJECT_DIR/monitor_and_transfer.py
Restart=on-failure
RestartSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Créer le script de surveillance des nouveaux fichiers
cat > $PROJECT_DIR/monitor_and_transfer.py << EOF
#!/usr/bin/env python3
"""
Moniteur de fichiers pour le transfert automatique de photos
"""
import os
import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('MonitorTransfer')

class NewFileHandler(FileSystemEventHandler):
    """Gestionnaire d'événements pour les nouveaux fichiers"""
    
    def __init__(self, config):
        self.config = config
        self.download_path = config.get('camera', {}).get('download_path', '/tmp/photos')
        
    def on_created(self, event):
        """Appelé quand un fichier est créé"""
        if event.is_directory:
            return
            
        if any(event.src_path.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.nef']):
            logger.info(f"Nouveau fichier détecté: {event.src_path}")
            self.process_file(event.src_path)
    
    def process_file(self, file_path):
        """Traite un nouveau fichier"""
        # Attendre un moment pour que le fichier soit complètement écrit
        time.sleep(2)
        
        # Vérifier que le fichier existe et n'est pas vide
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            logger.warning(f"Fichier invalide ou vide: {file_path}")
            return
            
        logger.info(f"Traitement du fichier: {file_path}")
        
        # Transférer le fichier
        try:
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                      'robust_camera_transfer.py')
            result = subprocess.run([
                'python3',
                script_path,
                '--single-file',
                file_path
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Fichier transféré avec succès: {os.path.basename(file_path)}")
            else:
                logger.error(f"Erreur lors du transfert: {result.stderr}")
        except Exception as e:
            logger.error(f"Erreur lors du traitement du fichier: {e}")

def main():
    """Fonction principale"""
    import json
    
    # Charger la configuration
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except Exception as e:
        logger.error(f"Erreur lors du chargement de la configuration: {e}")
        sys.exit(1)
    
    # Chemin à surveiller
    path = config.get('camera', {}).get('download_path', '/tmp/photos')
    
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        logger.info(f"Création du répertoire {path}")
    
    # Créer l'observateur et démarrer la surveillance
    event_handler = NewFileHandler(config)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    
    logger.info(f"Démarrage de la surveillance du répertoire {path}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()

if __name__ == "__main__":
    main()
EOF

chmod +x $PROJECT_DIR/monitor_and_transfer.py

# Créer un script cron pour exécution périodique
echo -e "${YELLOW}Configuration du cron...${NC}"

CRON_FILE="/etc/cron.d/camera-transfer"
cat > "$CRON_FILE" << EOF
# Exécuter le transfert caméra toutes les 5 minutes
*/5 * * * * $(logname) cd $PROJECT_DIR && /usr/bin/python3 $PROJECT_DIR/robust_camera_transfer.py
# Nettoyer les fichiers corrompus chaque heure
0 * * * * $(logname) cd $PROJECT_DIR && /usr/bin/python3 $PROJECT_DIR/fix_corrupt_photos.py
EOF

chmod 644 "$CRON_FILE"

# Activer et démarrer les services
echo -e "${YELLOW}Activation des services...${NC}"
systemctl daemon-reload
systemctl enable camera-transfer.service
systemctl start camera-transfer.service
systemctl enable camera-monitor.service
systemctl start camera-monitor.service

echo -e "${GREEN}Installation terminée!${NC}"
echo
echo -e "${YELLOW}Résumé de l'installation:${NC}"
echo "- Dépendances installées: Python, gphoto2, lftp"
echo "- Service de transfert configuré et démarré"
echo "- Service de surveillance configuré et démarré"
echo "- Tâche cron configurée pour: "
echo "  - Transfert toutes les 5 minutes"
echo "  - Nettoyage des fichiers corrompus chaque heure"
echo
echo -e "${BLUE}Pour vérifier l'état du service:${NC}"
echo "systemctl status camera-transfer.service"
echo
echo -e "${BLUE}Pour voir les logs:${NC}"
echo "journalctl -u camera-transfer.service -f"
echo
echo -e "${BLUE}Pour un transfert manuel:${NC}"
echo "$PROJECT_DIR/run_camera_transfer.sh"
