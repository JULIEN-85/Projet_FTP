#!/bin/bash

# Script d'installation du système de transfert automatique de photos
# Pour Raspberry Pi OS (Debian)

set -e

echo "=== Installation du système de transfert automatique de photos ==="
echo ""

# Vérification des privilèges
if [[ $EUID -eq 0 ]]; then
   echo "Ce script ne doit PAS être exécuté en tant que root"
   echo "Utilisez: ./install.sh"
   exit 1
fi

# Variables
INSTALL_DIR="/home/pi/photo-ftp"
CURRENT_DIR=$(pwd)

echo "1. Mise à jour du système..."
sudo apt update && sudo apt upgrade -y

echo ""
echo "2. Installation des dépendances système..."
sudo apt install -y python3 python3-pip python3-venv gphoto2 libgphoto2-dev

echo ""
echo "3. Test de gPhoto2..."
if command -v gphoto2 &> /dev/null; then
    echo "✓ gPhoto2 installé avec succès"
    gphoto2 --version | head -1
else
    echo "✗ Erreur: gPhoto2 n'a pas pu être installé"
    exit 1
fi

echo ""
echo "4. Création du répertoire d'installation..."
sudo mkdir -p "$INSTALL_DIR"
sudo chown pi:pi "$INSTALL_DIR"

echo ""
echo "5. Copie des fichiers..."
cp -r "$CURRENT_DIR"/* "$INSTALL_DIR/"

echo ""
echo "6. Installation de l'environnement Python..."
cd "$INSTALL_DIR"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "7. Configuration des permissions..."
chmod +x "$INSTALL_DIR/main.py"
chmod +x "$INSTALL_DIR/webui.py"
mkdir -p "$INSTALL_DIR/logs"
mkdir -p "/tmp/photos"
sudo chown -R pi:pi "$INSTALL_DIR"
sudo chown pi:pi "/tmp/photos"

echo ""
echo "8. Installation des services systemd..."
sudo cp "$INSTALL_DIR/photo-ftp.service" /etc/systemd/system/
sudo cp "$INSTALL_DIR/photo-ftp-web.service" /etc/systemd/system/

# Mise à jour des chemins dans les services
sudo sed -i "s|/home/pi/photo-ftp|$INSTALL_DIR|g" /etc/systemd/system/photo-ftp.service
sudo sed -i "s|/home/pi/photo-ftp|$INSTALL_DIR|g" /etc/systemd/system/photo-ftp-web.service
sudo sed -i "s|/usr/bin/python3|$INSTALL_DIR/venv/bin/python|g" /etc/systemd/system/photo-ftp.service
sudo sed -i "s|/usr/bin/python3|$INSTALL_DIR/venv/bin/python|g" /etc/systemd/system/photo-ftp-web.service

echo ""
echo "9. Activation des services..."
sudo systemctl daemon-reload
sudo systemctl enable photo-ftp-web.service

echo ""
echo "10. Configuration des règles udev pour l'appareil photo..."
sudo tee /etc/udev/rules.d/90-camera.rules > /dev/null << EOF
# Règles pour les appareils photo USB
SUBSYSTEM=="usb", ATTRS{idVendor}=="04a9", GROUP="plugdev", MODE="0664"  # Canon
SUBSYSTEM=="usb", ATTRS{idVendor}=="054c", GROUP="plugdev", MODE="0664"  # Sony
SUBSYSTEM=="usb", ATTRS{idVendor}=="04b0", GROUP="plugdev", MODE="0664"  # Nikon
EOF

sudo udevadm control --reload-rules

echo ""
echo "11. Ajout de l'utilisateur pi au groupe plugdev..."
sudo usermod -a -G plugdev pi

echo ""
echo "12. Démarrage de l'interface web..."
sudo systemctl start photo-ftp-web.service

echo ""
echo "=== Installation terminée avec succès! ==="
echo ""
echo "Prochaines étapes:"
echo "1. Redémarrez votre Raspberry Pi: sudo reboot"
echo "2. Connectez votre appareil photo en USB"
echo "3. Accédez à l'interface web: http://$(hostname -I | awk '{print $1}'):8080"
echo "4. Configurez vos paramètres FTP dans l'interface web"
echo "5. Démarrez le service de transfert depuis l'interface web"
echo ""
echo "Pour activer le démarrage automatique du service principal:"
echo "sudo systemctl enable photo-ftp.service"
echo ""
echo "Pour voir les logs en temps réel:"
echo "journalctl -u photo-ftp.service -f"
echo "journalctl -u photo-ftp-web.service -f"
echo ""
echo "Répertoire d'installation: $INSTALL_DIR"
echo "Interface web accessible sur le port 8080"
