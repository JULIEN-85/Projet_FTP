#!/bin/bash
#
# Script de test pour télécharger manuellement une photo du D800
#

echo "=== Test de téléchargement manuel D800 ==="

# Arrêter tous les services qui pourraient interférer
echo "1. Arrêt des services en conflit..."
pkill -f d800_auto_download.py 2>/dev/null
pkill -f gvfs-gphoto2-volume-monitor 2>/dev/null
pkill -f gvfs-udisks2-volume-monitor 2>/dev/null
pkill -f gvfs-mtp-volume-monitor 2>/dev/null

sleep 3

# Test de détection
echo "2. Test de détection..."
gphoto2 --auto-detect
if [ $? -ne 0 ]; then
    echo "❌ Échec de la détection"
    exit 1
fi

# Lister les fichiers
echo "3. Liste des fichiers sur l'appareil..."
gphoto2 --list-files
if [ $? -ne 0 ]; then
    echo "❌ Impossible de lister les fichiers"
    exit 1
fi

# Créer un dossier de test
TEST_DIR="/tmp/test_d800_$(date +%H%M%S)"
mkdir -p "$TEST_DIR"

echo "4. Téléchargement dans $TEST_DIR..."
gphoto2 --get-all-files --filename "$TEST_DIR/%C"

if [ $? -eq 0 ]; then
    echo "✅ Téléchargement réussi"
    echo "Fichiers téléchargés:"
    ls -la "$TEST_DIR/"
    
    # Compter les fichiers
    COUNT=$(find "$TEST_DIR" -type f | wc -l)
    echo "Nombre de fichiers: $COUNT"
    
    # Nettoyer
    echo "Nettoyage du dossier de test..."
    rm -rf "$TEST_DIR"
else
    echo "❌ Échec du téléchargement"
    rm -rf "$TEST_DIR"
    exit 1
fi

echo "=== Test terminé avec succès ==="
