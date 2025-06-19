#!/bin/bash
# Script de vérification rapide de la détection d'appareil photo

echo "=== Vérification de Détection d'Appareil Photo ==="
echo

echo "1. Détection gphoto2:"
gphoto2 --auto-detect 2>/dev/null | grep -v "^Model" | grep -v "^---" | grep -v "^$" || echo "Aucun appareil détecté"
echo

echo "2. Périphériques USB (caméras):"
lsusb | grep -i -E "(nikon|canon|sony|camera|kodak|fuji)" || echo "Aucune caméra USB détectée"
echo

echo "3. Tous les périphériques USB:"
lsusb
echo

echo "4. Vérification des dossiers photos:"
if [ -d "/tmp/photos" ]; then
    echo "Dossier /tmp/photos existe"
    file_count=$(ls -1 /tmp/photos 2>/dev/null | wc -l)
    echo "Nombre de fichiers: $file_count"
else
    echo "Dossier /tmp/photos n'existe pas"
fi
echo

echo "5. Processus du service photo:"
ps aux | grep -E "(simple_main|photo)" | grep -v grep || echo "Service photo non actif"
echo

echo "=== Instructions ==="
echo "Si aucun appareil n'est détecté:"
echo "1. Vérifiez que l'appareil photo est allumé"
echo "2. Vérifiez le câble USB"
echo "3. Mettez l'appareil en mode PTP/MTP"
echo "4. Sur certains appareils, activez 'PC Connection' dans les menus"
echo "5. Essayez de déconnecter/reconnecter le câble USB"
