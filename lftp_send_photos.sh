#!/bin/bash
#
# Script de transfert FTP utilisant lftp pour contourner les problèmes TLS
# lftp gère mieux les connexions FTPS problématiques

# Configuration
FTP_HOST="192.168.1.22"
FTP_USER="julien"
FTP_PASS="2004"
FTP_DIR="/photos"
LOCAL_DIR="/tmp/photos"
DELETE_AFTER=true

echo "=== Transfert de photos via lftp ==="
echo "Source: $LOCAL_DIR"
echo "Destination: $FTP_HOST:$FTP_DIR"

# Vérifier si le répertoire local existe
if [ ! -d "$LOCAL_DIR" ]; then
    echo "ERREUR: Le répertoire local $LOCAL_DIR n'existe pas"
    exit 1
fi

# Compter les fichiers à transférer
FILES_COUNT=$(find "$LOCAL_DIR" -type f | wc -l)
if [ "$FILES_COUNT" -eq 0 ]; then
    echo "Aucun fichier à transférer dans $LOCAL_DIR"
    exit 0
fi

echo "Trouvé $FILES_COUNT fichiers à transférer"

# Créer un fichier temporaire de commandes lftp
LFTP_CMDS=$(mktemp)
cat > "$LFTP_CMDS" << EOF
# Désactiver les vérifications SSL pour contourner les problèmes TLS
set ssl:verify-certificate no
set ssl:check-hostname no

# Se connecter au serveur
open -u "$FTP_USER","$FTP_PASS" "ftp://$FTP_HOST"

# Créer le répertoire distant s'il n'existe pas
mkdir -p "$FTP_DIR"

# Aller dans le répertoire distant
cd "$FTP_DIR"

# Afficher les fichiers distants
ls

# Transférer tous les fichiers - mode miroir
mirror -R "$LOCAL_DIR" .

# Quitter
bye
EOF

# Exécuter lftp avec notre script de commandes
echo "Démarrage du transfert..."
lftp -f "$LFTP_CMDS"
RESULT=$?

# Supprimer le fichier temporaire
rm -f "$LFTP_CMDS"

# Vérifier le résultat
if [ $RESULT -eq 0 ]; then
    echo "✅ Transfert terminé avec succès"
    
    # Supprimer les fichiers locaux si demandé
    if [ "$DELETE_AFTER" = true ]; then
        echo "Suppression des fichiers locaux..."
        find "$LOCAL_DIR" -type f -exec rm -f {} \;
        echo "Fichiers locaux supprimés"
    fi
else
    echo "❌ Erreur lors du transfert (code $RESULT)"
fi
