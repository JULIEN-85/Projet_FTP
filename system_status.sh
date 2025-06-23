#!/bin/bash
#
# Script de statut complet du système de transfert automatique D800 -> FTP
#

echo "========================================="
echo "    SYSTÈME DE TRANSFERT AUTOMATIQUE"
echo "    Nikon D800 -> FTP"
echo "========================================="
echo ""

# Vérifier les services en cours d'exécution
echo "🔍 STATUT DES SERVICES:"
echo "------------------------"

D800_PID=$(pgrep -f "d800_auto_download.py")
FTP_PID=$(pgrep -f "auto_jpg_transfer.py")

if [ -n "$D800_PID" ]; then
    echo "✅ Service téléchargement D800: ACTIF (PID: $D800_PID)"
else
    echo "❌ Service téléchargement D800: INACTIF"
fi

if [ -n "$FTP_PID" ]; then
    echo "✅ Service transfert FTP: ACTIF (PID: $FTP_PID)"
else
    echo "❌ Service transfert FTP: INACTIF"
fi

echo ""

# Vérifier la connexion du D800
echo "📷 CONNEXION APPAREIL PHOTO:"
echo "-----------------------------"
pkill -f gvfs-gphoto2-volume-monitor 2>/dev/null
sleep 1

D800_DETECTED=$(gphoto2 --auto-detect 2>/dev/null | grep -i "nikon.*d800")
if [ -n "$D800_DETECTED" ]; then
    echo "✅ Nikon D800 détecté et connecté"
    echo "   $D800_DETECTED"
else
    echo "❌ Nikon D800 non détecté"
    echo "   Vérifiez la connexion USB et que l'appareil est allumé"
fi

echo ""

# Statistiques des photos
echo "📊 STATISTIQUES:"
echo "-----------------"
PHOTOS_LOCAL=$(find /tmp/photos -name "*.jpg" -o -name "*.jpeg" 2>/dev/null | wc -l)
echo "Photos dans /tmp/photos: $PHOTOS_LOCAL"

if [ "$PHOTOS_LOCAL" -gt 0 ]; then
    echo "Dernières photos:"
    ls -lt /tmp/photos/*.jpg 2>/dev/null | head -3 | while read line; do
        echo "  $line"
    done
fi

echo ""

# Logs récents
echo "📋 LOGS RÉCENTS:"
echo "-----------------"
echo "Téléchargement D800 (5 dernières lignes):"
if [ -f "/home/server01/projet_ftp/Projet_FTP/logs/d800_download.log" ]; then
    tail -n 5 /home/server01/projet_ftp/Projet_FTP/logs/d800_download.log | sed 's/^/  /'
else
    echo "  Aucun log disponible"
fi

echo ""
echo "Transfert FTP (5 dernières lignes):"
if [ -f "/home/server01/projet_ftp/Projet_FTP/logs/auto_transfer.log" ]; then
    tail -n 5 /home/server01/projet_ftp/Projet_FTP/logs/auto_transfer.log | sed 's/^/  /'
else
    echo "  Aucun log disponible"
fi

echo ""

# Configuration actuelle
echo "⚙️  CONFIGURATION:"
echo "-------------------"
if [ -f "/home/server01/projet_ftp/Projet_FTP/config.json" ]; then
    echo "Serveur FTP: $(python3 -c "import json; config=json.load(open('/home/server01/projet_ftp/Projet_FTP/config.json')); print(config['ftp']['server'])")"
    echo "Utilisateur: $(python3 -c "import json; config=json.load(open('/home/server01/projet_ftp/Projet_FTP/config.json')); print(config['ftp']['username'])")"
    echo "Répertoire distant: $(python3 -c "import json; config=json.load(open('/home/server01/projet_ftp/Projet_FTP/config.json')); print(config['ftp']['directory'])")"
    echo "Suppression après transfert: $(python3 -c "import json; config=json.load(open('/home/server01/projet_ftp/Projet_FTP/config.json')); print(config['camera']['delete_after_upload'])")"
else
    echo "❌ Fichier de configuration non trouvé"
fi

echo ""
echo "========================================="
