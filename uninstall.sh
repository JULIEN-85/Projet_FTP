#!/bin/bash

# Script de désinstallation du système de transfert automatique de photos

set -e

echo "=== Désinstallation du système de transfert automatique de photos ==="
echo ""

# Variables
INSTALL_DIR="/home/pi/photo-ftp"

echo "1. Arrêt des services..."
sudo systemctl stop photo-ftp.service 2>/dev/null || true
sudo systemctl stop photo-ftp-web.service 2>/dev/null || true

echo ""
echo "2. Désactivation des services..."
sudo systemctl disable photo-ftp.service 2>/dev/null || true
sudo systemctl disable photo-ftp-web.service 2>/dev/null || true

echo ""
echo "3. Suppression des fichiers de service..."
sudo rm -f /etc/systemd/system/photo-ftp.service
sudo rm -f /etc/systemd/system/photo-ftp-web.service
sudo systemctl daemon-reload

echo ""
echo "4. Suppression des règles udev..."
sudo rm -f /etc/udev/rules.d/90-camera.rules
sudo udevadm control --reload-rules

echo ""
echo "5. Suppression du répertoire d'installation..."
if [ -d "$INSTALL_DIR" ]; then
    read -p "Voulez-vous supprimer le répertoire d'installation $INSTALL_DIR ? (y/N): " confirm
    if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
        sudo rm -rf "$INSTALL_DIR"
        echo "✓ Répertoire supprimé"
    else
        echo "✓ Répertoire conservé"
    fi
fi

echo ""
echo "6. Nettoyage des dossiers temporaires..."
sudo rm -rf "/tmp/photos" 2>/dev/null || true

echo ""
echo "=== Désinstallation terminée ==="
echo ""
echo "Note: Les paquets système (gphoto2, python3, etc.) n'ont pas été supprimés."
echo "Pour les supprimer manuellement si nécessaire:"
echo "sudo apt remove gphoto2 libgphoto2-dev"
echo ""
echo "Redémarrage recommandé: sudo reboot"
