# 📷 Système de Transfert Automatique de Photos

Un système robuste pour transférer automatiquement des photos depuis un appareil photo (notamment Nikon D800) vers un serveur FTP/FTPS, avec une solution fiable pour éviter les fichiers vides (0 octet).

## 🌟 Fonctionnalités principales

- ✅ **Transfert automatique** des photos vers serveur FTP/FTPS/SFTP
- ✅ **Détection en temps réel** de nouvelles photos dans le dossier local
- ✅ **Solution fiable** au problème des fichiers vides (0 octet) transférés via FTPS
- ✅ **Interface web** pour configuration, monitoring et contrôle
- ✅ **Compatible** avec Nikon D800 et autres appareils photo numériques
- ✅ **Fallback automatique** vers curl en cas d'échec du transfert FTPS
- ✅ **Purge simplifiée** des photos locales via bouton dans l'interface web

## 🔍 Solution au problème des fichiers vides (0 octet)

Cette version intègre une solution complète et définitive au problème des photos qui arrivaient vides (taille 0 octet) sur le serveur FTPS :

1. **Tentative principale** avec Python ftplib (optimisé)
2. **Fallback automatique** vers curl si le transfert échoue
3. **Vérification de taille** pour garantir l'intégrité des fichiers

## 📋 Prérequis

- Python 3.6+
- curl (`apt install curl`)
- Bibliothèques Python : Flask, ftplib (voir requirements.txt)

## 🚀 Installation

### Installation simple

1. Cloner ou télécharger le projet :
   ```bash
   git clone https://github.com/votre-repo/projet_ftp.git
   cd projet_ftp/Projet_FTP
   ```

2. Installer les dépendances :
   ```bash
   pip3 install -r requirements.txt
   ```

3. Configurer l'application :
   ```bash
   # Éditer selon vos besoins
   nano config.json
   ```

### Installation comme service système

Pour que l'interface web démarre automatiquement au démarrage :

```bash
sudo bash install_service.sh
```

## ⚙️ Configuration

Le fichier `config.json` contient tous les paramètres :

```json
{
    "ftp": {
        "server": "192.168.1.22",      # Adresse du serveur
        "port": 21,                    # Port (21 pour FTP/FTPS, 22 pour SFTP)
        "username": "utilisateur",     # Nom d'utilisateur
        "password": "motdepasse",      # Mot de passe
        "directory": "/photos",        # Répertoire distant
        "protocol": "ftp",            # "ftp", "ftps" ou "sftp"
        "passive_mode": true,          # Mode passif
        "use_ftps": true               # Utiliser FTPS (true) ou FTP (false)
    },
    "camera": {
        "auto_detect": true,           # Détection automatique de l'appareil
        "download_path": "/tmp/photos", # Dossier local de téléchargement
        "delete_after_upload": false   # Supprimer après transfert
    },
    "system": {
        "log_level": "INFO",           # Niveau de journalisation
        "check_interval": 5,           # Intervalle entre vérifications (secondes)
        "max_retries": 3,              # Nombre max de tentatives
        "web_port": 8080,              # Port de l'interface web
        "web_host": "0.0.0.0"          # Hôte de l'interface web (0.0.0.0 = toutes les interfaces)
    }
}
```

## 🖥️ Utilisation de l'interface web

1. **Démarrer l'interface web** :
   ```bash
   python3 simple_webui.py
   ```

2. **Accéder à l'interface** via votre navigateur :
   ```
   http://adresse-ip:8080
   ```

### Fonctionnalités de l'interface web

- **Accueil** : Vue d'ensemble du système
- **État** : Statut du service et des connexions
  - Tester la connexion au serveur
  - Démarrer/arrêter le service de transfert
  - **Purger les photos** du dossier local (nouveau !)
- **Configuration** : Modifier les paramètres
- **Upload manuel** : Transférer des fichiers manuellement

## 📲 Utilisation en ligne de commande

### Transfert manuel

```bash
# Transfert manuel (utilise simple_transfer.py avec fallback curl)
python3 simple_main.py

# Transfert direct avec curl uniquement
python3 curl_transfer.py
```

### Tests et diagnostics

```bash
# Tester la solution intégrée contre le problème des fichiers vides
python3 test_solution_integree.py

# Diagnostiquer les problèmes de connexion FTP
python3 diagnose_ftp.py

# Diagnostiquer les problèmes de connexion FTPS
python3 diagnose_ftps.py
```

## 🛠️ Scripts et outils

- `simple_webui.py` : Interface web
- `simple_main.py` : Application principale
- `simple_transfer.py` : Moteur de transfert avec fallback curl
- `curl_transfer.py` : Transfert direct via curl
- `diagnose_ftp.py` et `diagnose_ftps.py` : Outils de diagnostic
- `purge_photos.sh` : Script de nettoyage du dossier local

## 📝 Logs et surveillance

Les logs sont stockés dans le dossier `logs/` :

- `photo_transfer.log` : Logs du processus de transfert
- `webui.log` : Logs de l'interface web

**Messages importants à surveiller** :
```
"Échec d'upload avec FTP, tentative avec curl..."
"✅ Upload curl réussi:"
```

## 🔧 Résolution de problèmes

### Problèmes courants

1. **Fichiers vides (0 octet) sur le serveur**
   - La solution intégrée devrait résoudre ce problème automatiquement
   - Vérifiez les logs pour confirmer que le fallback curl s'active

2. **Erreurs de connexion**
   - Vérifiez les paramètres dans config.json
   - Confirmez que le serveur est accessible
   - Utilisez les scripts de diagnostic : `diagnose_ftp.py` ou `diagnose_ftps.py`

3. **Interface web inaccessible**
   - Vérifiez que le service est démarré : `ps aux | grep simple_webui.py`
   - Confirmez le port configuré dans config.json
   - Vérifiez les logs dans `logs/webui.log`

## 📌 Remarques importantes

- Le dossier par défaut pour les photos est `/tmp/photos`
- L'interface web utilise le port 8080 par défaut
- Pour une meilleure sécurité, changez le mot de passe dans config.json

## 🤝 Support

Pour tout problème ou question :
- Consultez les logs dans le dossier `logs/`
- Utilisez les outils de diagnostic inclus
- Contactez l'administrateur système

---

*Dernière mise à jour : 24 juin 2025*
