# Système de transfert de photos simplifié

Ce projet est une version allégée du système de transfert automatique de photos depuis un Raspberry Pi vers un serveur FTP/SFTP.

## Fonctionnalités principales

- Transfert automatique de photos vers FTP ou SFTP
- Interface web simple pour la configuration et l'utilisation
- Support des protocoles FTP et SFTP (si paramiko est installé)
- Configuration facile via interface web
- Gestion robuste des erreurs

## Installation

### Prérequis

- Python 3.6 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation rapide

1. Cloner le dépôt:
   ```bash
   git clone https://github.com/votre-compte/projet-ftp.git
   cd projet-ftp/Projet_FTP
   ```

2. Exécuter le script d'installation simplifié:
   ```bash
   python3 simple_setup.py
   ```

3. Démarrer l'application:
   ```bash
   python3 simple_webui.py
   ```

4. Accéder à l'interface web:
   - Ouvrir un navigateur et aller à `http://adresse-du-raspberry:8080`

### Installation comme service système

Pour que l'application démarre automatiquement au démarrage:

```bash
sudo bash install_service.sh
sudo systemctl start photo-ftp-web.service
```

## Utilisation

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
