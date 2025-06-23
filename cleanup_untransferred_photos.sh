#!/bin/bash
# Script de nettoyage des fichiers non transférés dans /tmp/photos
# Supprime tous les fichiers qui ne sont pas .jpg/.jpeg (donc non transférés)

PHOTO_DIR="/tmp/photos"

cd "$PHOTO_DIR" || exit 1

# Supprimer tous les fichiers qui ne sont pas .jpg ou .jpeg
for f in *; do
    if [ -f "$f" ] && [[ ! "$f" =~ \.(jpg|jpeg|JPG|JPEG)$ ]]; then
        echo "Suppression du fichier non transféré: $f"
        rm -f "$f"
    fi
done

echo "Nettoyage terminé."
