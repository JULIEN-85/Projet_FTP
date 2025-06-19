# Projet FTP - État Actuel

## Fonctionnalités Implementées ✅

### 1. Interface Web
- ✅ Serveur Flask fonctionnel sur port 8080
- ✅ Page d'upload avec drag & drop
- ✅ Support upload multiple de fichiers
- ✅ Interface moderne et responsive
- ✅ Messages d'erreur et de succès en JSON

### 2. Connexion FTP/FTPS
- ✅ Détection automatique du protocole
- ✅ Support FTPS avec AUTH TLS
- ✅ Connexion et authentification réussies
- ✅ Gestion des erreurs de connexion

### 3. Transfert de Fichiers
- ⚠️ **PROBLÈME ACTUEL**: Timeout lors des uploads FTPS
- ✅ Méthode `ensure_dir` ajoutée
- ✅ Gestion des timeouts et reconnexions
- ✅ Support des formats d'images multiples

### 4. Détection Caméra
- ✅ Integration gphoto2 pour Nikon D800
- ✅ Détection automatique et download
- ✅ Service en arrière-plan

## Problème Principal 🔴

**Upload FTPS timeout**: Les fichiers ne peuvent pas être uploadés via FTPS en raison de timeouts sur le canal de données. Le serveur FTP (192.168.1.22) :
- Exige FTPS (AUTH TLS)
- Accepte les connexions et l'authentification
- Timeout lors des transferts de données (commande STOR)

### Causes Possibles
1. Firewall bloquant les ports de données passifs
2. Configuration réseau/NAT
3. Incompatibilité FTPS
4. Ports de données non configurés sur le serveur

### Solutions Testées
- ✅ Mode passif/actif
- ✅ Timeouts plus longs
- ✅ Buffers plus petits
- ✅ Protection de données (prot_p/prot_c)
- ❌ FTP simple (serveur refuse sans AUTH)

## Solutions Recommandées

### Solution 1: Configuration Réseau
- Vérifier les règles de firewall pour les ports FTP data (ephemeral ports)
- Configurer le serveur FTP pour utiliser une plage de ports définie
- Ouvrir cette plage dans le firewall

### Solution 2: Alternative SFTP
- Installer un serveur SSH/SFTP sur 192.168.1.22
- Modifier la configuration pour utiliser SFTP au lieu de FTPS

### Solution 3: Debug Avancé
- Utiliser Wireshark pour analyser le trafic réseau
- Tester avec un client FTP externe (FileZilla)
- Vérifier les logs du serveur FTP

## Fichiers Principaux

```
/home/server01/projet_ftp/Projet_FTP/
├── simple_main.py         # Service principal avec gphoto2
├── simple_webui.py        # Interface web Flask
├── simple_transfer.py     # Module FTPS (problème upload)
├── config_util.py         # Utilitaires configuration
├── config.json           # Configuration FTP/caméra
├── templates/upload.html  # Interface upload
└── logs/                 # Logs applicatifs
```

## Commandes Utiles

```bash
# Démarrer le serveur web
cd /home/server01/projet_ftp/Projet_FTP
source venv/bin/activate
python3 simple_webui.py

# Tester l'upload
curl -X POST -F "file=@test.jpg" http://localhost:8080/upload

# Voir les logs
tail -f logs/photo_transfer.log
```

Le système est prêt à 90% - seul le problème de timeout FTPS empêche les uploads de fonctionner.
