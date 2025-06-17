#!/bin/bash
# Installation minimaliste et optimisée pour Raspberry Pi

set -e

echo "🔋 Installation Photo Transfer System - Version Économique"
echo ""

# Vérifications
if [[ $EUID -eq 0 ]]; then
   echo "❌ Ne pas exécuter en tant que root"
   exit 1
fi

echo "📦 Installation des dépendances essentielles..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv gphoto2 libgphoto2-dev cpufrequtils

echo "📁 Installation du système..."
INSTALL_DIR="/home/pi/photo-ftp"
sudo mkdir -p "$INSTALL_DIR"
sudo cp -r . "$INSTALL_DIR/"
sudo chown -R pi:pi "$INSTALL_DIR"
cd "$INSTALL_DIR"

echo "🐍 Configuration Python..."
python3 -m venv venv
source venv/bin/activate
pip install --no-cache-dir flask werkzeug

echo "⚙️  Configuration services..."
sudo cp photo-ftp.service /etc/systemd/system/
sudo cp photo-ftp-web.service /etc/systemd/system/
sudo systemctl daemon-reload

echo "🔋 Optimisations énergétiques..."
echo 'GOVERNOR="ondemand"' | sudo tee /etc/default/cpufrequtils
echo "gpu_mem=64" | sudo tee -a /boot/config.txt

echo "🔒 Permissions..."
sudo usermod -a -G plugdev pi

mkdir -p logs
touch logs/photo_transfer.log

echo ""
echo "✅ Installation terminée!"
echo "📋 Prochaines étapes:"
echo "1. sudo reboot"
echo "2. sudo systemctl enable photo-ftp photo-ftp-web"
echo "3. sudo systemctl start photo-ftp photo-ftp-web"
echo "4. Configuration: http://$(hostname -I | awk '{print $1}'):8080"
