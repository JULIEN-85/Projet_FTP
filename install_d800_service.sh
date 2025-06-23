#!/bin/bash
#
# Script d'installation du service de téléchargement automatique D800
#

SERVICE_NAME="d800_download"
SERVICE_FILE="/home/server01/projet_ftp/Projet_FTP/${SERVICE_NAME}.service"
SYSTEM_SERVICE="/etc/systemd/system/${SERVICE_NAME}.service"

echo "=== Installation du service ${SERVICE_NAME} ==="

# Vérifier les permissions sudo
if [ "$EUID" -ne 0 ]; then
  echo "Ce script doit être exécuté avec sudo."
  echo "Usage: sudo $0"
  exit 1
fi

# Vérifier que le fichier service existe
if [ ! -f "$SERVICE_FILE" ]; then
  echo "ERREUR: Fichier service non trouvé: $SERVICE_FILE"
  exit 1
fi

# Copier le fichier service
echo "Copie du fichier service vers /etc/systemd/system/"
cp "$SERVICE_FILE" "$SYSTEM_SERVICE"
chmod 644 "$SYSTEM_SERVICE"

# Recharger les services systemd
echo "Rechargement de systemd"
systemctl daemon-reload

# Activer le service
echo "Activation du service"
systemctl enable "$SERVICE_NAME"

# Démarrer le service
echo "Démarrage du service"
systemctl start "$SERVICE_NAME"

# Vérifier l'état du service
echo "Vérification de l'état du service"
systemctl status "$SERVICE_NAME"

echo "====================================="
echo "Pour vérifier les logs du service:"
echo "journalctl -u $SERVICE_NAME -f"
echo "====================================="
