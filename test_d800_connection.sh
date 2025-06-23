#!/bin/bash
#
# Script de test pour vérifier l'accès au Nikon D800 avec gphoto2
#

echo "=== Test de connexion Nikon D800 ==="

# Arrêter les services qui peuvent bloquer l'accès
echo "1. Arrêt des services gvfs..."
pkill -f gvfs-gphoto2-volume-monitor 2>/dev/null
pkill -f gvfs-udisks2-volume-monitor 2>/dev/null
pkill -f gvfs-mtp-volume-monitor 2>/dev/null

sleep 2

# Vérifier la détection de l'appareil photo
echo "2. Détection de l'appareil photo..."
gphoto2 --auto-detect

if [ $? -eq 0 ]; then
    echo "✅ Détection réussie"
else
    echo "❌ Erreur de détection"
    exit 1
fi

# Lister les fichiers sur l'appareil photo
echo "3. Liste des fichiers sur l'appareil photo..."
gphoto2 --list-files

if [ $? -eq 0 ]; then
    echo "✅ Accès aux fichiers réussi"
else
    echo "❌ Impossible d'accéder aux fichiers"
    echo "Vérifiez que:"
    echo "- L'appareil photo est allumé"
    echo "- Le câble USB est bien connecté"
    echo "- L'appareil photo est en mode PTP/MTP"
    exit 1
fi

# Test de téléchargement (simulation)
echo "4. Test de téléchargement (sans télécharger réellement)..."
mkdir -p /tmp/photos
gphoto2 --get-all-files --skip-existing --filename /tmp/photos/%C --simulation

if [ $? -eq 0 ]; then
    echo "✅ Test de téléchargement réussi"
    echo "Le système est prêt pour le téléchargement automatique !"
else
    echo "❌ Problème lors du test de téléchargement"
fi

echo "=== Fin du test ==="
