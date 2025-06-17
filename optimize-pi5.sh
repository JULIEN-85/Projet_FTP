#!/bin/bash

# Script d'optimisation spécifique pour Raspberry Pi 5
# À exécuter après l'installation principale

echo "🚀 Optimisation pour Raspberry Pi 5..."

# Vérifier qu'on est bien sur un Pi 5
PI_MODEL=$(cat /proc/device-tree/model 2>/dev/null)
if [[ ! "$PI_MODEL" == *"Raspberry Pi 5"* ]]; then
    echo "⚠️  Ce script est conçu pour Raspberry Pi 5"
    echo "Modèle détecté: $PI_MODEL"
    read -p "Continuer quand même? (y/N): " -r
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

echo "✅ Raspberry Pi 5 détecté: $PI_MODEL"

# 1. Optimisations système
echo "🔧 Application des optimisations système..."

# Augmenter les limites pour les gros fichiers
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Optimisations réseau
echo "net.core.rmem_max = 16777216" | sudo tee -a /etc/sysctl.conf
echo "net.core.wmem_max = 16777216" | sudo tee -a /etc/sysctl.conf
echo "net.ipv4.tcp_rmem = 4096 87380 16777216" | sudo tee -a /etc/sysctl.conf
echo "net.ipv4.tcp_wmem = 4096 65536 16777216" | sudo tee -a /etc/sysctl.conf

# 2. Configuration boot optimisée
echo "⚙️  Configuration du boot..."
if [ -f "pi5-config.txt" ]; then
    echo "Sauvegarde de la config actuelle..."
    sudo cp /boot/firmware/config.txt /boot/firmware/config.txt.backup
    
    echo "Application de la config optimisée..."
    sudo cp pi5-config.txt /boot/firmware/config-pi5-optimized.txt
    
    # Ajouter les optimisations à la config existante
    echo "" | sudo tee -a /boot/firmware/config.txt
    echo "# Optimisations Pi 5 pour photo-transfer" | sudo tee -a /boot/firmware/config.txt
    cat pi5-config.txt | sudo tee -a /boot/firmware/config.txt
fi

# 3. Optimisations Python pour Pi 5
echo "🐍 Optimisations Python..."
cd /home/pi/photo-ftp
source venv/bin/activate

# Installer des packages optimisés
pip install --upgrade pip setuptools wheel
pip install pillow-simd 2>/dev/null || pip install pillow  # Version optimisée si disponible

# 4. Configuration spécifique photo-transfer pour Pi 5
echo "📸 Configuration photo-transfer pour Pi 5..."

# Créer une config optimisée pour Pi 5
cat > config-pi5.json << 'EOF'
{
    "ftp": {
        "server": "",
        "port": 21,
        "username": "",
        "password": "",
        "directory": "/uploads",
        "passive_mode": true,
        "timeout": 30,
        "retry_delay": 2
    },
    "camera": {
        "auto_detect": true,
        "download_path": "/tmp/photos",
        "delete_after_upload": true,
        "concurrent_downloads": 2,
        "max_file_size": "500MB"
    },
    "system": {
        "log_level": "INFO",
        "check_interval": 3,
        "max_retries": 5,
        "web_port": 8080,
        "web_host": "0.0.0.0",
        "worker_threads": 4,
        "memory_limit": "1GB",
        "cpu_priority": "normal"
    },
    "pi5_optimizations": {
        "use_hardware_acceleration": true,
        "parallel_processing": true,
        "fast_usb_mode": true,
        "network_buffer_size": 65536
    }
}
EOF

echo "📝 Configuration Pi 5 créée: config-pi5.json"

# 5. Service systemd optimisé pour Pi 5
echo "⚡ Services optimisés pour Pi 5..."

# Service principal avec optimisations Pi 5
cat > photo-ftp-pi5.service << 'EOF'
[Unit]
Description=Photo Transfer Service - Optimized for Pi 5
After=network.target
Wants=network.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=/home/pi/photo-ftp
ExecStart=/home/pi/photo-ftp/venv/bin/python /home/pi/photo-ftp/main.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

# Optimisations Pi 5
Nice=-5
IOSchedulingClass=1
IOSchedulingPriority=4
CPUSchedulingPolicy=2
CPUSchedulingPriority=10

# Limites de ressources pour Pi 5
LimitNOFILE=65536
LimitMEMLOCK=infinity
MemoryMax=2G
TasksMax=1024

# Variables d'environnement
Environment=PYTHONUNBUFFERED=1
Environment=OPENCV_OPENCL_DEVICE=disabled
Environment=PATH=/usr/local/bin:/usr/bin:/bin

# Sécurité
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/pi/photo-ftp /tmp

[Install]
WantedBy=multi-user.target
EOF

sudo cp photo-ftp-pi5.service /etc/systemd/system/

# 6. Monitoring amélioré pour Pi 5
echo "📊 Monitoring Pi 5..."

# Script de monitoring Pi 5
cat > monitor-pi5.sh << 'EOF'
#!/bin/bash

echo "🎯 Monitoring Raspberry Pi 5 - Photo Transfer"
echo "============================================="
echo ""

# Température et fréquences
echo "🌡️  Température et performances:"
echo "  CPU Temp: $(vcgencmd measure_temp)"
echo "  CPU Freq: $(vcgencmd measure_clock arm) Hz"
echo "  GPU Freq: $(vcgencmd measure_clock core) Hz"
echo "  Voltage:  $(vcgencmd measure_volts)"

# Mémoire
echo ""
echo "💾 Mémoire:"
free -h | grep -E "(Mem|Swap)"

# CPU
echo ""
echo "⚡ CPU (5 dernières minutes):"
uptime

# Stockage
echo ""
echo "💿 Stockage:"
df -h / | tail -1

# USB (appareils photo)
echo ""
echo "🔌 Appareils USB:"
lsusb | grep -i -E "(canon|nikon|sony|camera)" || echo "  Aucun appareil photo détecté"

# Réseau
echo ""
echo "🌐 Réseau:"
ip route get 8.8.8.8 | head -1

# Services
echo ""
echo "🔧 Services photo-transfer:"
systemctl is-active photo-ftp.service || echo "  photo-ftp: inactif"
systemctl is-active photo-ftp-web.service || echo "  photo-ftp-web: inactif"

# Logs récents
echo ""
echo "📝 Dernières activités:"
journalctl -u photo-ftp.service -n 3 --no-pager | tail -3 || echo "  Aucune activité récente"
EOF

chmod +x monitor-pi5.sh

echo ""
echo "🎉 Optimisation Pi 5 terminée!"
echo ""
echo "📋 Changements appliqués:"
echo "  ✅ Configuration boot optimisée"
echo "  ✅ Limites système augmentées"
echo "  ✅ Services avec priorité haute"
echo "  ✅ Configuration spéciale Pi 5"
echo "  ✅ Monitoring amélioré"
echo ""
echo "🔄 Redémarrage recommandé: sudo reboot"
echo ""
echo "📊 Commandes utiles:"
echo "  ./monitor-pi5.sh       # Monitoring Pi 5"
echo "  make status            # État des services"
echo "  vcgencmd measure_temp  # Température CPU"
echo ""
echo "⚙️  Pour utiliser la config Pi 5:"
echo "  cp config-pi5.json config.json"
EOF
