# Système de Transfert Automatique de Photos

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-compatible-red.svg)](https://www.raspberrypi.org/)

Un système autonome basé sur Raspberry Pi pour transférer automatiquement les photos prises avec un appareil photo numérique vers un serveur FTP, avec une interface web de configuration.

## 🎯 Caractéristiques

- **🔄 Transfert automatique** : Détection et upload automatique des nouvelles photos
- **📷 Compatible gPhoto2** : Support des principales marques d'appareils photo (Canon, Nikon, Sony...)
- **🌐 Interface web intuitive** : Configuration et monitoring via navigateur
- **🚀 Démarrage automatique** : Service systemd pour démarrage au boot
- **📊 Monitoring en temps réel** : Statut, logs et statistiques
- **🔒 Robuste** : Gestion d'erreurs, retry automatique, logs détaillés
- **⚡ Faible consommation** : Optimisé pour fonctionnement sur batterie

## 📋 Prérequis

### Hardware
- **Raspberry Pi 3B+ ou plus récent** (Pi 4 et Pi 5 recommandés)
- **Raspberry Pi 5** : Performances optimales avec support USB 3.0
- Carte SD (16GB minimum, 32GB recommandé pour Pi 5)
- Appareil photo compatible gPhoto2
- Câble USB pour connecter l'appareil photo
- Connexion réseau (WiFi ou Ethernet Gigabit sur Pi 5)

### Software
- Raspberry Pi OS (Debian 10+ / Bullseye ou plus récent)
- Python 3.7+
- gPhoto2
- Accès à un serveur FTP

### Appareils photo testés
- Canon EOS (série 5D, 6D, 7D, 80D, 90D...)
- Nikon DSLR (D3500, D5600, D750, D850...)
- Sony Alpha (A7, A7R, A6000...)

> 💡 Vérifiez la compatibilité de votre appareil : [Liste gPhoto2](http://gphoto.org/proj/libgphoto2/support.php)

## 🚀 Installation Rapide

### 1. Téléchargement
```bash
cd /home/pi
git clone <votre-repo> photo-ftp
cd photo-ftp
```

### 2. Installation automatique
```bash
chmod +x install.sh
./install.sh
```

Le script d'installation va :
- Installer les dépendances système
- Configurer gPhoto2
- Installer l'environnement Python
- Configurer les services systemd
- Paramétrer les permissions USB

### 3. Redémarrage
```bash
sudo reboot
```

### 4. Configuration
1. Connectez votre appareil photo en USB
2. Accédez à l'interface web : `http://[IP_RASPBERRY]:8080`
3. Configurez vos paramètres FTP
4. Testez les connexions
5. Démarrez le service

## 🎛️ Configuration

### Interface Web
L'interface web est accessible sur le port 8080 et propose :

- **🏠 Accueil** : Vue d'ensemble, statut du système, contrôles
- **⚙️ Configuration** : Paramètres FTP, appareil photo, système  
- **📝 Logs** : Consultation des logs en temps réel

### Paramètres FTP
```json
{
  "ftp": {
    "server": "ftp.example.com",
    "port": 21,
    "username": "votre_nom",
    "password": "votre_mot_de_passe",
    "directory": "/uploads",
    "passive_mode": true
  }
}
```

### Paramètres Appareil Photo
```json
{
  "camera": {
    "auto_detect": true,
    "download_path": "/tmp/photos",
    "delete_after_upload": true
  }
}
```

### Paramètres Système
```json
{
  "system": {
    "log_level": "INFO",
    "check_interval": 5,
    "max_retries": 3,
    "web_port": 8080,
    "web_host": "0.0.0.0"
  }
}
```

## 🔧 Utilisation

### Démarrage Manuel
```bash
# Démarrer le service principal
sudo systemctl start photo-ftp.service

# Démarrer l'interface web  
sudo systemctl start photo-ftp-web.service
```

### Démarrage Automatique
```bash
# Activer le démarrage automatique
sudo systemctl enable photo-ftp.service
sudo systemctl enable photo-ftp-web.service
```

### Contrôle via Interface Web
1. Ouvrez `http://[IP_RASPBERRY]:8080`
2. Vérifiez le statut des connexions
3. Cliquez sur "Start" pour démarrer le transfert
4. Surveillez les logs en temps réel

## 📊 Monitoring

### Logs Système
```bash
# Logs du service principal
journalctl -u photo-ftp.service -f

# Logs de l'interface web
journalctl -u photo-ftp-web.service -f

# Logs dans fichier
tail -f /home/pi/photo-ftp/logs/photo_transfer.log
```

### Statut des Services
```bash
# Vérifier le statut
sudo systemctl status photo-ftp.service
sudo systemctl status photo-ftp-web.service

# Redémarrer si nécessaire
sudo systemctl restart photo-ftp.service
```

## 🧪 Tests

### Test Automatique
```bash
python3 test_system.py
```

### Tests Manuels
```bash
# Test appareil photo
gphoto2 --auto-detect

# Test capture photo
gphoto2 --capture-image-and-download

# Test connexion FTP (exemple)
ftp ftp.example.com
```

## 🧪 **Comment Tester le Système**

### 🖥️ **Test Local (Windows/PC)**

#### Test Rapide sur PC
```powershell
# 1. Ouvrir PowerShell dans le dossier projet
cd C:\Users\julie\Desktop\projet_FTP

# 2. Test automatique Windows
test_windows.bat

# 3. Ou test Python détaillé
python test_system.py
```

#### Test de l'Interface Web
```powershell
# 1. Installer les dépendances
pip install flask werkzeug

# 2. Lancer l'interface web
python webui.py

# 3. Ouvrir dans le navigateur
# http://localhost:8080
```

### 🥧 **Test sur Raspberry Pi**

#### Installation et Test Complet
```bash
# 1. Copier les fichiers sur le Pi
scp -r projet_FTP pi@[IP_DU_PI]:/home/pi/

# 2. Se connecter au Pi
ssh pi@[IP_DU_PI]

# 3. Installation et test
cd /home/pi/projet_FTP
make install
make test

# 4. Test interface web
make test-web
# Accéder à: http://[IP_DU_PI]:8080
```

#### Tests Individuels
```bash
# Test appareil photo
make test-camera
gphoto2 --auto-detect

# Test FTP
make test-ftp

# Test complet
python3 test_system.py

# Monitoring
make status
make logs
```

### 📱 **Test de l'Interface Web**

1. **Page d'Accueil** (`/`)
   - ✅ Statistiques visibles
   - ✅ Tests de connexion
   - ✅ Contrôles Start/Stop

2. **Configuration** (`/config`)
   - ✅ Paramètres FTP modifiables
   - ✅ Sauvegarde fonctionne
   - ✅ Tests en temps réel

3. **Logs** (`/logs`)
   - ✅ Affichage des logs
   - ✅ Filtrage par niveau
   - ✅ Auto-refresh

### 🔍 **Test du Workflow Complet**

```bash
# 1. Connecter appareil photo USB
# 2. Configurer FTP via interface web
# 3. Démarrer le service
make start

# 4. Prendre une photo sur l'appareil
# 5. Vérifier dans l'interface web :
#    - Détection automatique
#    - Upload FTP
#    - Logs détaillés
```

### ✅ **Checklist de Test**

#### Tests de Base
- [ ] Installation réussie
- [ ] Interface web accessible  
- [ ] Configuration sauvegardée
- [ ] Détection appareil photo
- [ ] Connexion FTP testée
- [ ] Services démarrent/arrêtent
- [ ] Logs visibles

#### Tests Avancés
- [ ] Démarrage automatique
- [ ] Gestion d'erreurs
- [ ] Retry automatique
- [ ] Monitoring temps réel
- [ ] Performance sur gros fichiers

## 🔍 Dépannage

### Problèmes Courants

#### Appareil photo non détecté
```bash
# Vérifier la connexion USB
lsusb

# Tester gPhoto2
gphoto2 --auto-detect

# Vérifier les permissions
groups $USER
# doit inclure 'plugdev'
```

#### Erreur de connexion FTP
- Vérifiez les paramètres de connexion
- Testez le mode passif/actif
- Vérifiez les règles de firewall
- Contrôlez les permissions du dossier de destination

#### Service ne démarre pas
```bash
# Vérifier les logs
journalctl -u photo-ftp.service -n 50

# Vérifier le fichier de config
python3 -c "import json; print(json.load(open('config.json')))"

# Tester le script manuellement
cd /home/pi/photo-ftp
python3 main.py
```

### Logs de Debug
Pour plus de détails, activez le mode DEBUG :
1. Interface web → Configuration → Niveau de log → DEBUG
2. Ou éditez `config.json` : `"log_level": "DEBUG"`

## 📁 Structure du Projet

```
photo-ftp/
├── main.py                 # Script principal
├── webui.py               # Interface web Flask
├── config.json            # Configuration
├── requirements.txt       # Dépendances Python
├── install.sh            # Script d'installation
├── uninstall.sh          # Script de désinstallation
├── test_system.py        # Tests automatiques
├── photo-ftp.service     # Service systemd principal
├── photo-ftp-web.service # Service systemd web
├── logs/                 # Dossier des logs
├── templates/            # Templates HTML
│   ├── base.html
│   ├── index.html
│   ├── config.html
│   └── logs.html
└── static/              # Fichiers statiques (CSS, JS)
```

## 🔒 Sécurité

### Recommandations
- Changez le mot de passe par défaut du Raspberry Pi
- Utilisez des connexions FTP sécurisées (FTPS/SFTP) si possible
- Restreignez l'accès réseau à l'interface web
- Surveillez régulièrement les logs

### Permissions
Le système fonctionne avec l'utilisateur `pi` et les groupes appropriés pour l'accès USB aux appareils photo.

## 🚀 Fonctionnalités Avancées

### Configuration Multiple
Vous pouvez créer plusieurs profils de configuration :
```bash
cp config.json config_studio.json
cp config.json config_event.json
# Puis charger avec : python3 main.py --config config_studio.json
```

### Intégration Scripts
Le système peut être étendu avec des scripts personnalisés :
- Post-traitement des images
- Notifications (email, webhook)
- Sauvegarde multiple

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer des améliorations
- Ajouter des fonctionnalités
- Améliorer la documentation

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- [gPhoto2](http://gphoto.org/) pour l'interface avec les appareils photo
- [Flask](https://flask.palletsprojects.com/) pour l'interface web
- La communauté Raspberry Pi

## 📞 Support

Si vous rencontrez des problèmes :
1. Consultez la section dépannage
2. Vérifiez les logs
3. Lancez les tests automatiques
4. Ouvrez une issue sur GitHub

---

**Système de Transfert Automatique de Photos** - Automatisez votre workflow photo avec votre Raspberry Pi ! 📸🚀

## 🚀 Optimisations Raspberry Pi 5

### Installation optimisée pour Pi 5
```bash
# Installation standard
./install.sh

# Puis optimisations Pi 5
make optimize-pi5

# Redémarrage pour appliquer les optimisations
sudo reboot
```

### Avantages du Pi 5
- **Performance 2-3x supérieure** au Pi 4
- **USB 3.0** : Transfert plus rapide depuis l'appareil photo
- **Ethernet Gigabit** : Upload FTP accéléré
- **Plus de RAM** : Gestion de fichiers RAW volumineux
- **Gestion thermique améliorée** : Fonctionnement stable

### Monitoring Pi 5
```bash
make monitor-pi5     # Monitoring complet Pi 5
vcgencmd measure_temp # Température CPU
vcgencmd measure_clock arm # Fréquence CPU
```

### Configuration recommandée Pi 5
```json
{
  "system": {
    "check_interval": 2,        # Plus rapide grâce au CPU
    "worker_threads": 4,        # Multi-threading
    "memory_limit": "2GB"       # Plus de RAM disponible
  },
  "camera": {
    "concurrent_downloads": 2,  # Téléchargements parallèles
    "max_file_size": "500MB"    # Support fichiers RAW
  }
}
```

## 📱 **Utilisation avec un Téléphone (Alternative Appareil Photo)**

### 🔍 **Compatibilité Téléphones**

#### ✅ **Téléphones Compatibles gPhoto2**
- **Android en mode PTP** : La plupart des Android récents
- **iPhone avec adaptateur** : Via Lightning vers USB-A/C
- **Téléphones avec mode "Appareil photo USB"**

#### 📋 **Configuration Requise**
```bash
# Sur le téléphone Android :
# 1. Activer "Options développeur"
# 2. Activer "Débogage USB" 
# 3. Choisir "Transfert de fichiers (MTP)" ou "PTP (Appareil photo)"
# 4. Connecter via câble USB
```

### 🔧 **Configuration pour Android**

#### Étape 1 : Préparer le téléphone
```
1. Paramètres → À propos du téléphone
2. Appuyez 7 fois sur "Numéro de build"
3. Options développeur → Débogage USB (ON)
4. Connecter en USB → Choisir "PTP" ou "Transfert photos"
```

#### Étape 2 : Test de détection
```bash
# Sur Raspberry Pi
sudo apt install gphoto2 libgphoto2-dev

# Test de détection
gphoto2 --auto-detect
# Devrait afficher votre téléphone si compatible

# Liste des appareils supportés
gphoto2 --list-cameras | grep -i android
gphoto2 --list-cameras | grep -i samsung
gphoto2 --list-cameras | grep -i huawei
```

#### Étape 3 : Test de capture
```bash
# Test capture (si supporté)
gphoto2 --capture-image-and-download

# Ou récupération des photos existantes
gphoto2 --get-all-files
```

### 📱 **Téléphones Testés et Compatibilité**

| Marque | Modèles | gPhoto2 | Notes |
|--------|---------|---------|--------|
| **Samsung** | Galaxy S/Note series | ✅ Excellent | Mode PTP natif |
| **Google** | Pixel series | ✅ Bon | Support PTP standard |
| **Huawei** | P/Mate series | ⚠️ Partiel | Selon version Android |
| **OnePlus** | Série Nord/Pro | ✅ Bon | Configuration PTP |
| **Xiaomi** | Mi/Redmi | ⚠️ Variable | Dépend du firmware |
| **iPhone** | Tous modèles | ❌ Limité | Nécessite libimobiledevice |

### ⚙️ **Configuration du Système pour Téléphones**

#### Mise à jour de la configuration
```json
{
  "camera": {
    "auto_detect": true,
    "device_type": "phone",
    "download_path": "phone_photos",
    "delete_after_upload": false,
    "phone_mode": {
      "connection_type": "PTP",
      "wait_for_unlock": true,
      "retry_connection": 5
    }
  }
}
```

#### Script de détection téléphone
```bash
#!/bin/bash
# detect_phone.sh - Script de détection spécial téléphones

echo "🔍 Recherche de téléphones connectés..."

# Vérifier les périphériques USB
lsusb | grep -E "(Samsung|Google|Huawei|OnePlus|Xiaomi)"

# Test gPhoto2
echo "📱 Test gPhoto2..."
gphoto2 --auto-detect

# Test MTP (alternative)
echo "📁 Test MTP..."
mtp-detect

# Conseils selon le résultat
if gphoto2 --auto-detect | grep -q "usb:"; then
    echo "✅ Téléphone détecté en mode PTP"
    echo "🎯 Configuration recommandée : PTP mode"
else
    echo "⚠️ Téléphone non détecté en PTP"
    echo "💡 Vérifiez :"
    echo "   - Mode PTP activé sur le téléphone"
    echo "   - Débogage USB activé"
    echo "   - Téléphone déverrouillé"
    echo "   - Autorisation de débogage accordée"
fi
```

### 📸 **Workflow avec Téléphone**

#### Mode 1 : Capture Automatique (si supportée)
```python
# Dans main.py - adaptation pour téléphones
def detect_phone_photos(self):
    """Détection spéciale pour téléphones"""
    try:
        # Vérifier si téléphone connecté et déverrouillé
        result = subprocess.run(['gphoto2', '--auto-detect'], 
                              capture_output=True, text=True)
        
        if 'usb:' in result.stdout:
            # Téléphone détecté, vérifier nouvelles photos
            return self.get_new_phone_photos()
        else:
            self.logger.warning("Téléphone non détecté - vérifier connexion PTP")
            return []
            
    except Exception as e:
        self.logger.error(f"Erreur détection téléphone: {e}")
        return []

def get_new_phone_photos(self):
    """Récupère les nouvelles photos du téléphone"""
    try:
        # Lister les fichiers sur le téléphone
        result = subprocess.run(['gphoto2', '--list-files'], 
                              capture_output=True, text=True)
        
        # Télécharger les nouvelles photos seulement
        photos = []
        for line in result.stdout.split('\n'):
            if '.jpg' in line.lower() or '.jpeg' in line.lower():
                # Extraire nom fichier et télécharger
                photo_name = self.extract_photo_name(line)
                if self.is_new_photo(photo_name):
                    downloaded_path = self.download_phone_photo(photo_name)
                    if downloaded_path:
                        photos.append(downloaded_path)
        
        return photos
        
    except Exception as e:
        self.logger.error(f"Erreur récupération photos téléphone: {e}")
        return []
```

#### Mode 2 : Surveillance Dossier (Alternative)
```python
# Alternative : Surveiller le dossier de synchronisation
def setup_phone_sync_folder(self):
    """Configure la surveillance d'un dossier de sync téléphone"""
    sync_folders = [
        "/media/pi/phone/DCIM/Camera",  # Android monté
        "/home/pi/phone_sync",          # Dossier de sync
        "/mnt/phone/Pictures"           # Autre point de montage
    ]
    
    for folder in sync_folders:
        if os.path.exists(folder):
            self.logger.info(f"Surveillance dossier téléphone: {folder}")
            return folder
    
    self.logger.warning("Aucun dossier de sync téléphone trouvé")
    return None
```

### 🔧 **Dépannage Téléphones**

#### Problèmes Courants
```bash
# Téléphone non détecté
sudo lsusb  # Vérifier connexion USB
sudo dmesg | tail  # Messages système

# Permissions USB
sudo usermod -a -G plugdev pi
sudo udevadm control --reload

# Test manuel MTP
sudo apt install mtp-tools
mtp-detect
mtp-files
```

#### Règles udev pour téléphones
```bash
# /etc/udev/rules.d/99-phone-gphoto.rules
# Samsung
SUBSYSTEM=="usb", ATTR{idVendor}=="04e8", MODE="0664", GROUP="plugdev"
# Google Pixel
SUBSYSTEM=="usb", ATTR{idVendor}=="18d1", MODE="0664", GROUP="plugdev"
# Huawei
SUBSYSTEM=="usb", ATTR{idVendor}=="12d1", MODE="0664", GROUP="plugdev"

# Recharger les règles
sudo udevadm control --reload
sudo udevadm trigger
```

### 💡 **Conseils pour Téléphones**

#### ✅ **Bonnes Pratiques**
- **Gardez le téléphone déverrouillé** pendant le transfert
- **Utilisez un câble USB de qualité** (pas de charge seule)
- **Configurez "Ne pas charger seulement"** sur Android
- **Accordez les autorisations** de débogage USB
- **Testez en mode PTP** avant MTP

#### ⚠️ **Limitations**
- **Capture distante limitée** selon le modèle
- **Nécessite interaction utilisateur** (déverrouillage)
- **Moins fiable** qu'un vrai appareil photo
- **Dépendant de la version Android**

### 🎯 **Configuration Recommandée**

Pour utiliser un téléphone comme appareil photo :

1. **Téléphone Samsung/Google/OnePlus** (meilleure compatibilité)
2. **Mode PTP activé** dans les options développeur
3. **Câble USB-C vers USB-A** de qualité
4. **Débogage USB autorisé** pour le Raspberry Pi
5. **Configuration "delete_after_upload": false** (sécurité)

Le système fonctionnera, mais sera **moins automatique** qu'avec un vrai appareil photo ! 📱📸
