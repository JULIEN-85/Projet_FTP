# Système de transfert de photos simplifié

Ce projet est une version allégée du système de transfert automatique de photos depuis un Raspberry Pi vers un serveur FTP/SFTP, conçu pour détecter automatiquement les nouvelles photos JPG et les transférer instantanément.

## Fonctionnalités principales

- Transfert automatique des photos JPG vers FTP
- Détection en temps réel de nouvelles photos dans /tmp/photos
- Support des appareils photo Nikon D800 et autres caméras produisant des fichiers JPG
- Contournement des problèmes FTPS/TLS via lftp
- Interface web simple pour la configuration et le suivi (via simple_webui.py)
- Gestion robuste des erreurs et des problèmes de connectivité réseau

## Composants du système

### Scripts principaux

- **auto_jpg_transfer.py**: Détecte automatiquement les nouveaux fichiers JPG et les transfère via FTP
- **lftp_send_jpg.sh**: Script bash utilisant lftp pour transférer uniquement les fichiers JPG
- **lftp_send_photos.sh**: Script bash utilisant lftp pour transférer tous les fichiers (non filtré)
- **simple_webui.py**: Interface web pour la configuration et le suivi
- **config_util.py**: Utilitaire de gestion de la configuration
- **simple_transfer.py**: Fonctions de base pour le transfert de fichiers

### Scripts de service

- **install_auto_transfer_service.sh**: Installation du service de surveillance automatique
- **auto_jpg_transfer.service**: Définition du service systemd
- **install_service.sh**: Installation du service web

### Scripts de test et utilitaires

- **test_auto_transfer.sh**: Crée un fichier JPG de test pour valider la détection et le transfert
- **test_camera_detection.py**: Test de détection de l'appareil photo
- **test_protocols.py**: Test des différents protocoles de transfert
- **check_camera.sh**: Vérification de la détection de l'appareil photo
- **optimize_project.sh**: Optimisation des performances du projet

## Installation

### Prérequis

- Python 3.6 ou supérieur
- pip (gestionnaire de paquets Python)
- lftp (`apt install lftp`)
- python3-watchdog (`apt install python3-watchdog`)

### Installation rapide

1. Cloner le dépôt:
   ```bash
   git clone https://github.com/votre-compte/projet-ftp.git
   cd projet-ftp/Projet_FTP
   ```

2. Installer les dépendances Python:
   ```bash
   pip3 install -r requirements.txt
   ```

3. Installer lftp et watchdog:
   ```bash
   sudo apt install lftp python3-watchdog
   ```

4. Configurer l'application:
   ```bash
   # Éditer la configuration selon vos besoins
   nano config.json
   ```

### Installation comme service système

Pour que la détection automatique démarre au démarrage du système:

```bash
sudo bash install_auto_transfer_service.sh
```

Pour l'interface web:

```bash
sudo bash install_service.sh
```

### Interface web

Pour démarrer l'interface web:

```bash
python3 simple_webui.py
```

Puis accéder à l'interface via `http://adresse-ip:8080`

## Configuration

Le fichier `config.json` contient la configuration du système:

- Détails de connexion FTP (serveur, identifiants, répertoire)
- Chemin de téléchargement des photos
- Option de suppression après transfert
- Paramètres de journalisation et d'intervalle de vérification

## Résolution des problèmes

- Consulter les logs dans `logs/auto_transfer.log` et `logs/webui.log`
- Exécuter `diagnose_ftp.py` pour diagnostiquer les problèmes de connexion FTP
- Vérifier que lftp est correctement installé: `which lftp`
- Vérifier les permissions sur les dossiers de destination

## Utilisation

### Détection et transfert automatiques

Le système détecte automatiquement les nouvelles photos JPG dans `/tmp/photos` et les transfère immédiatement vers le serveur FTP configuré.

Pour démarrer manuellement:

```bash
python3 auto_jpg_transfer.py
```

### Transfert manuel de fichiers JPG

```bash
# Transférer un seul fichier JPG
./lftp_send_jpg.sh /chemin/vers/photo.jpg

# Transférer tous les fichiers JPG dans /tmp/photos
./lftp_send_jpg.sh
```

### Test du système

```bash
# Créer un fichier JPG de test pour vérifier le transfert automatique
./test_auto_transfer.sh
```

### Configuration

1. Accéder à l'interface web
2. Aller dans "Configuration"
3. Remplir les paramètres FTP/SFTP:
   - Serveur (nom d'hôte ou IP)
   - Port (21 pour FTP, 22 ou 2222 pour SFTP)
   - Nom d'utilisateur et mot de passe
   - Répertoire distant
4. Configurer les paramètres de la caméra:
   - Répertoire local de téléchargement des photos
   - Options de suppression automatique
5. Enregistrer la configuration

### Vérification de la connexion

1. Aller dans "État"
2. Cliquer sur "Tester la connexion" pour vérifier les paramètres

### Démarrer le service

1. Aller dans "État"
2. Cliquer sur "Démarrer le service"

### Upload manuel

1. Aller dans "Upload manuel"
2. Sélectionner un fichier image
3. Cliquer sur "Uploader"

## Structure des fichiers

- `simple_webui.py`: Interface web simplifiée 
- `simple_main.py`: Application principale allégée
- `simple_transfer.py`: Module de transfert FTP/SFTP unifié
- `config_util.py`: Gestion de la configuration
- `config.json`: Fichier de configuration
- `logs/`: Répertoire des journaux
- `templates/`: Modèles pour l'interface web

## Aide et dépannage

### Problèmes courants

1. **Erreur de connexion FTP/SFTP**
   - Vérifier les paramètres de connexion
   - S'assurer que le serveur est accessible
   - Vérifier que le nom d'utilisateur et le mot de passe sont corrects

2. **Problème de permissions**
   - Vérifier que le répertoire local existe et est accessible en écriture
   - Vérifier que le répertoire distant existe et est accessible en écriture

3. **Photos non transférées**
   - Vérifier le chemin du répertoire local
   - Vérifier que les photos sont dans un format pris en charge (.jpg, .jpeg, .png, .raw)

### Logs

Les fichiers de journaux se trouvent dans le répertoire `logs/`:
- `photo_transfer.log`: Journal du service de transfert
- `webui.log`: Journal de l'interface web

## Personnalisation

Le projet est conçu pour être simple et facile à modifier:

1. Modifier les templates dans le répertoire `templates/`
2. Ajouter des fonctionnalités à `simple_main.py` ou `simple_webui.py`
3. Adapter la configuration dans `config.json`

## Économie d'énergie

Cette version simplifiée est optimisée pour une faible consommation d'énergie sur Raspberry Pi:
- Utilisation minimale des ressources
- Intervalles de vérification configurables
- Fermeture propre des connexions inutilisées
