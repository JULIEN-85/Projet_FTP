# Photo Transfer System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-4%2F5-red.svg)](https://www.raspberrypi.org/)

🚀 **Système automatique de transfert de photos** via Raspberry Pi avec interface web moderne.

Détecte automatiquement les nouvelles photos d'un appareil photo (ou téléphone) connecté en USB et les transfère vers un serveur FTP en temps réel.

![Demo Interface](https://via.placeholder.com/800x400/2196F3/FFFFFF?text=Interface+Web+Moderne)

## ✨ Fonctionnalités

### 🎯 **Core Features**
- ⚡ **Détection automatique** d'appareils photo et téléphones via gPhoto2
- 📤 **Transfert FTP automatique** avec retry et gestion d'erreurs
- 🌐 **Interface web moderne** pour configuration et monitoring
- 🔄 **Démarrage automatique** au boot (systemd)
- 📊 **Monitoring temps réel** avec statistiques
- 📝 **Logs détaillés** avec interface de consultation

### 📱 **Support Matériel**
- 📸 **Appareils photo** : Canon, Nikon, Sony, Fuji (gPhoto2 compatible)
- 📱 **Téléphones Android** : Mode PTP (Samsung, Google Pixel, OnePlus...)
- 🥧 **Raspberry Pi** : Pi 4, Pi 5 (optimisations spéciales Pi 5)
- 💾 **Stockage** : SD, USB, NAS

### 🛡️ **Fiabilité**
- 🔄 **Auto-récupération** en cas de panne réseau/USB
- 🔁 **Retry automatique** avec backoff exponentiel  
- 📈 **Monitoring système** (CPU, température, stockage)
- 💾 **Sauvegarde/restauration** complète

## 🎬 Démo Rapide

```bash
# Installation en une ligne
curl -sSL https://raw.githubusercontent.com/VOTRE_USERNAME/photo-transfer-system/main/install.sh | bash

# Configuration via interface web
http://raspberry-pi.local:8080

# C'est tout ! 🎉
```

## 🚀 Installation

### 📋 **Prérequis**
- Raspberry Pi 4 ou 5 avec Raspberry Pi OS
- Appareil photo compatible gPhoto2 ou téléphone Android
- Connexion réseau (WiFi/Ethernet)
- Serveur FTP (NAS, hébergeur, serveur personnel)

### 🔧 **Installation Automatique**

```bash
# 1. Cloner le repository
git clone https://github.com/VOTRE_USERNAME/photo-transfer-system.git
cd photo-transfer-system

# 2. Installation complète
chmod +x install.sh
./install.sh

# 3. Redémarrer pour activer les services
sudo reboot
```

### ⚙️ **Configuration**

1. **Accéder à l'interface web** : `http://[IP_DU_PI]:8080`
2. **Configurer FTP** : Serveur, identifiants, dossier de destination
3. **Tester les connexions** : Boutons de test intégrés
4. **Démarrer le service** : Bouton Start dans l'interface

## 📱 Support Téléphones

### Configuration Android
```bash
# Configuration automatique téléphone
make setup-phone

# Ou script dédié
./setup_phone.sh
```

**Sur le téléphone :**
1. Activer **Options développeur** (taper 7x sur "Numéro de build")
2. Activer **Débogage USB**
3. Connecter en USB et choisir **"Transfert de fichiers"** ou **"PTP"**
4. Autoriser l'accès depuis le Raspberry Pi

## 🎛️ Interface Web

### 🏠 **Dashboard**
- Vue d'ensemble du système
- Statistiques temps réel
- Contrôles Start/Stop
- Tests de connexion

### ⚙️ **Configuration**  
- Paramètres FTP complets
- Configuration appareil photo
- Réglages système
- Import/Export de config

### 📝 **Logs**
- Consultation en temps réel
- Filtrage par niveau (INFO, WARNING, ERROR)
- Auto-refresh
- Export des logs

## 🧪 Tests

### Tests Rapides
```bash
# Test complet du système
make test

# Tests individuels
make test-camera    # Appareil photo/téléphone
make test-ftp      # Connexion FTP
make test-web      # Interface web

# Configuration téléphone
make setup-phone
```

### Tests Manuel
```bash
# Test gPhoto2
gphoto2 --auto-detect
gphoto2 --capture-image-and-download

# Test interface web
python3 webui.py
# Puis http://localhost:8080
```

## 🔧 Utilisation

### Commandes Makefile
```bash
make help          # Aide complète
make install       # Installation
make start         # Démarrer services
make stop          # Arrêter services
make status        # État du système
make logs          # Logs temps réel
make backup        # Sauvegarde complète
make monitor-pi5   # Monitoring Pi 5
```

### Gestion des Services
```bash
# Services systemd
sudo systemctl status photo-ftp
sudo systemctl status photo-ftp-web

# Logs système
journalctl -u photo-ftp.service -f
```

## 🚀 Optimisations Raspberry Pi 5

### Installation optimisée Pi 5
```bash
# Installation standard
./install.sh

# Optimisations Pi 5
make optimize-pi5

# Redémarrage
sudo reboot

# Monitoring Pi 5
make monitor-pi5
```

### Avantages Pi 5
- **Performance 2-3x** supérieure
- **USB 3.0** : Transfert appareil photo plus rapide
- **Ethernet Gigabit** : Upload FTP accéléré
- **Gestion thermique** améliorée

## 📊 Architecture

```
photo-transfer-system/
├── main.py              # Service principal
├── webui.py            # Interface web Flask
├── config.json         # Configuration
├── install.sh          # Installation automatique
├── setup_phone.sh      # Configuration téléphones
├── templates/          # Templates web
├── static/            # CSS/JS
├── logs/              # Logs système
└── services/          # Services systemd
```

## 🔒 Sécurité

- **Configuration chiffrée** des mots de passe FTP
- **Interface web** limitée au réseau local par défaut
- **Logs sécurisés** sans informations sensibles
- **Permissions** utilisateur limitées
- **Isolation** des services

## 🐛 Dépannage

### Problèmes courants

#### Appareil photo non détecté
```bash
# Vérifier gPhoto2
gphoto2 --auto-detect

# Permissions USB
sudo usermod -a -G plugdev pi

# Redémarrer
sudo reboot
```

#### Téléphone non reconnu
```bash
# Configuration téléphone
make setup-phone

# Vérifier mode PTP
# Sur téléphone : Paramètres USB → PTP/Appareil photo
```

#### Problème FTP
```bash
# Test manuel
ftp votre-serveur.com

# Vérifier firewall
sudo ufw status

# Logs FTP
make logs | grep FTP
```

## 🤝 Contribution

1. **Fork** le projet
2. **Créer** une branche feature (`git checkout -b feature/AmazingFeature`)  
3. **Commit** vos changements (`git commit -m 'Add AmazingFeature'`)
4. **Push** vers la branche (`git push origin feature/AmazingFeature`)
5. **Ouvrir** une Pull Request

### Développement
```bash
# Environnement de dev
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Tests
make test
python3 test_system.py
```

## 📝 Changelog

### v1.0.0 (2025-06-17)
- 🎉 Version initiale
- ✅ Support appareils photo gPhoto2
- ✅ Support téléphones Android  
- ✅ Interface web complète
- ✅ Optimisations Raspberry Pi 5
- ✅ Installation automatique
- ✅ Documentation complète

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour les détails.

## 🙏 Remerciements

- **gPhoto2** : Bibliothèque de gestion d'appareils photo
- **Flask** : Framework web Python
- **Bootstrap** : Framework CSS
- **Raspberry Pi Foundation** : Matériel exceptionnel

## 📞 Support

- 📖 **Documentation** : [Wiki](https://github.com/VOTRE_USERNAME/photo-transfer-system/wiki)
- 🐛 **Issues** : [GitHub Issues](https://github.com/VOTRE_USERNAME/photo-transfer-system/issues)
- 💬 **Discussions** : [GitHub Discussions](https://github.com/VOTRE_USERNAME/photo-transfer-system/discussions)

---

⭐ **N'oubliez pas de mettre une étoile si ce projet vous aide !**

📸 **Bon transfert de photos !** 🚀
