#!/bin/bash
# Script d'optimisation post-installation pour économie d'énergie maximale

echo "🔋 Optimisation énergétique avancée du Raspberry Pi"
echo ""

# Configuration du gouverneur CPU
echo "⚙️  Configuration CPU..."
echo 'GOVERNOR="ondemand"' | sudo tee /etc/default/cpufrequtils
sudo systemctl enable cpufrequtils

# Optimisation GPU
echo "🎮 Optimisation GPU..."
if ! grep -q "gpu_mem=64" /boot/config.txt; then
    echo "gpu_mem=64" | sudo tee -a /boot/config.txt
fi

# Désactiver services non nécessaires
echo "🚫 Désactivation services non essentiels..."
sudo systemctl disable bluetooth
sudo systemctl disable hciuart
sudo systemctl disable dphys-swapfile  # Pas de swap sur SD

# Configuration réseau économique
echo "📡 Optimisation réseau..."
# Désactiver WiFi power management si utilisé
if iwconfig 2>/dev/null | grep -q "wlan0"; then
    sudo iwconfig wlan0 power off
fi

# Optimisation logs
echo "📝 Configuration logs..."
sudo tee /etc/logrotate.d/photo-transfer > /dev/null << 'EOF'
/home/pi/photo-ftp/logs/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
    copytruncate
}
EOF

# Configuration sysctl pour économie
echo "🔧 Optimisations système..."
sudo tee -a /etc/sysctl.conf > /dev/null << 'EOF'

# Optimisations Photo Transfer System
vm.swappiness=1
vm.dirty_ratio=3
vm.dirty_background_ratio=1
net.core.rmem_default=262144
net.core.wmem_default=262144
EOF

# Configuration tmpfs pour logs temporaires
echo "💾 Configuration tmpfs..."
if ! grep -q "tmpfs.*photo-ftp.*logs" /etc/fstab; then
    echo "tmpfs /home/pi/photo-ftp/logs tmpfs defaults,size=32M,uid=pi,gid=pi 0 0" | sudo tee -a /etc/fstab
fi

# Crontab pour nettoyage automatique
echo "🗑️  Configuration nettoyage automatique..."
(crontab -l 2>/dev/null; echo "0 2 * * * find /home/pi/photo-ftp/photos -mtime +7 -delete") | crontab -
(crontab -l 2>/dev/null; echo "0 3 * * * sudo journalctl --vacuum-time=3d") | crontab -

echo ""
echo "✅ Optimisations appliquées!"
echo ""
echo "📋 Optimisations activées:"
echo "   🔋 Gouverneur CPU adaptatif"
echo "   🎮 Mémoire GPU minimale (64MB)"
echo "   🚫 Services non essentiels désactivés"
echo "   📝 Rotation automatique des logs"
echo "   💾 Logs en RAM (tmpfs)"
echo "   🗑️  Nettoyage automatique"
echo ""
echo "⚠️  Redémarrage nécessaire pour appliquer toutes les optimisations"
echo "sudo reboot"
