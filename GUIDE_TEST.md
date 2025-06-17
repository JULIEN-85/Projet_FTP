# 🧪 Guide Complet de Test du Système Photo

## 🖥️ **1. Test Local sur PC Windows**

### Étape 1A: Préparation de l'environnement
```powershell
# Dans PowerShell, naviguez vers le dossier
cd C:\Users\julie\Desktop\projet_FTP

# Vérifiez Python
python --version
# ou
python3 --version

# Installez les dépendances
pip install flask werkzeug
```

### Étape 1B: Test des composants individuels
```powershell
# Test 1: Structure des fichiers
python test_local.py

# Test 2: Interface web (test rapide)
python webui.py
# Puis ouvrez: http://localhost:8080
```

### Étape 1C: Test de l'interface web
1. **Lancez l'interface web** :
   ```powershell
   python webui.py
   ```

2. **Accédez à l'interface** : http://localhost:8080

3. **Testez les pages** :
   - ✅ Page d'accueil s'affiche
   - ✅ Page configuration accessible
   - ✅ Page logs accessible
   - ✅ Saisie des paramètres FTP

4. **Testez la configuration** :
   - Entrez des paramètres FTP de test
   - Cliquez "Sauvegarder"
   - Vérifiez que `config.json` est modifié

---

## 🔧 **2. Test des Outils Système**

### Étape 2A: Test de gPhoto2 (sur Linux/WSL)
```bash
# Installation sur Ubuntu/WSL
sudo apt update
sudo apt install gphoto2

# Test de base
gphoto2 --version
gphoto2 --auto-detect
```

### Étape 2B: Test FTP
```bash
# Test connexion FTP manuel
ftp ftp.example.com
# ou
curl ftp://username:password@ftp.example.com/
```

---

## 🥧 **3. Test sur Raspberry Pi**

### Étape 3A: Préparation du Pi
```bash
# 1. Copier les fichiers sur le Pi
scp -r C:\Users\julie\Desktop\projet_FTP pi@[IP_DU_PI]:/home/pi/

# 2. Se connecter au Pi
ssh pi@[IP_DU_PI]

# 3. Aller dans le dossier
cd /home/pi/projet_FTP
```

### Étape 3B: Installation et test
```bash
# Installation automatique
chmod +x install.sh
./install.sh

# Test automatique complet
python3 test_system.py

# Test avec Makefile
make test
```

### Étape 3C: Tests spécifiques
```bash
# Test appareil photo
make test-camera
gphoto2 --auto-detect

# Test FTP
make test-ftp

# Test interface web
make start
# Puis accéder à: http://[IP_DU_PI]:8080
```

---

## 📱 **4. Test de l'Interface Web**

### Tests à effectuer dans l'interface :

#### Page d'Accueil
- [ ] **Statistiques** s'affichent
- [ ] **État des connexions** visible
- [ ] **Boutons Start/Stop** fonctionnels
- [ ] **Tests connexions** marchent

#### Page Configuration
- [ ] **Paramètres FTP** modifiables
- [ ] **Sauvegarde** fonctionne
- [ ] **Tests connexion** en temps réel
- [ ] **Validation** des champs

#### Page Logs
- [ ] **Logs** s'affichent
- [ ] **Filtrage** fonctionne
- [ ] **Auto-refresh** marche
- [ ] **Scroll automatique** OK

---

## 🔍 **5. Test du Workflow Complet**

### Scénario de test complet :

#### 5A: Préparation
```bash
# 1. Connecter un appareil photo USB
# 2. Vérifier la détection
gphoto2 --auto-detect

# 3. Configurer FTP dans l'interface web
# 4. Démarrer le service
make start
```

#### 5B: Test de capture
```bash
# Prendre une photo sur l'appareil
# Le système devrait automatiquement :
# 1. Détecter la nouvelle photo
# 2. La télécharger
# 3. L'envoyer sur FTP
# 4. Logger l'opération
```

#### 5C: Vérification
```bash
# Vérifier les logs
make logs

# Vérifier sur le serveur FTP
# Vérifier les statistiques dans l'interface web
```

---

## 🚨 **6. Test des Cas d'Erreur**

### Tests de robustesse :

#### 6A: Panne réseau
```bash
# Débrancher le réseau temporairement
# Le système devrait :
# - Logger l'erreur
# - Réessayer automatiquement
# - Reprendre quand le réseau revient
```

#### 6B: Appareil photo déconnecté
```bash
# Débrancher l'appareil photo
# Le système devrait :
# - Détecter la déconnexion
# - Logger un warning
# - Continuer à surveiller
```

#### 6C: Serveur FTP inaccessible
```bash
# Configurer un mauvais serveur FTP
# Le système devrait :
# - Échouer proprement
# - Réessayer selon la configuration
# - Logger les erreurs détaillées
```

---

## 📊 **7. Test de Performance**

### Métriques à vérifier :

#### 7A: Temps de réponse
- **Détection photo** : < 10 secondes
- **Upload FTP** : Selon taille et connexion
- **Interface web** : < 2 secondes

#### 7B: Utilisation ressources
```bash
# Surveiller CPU/RAM
htop

# Surveiller logs
tail -f logs/photo_transfer.log

# Surveiller température (Pi)
vcgencmd measure_temp
```

---

## ✅ **8. Checklist de Validation**

### Fonctionnalités de base :
- [ ] Installation automatique réussie
- [ ] Interface web accessible
- [ ] Configuration FTP sauvegardée
- [ ] Détection appareil photo
- [ ] Test connexion FTP
- [ ] Démarrage/arrêt des services
- [ ] Logs visibles et filtrables

### Fonctionnalités avancées :
- [ ] Démarrage automatique au boot
- [ ] Gestion d'erreurs et retry
- [ ] Monitoring en temps réel
- [ ] Sauvegarde/restauration
- [ ] Optimisations Pi 5

### Tests de charge :
- [ ] Plusieurs photos simultanées
- [ ] Fonctionnement 24h/24
- [ ] Gros fichiers (>50MB)
- [ ] Réseau lent/instable

---

## 🆘 **Commandes de Dépannage**

```bash
# État général
make status
make info

# Logs détaillés
make logs
journalctl -u photo-ftp.service -f

# Tests manuels
make test-camera
make test-ftp

# Redémarrage complet
make restart
sudo reboot

# Monitoring
make monitor-pi5  # Si Pi 5
```

---

## 📞 **Support et Aide**

Si vous rencontrez des problèmes :

1. **Vérifiez les logs** : `make logs`
2. **Testez les composants** : `make test`
3. **Consultez l'état** : `make status`
4. **Redémarrez si nécessaire** : `make restart`

Le système est conçu pour être **auto-diagnostique** et **auto-récupérant** ! 🚀
