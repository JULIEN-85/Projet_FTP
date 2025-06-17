# Photo Transfer System - Version Économique

🔋 **Système optimisé pour Raspberry Pi avec consommation d'énergie minimale**

Transfert automatique de photos d'un appareil photo/téléphone vers serveur FTP.

## 🚀 Installation Rapide

```bash
# Cloner et installer
git clone https://github.com/JULIEN-85/Projet_FTP.git
cd Projet_FTP
chmod +x install_minimal.sh
./install_minimal.sh

# Redémarrer
sudo reboot

# Activer et démarrer
sudo systemctl enable photo-ftp photo-ftp-web
sudo systemctl start photo-ftp photo-ftp-web
```

## ⚙️ Configuration

1. **Interface web** : http://[IP_DU_PI]:8080
2. **Configurer FTP** : Serveur, identifiants, dossier
3. **Connecter appareil** : USB (mode PTP pour téléphones)
4. **Démarrer** : Bouton Start dans l'interface

## 📱 Support Matériel

### Appareils Photo
- Canon, Nikon, Sony (compatibles gPhoto2)
- Connexion USB directe

### Téléphones Android
- Mode PTP activé
- Options développeur → Débogage USB
- Samsung, Google Pixel, OnePlus recommandés

## 🔧 Commandes Utiles

```bash
make help          # Aide
make status        # État des services  
make logs          # Voir les logs
make start/stop    # Contrôle services
make test          # Tests rapides
make info          # Infos système
```

## 🔋 Optimisations Énergétiques

### Automatiques
- **Mode veille** après 5 min d'inactivité
- **Fréquence CPU** adaptative selon la charge
- **Mémoire GPU** réduite (64MB)
- **Garbage collection** optimisé
- **Services** avec priorité basse

### Configuration
- **Check interval** : 10s (vs 5s standard)
- **Timeout FTP** : 30s optimisé
- **Queue limitée** : 10 photos max en mémoire
- **Logs** rotation automatique

### Mesures Optionnelles
```bash
# Désactiver WiFi (si Ethernet utilisé)
echo "dtoverlay=disable-wifi" | sudo tee -a /boot/config.txt

# Désactiver Bluetooth
echo "dtoverlay=disable-bt" | sudo tee -a /boot/config.txt

# Gouverneur CPU économique
echo 'GOVERNOR="powersave"' | sudo tee /etc/default/cpufrequtils
```

## 📊 Monitoring

### Interface Web
- Statistiques temps réel
- Température CPU
- Usage mémoire
- Mode d'alimentation

### Ligne de commande
```bash
# Température
vcgencmd measure_temp

# Fréquence CPU
vcgencmd measure_clock arm

# Mémoire
free -h

# État services
make status
```

## 🔍 Dépannage

### Appareil non détecté
```bash
# Test gPhoto2
gphoto2 --auto-detect

# Permissions
sudo usermod -a -G plugdev pi
sudo reboot
```

### Interface web inaccessible
```bash
# Vérifier service
systemctl status photo-ftp-web

# Redémarrer
sudo systemctl restart photo-ftp-web
```

### Consommation élevée
```bash
# Vérifier température
vcgencmd measure_temp

# Mode économique forcé
sudo cpufreq-set -g powersave

# Logs pour debug
make logs
```

## 📋 Configuration Type

```json
{
    "ftp": {
        "server": "votre-nas.local",
        "port": 21,
        "username": "photo_user",
        "password": "mot_de_passe",
        "directory": "/photos",
        "passive_mode": true,
        "timeout": 30
    },
    "camera": {
        "auto_detect": true,
        "download_path": "photos",
        "delete_after_upload": true
    },
    "system": {
        "log_level": "INFO",
        "check_interval": 10,
        "max_retries": 3,
        "idle_threshold": 300,
        "enable_power_management": true,
        "max_concurrent_transfers": 2
    }
}
```

## 🎯 Performances

### Consommation Typique
- **Idle** : ~2W (mode veille)
- **Transfert** : ~4W (activité)
- **Température** : <60°C en continu

### Autonomie Estimée
- **Batterie 10000mAh** : ~15h en activité, ~25h en veille
- **Pi 4** : Optimisé pour fonctionnement 24/7
- **Pi 5** : Performance supérieure avec même consommation

## ⚠️ Remarques Importantes

- **Toujours utiliser un bon câble USB** pour appareils photo
- **Garder le téléphone déverrouillé** pendant transfert
- **Surveiller la température** en été
- **Nettoyer les logs** régulièrement (`make clean`)

## 📄 Licence

MIT License - Utilisation libre pour projets personnels et commerciaux.

---

**Système optimisé pour un fonctionnement 24/7 avec consommation minimale ! 🔋**
