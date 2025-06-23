#!/bin/bash
#
# Script amélioré de transfert FTP pour les fichiers JPG uniquement
# Version corrigée qui préserve les extensions des fichiers
# Utilise lftp pour contourner les problèmes TLS

# Configuration depuis config.json ou valeurs par défaut
FTP_HOST="192.168.1.22"
FTP_USER="julien"
FTP_PASS="2004"
FTP_DIR="/photos"
LOCAL_DIR="/tmp/photos"

# Lire la configuration depuis config.json si disponible
CONFIG_FILE="/home/server01/projet_ftp/Projet_FTP/config.json"
if [ -f "$CONFIG_FILE" ]; then
    DELETE_AFTER=$(python3 -c "import json; config=json.load(open('$CONFIG_FILE')); print(str(config.get('camera', {}).get('delete_after_upload', True)).lower())")
    FTP_HOST=$(python3 -c "import json; config=json.load(open('$CONFIG_FILE')); print(config.get('ftp', {}).get('server', '192.168.1.22'))")
    FTP_USER=$(python3 -c "import json; config=json.load(open('$CONFIG_FILE')); print(config.get('ftp', {}).get('username', 'julien'))")
    FTP_PASS=$(python3 -c "import json; config=json.load(open('$CONFIG_FILE')); print(config.get('ftp', {}).get('password', '2004'))")
    FTP_DIR=$(python3 -c "import json; config=json.load(open('$CONFIG_FILE')); print(config.get('ftp', {}).get('directory', '/photos'))")
    LOCAL_DIR=$(python3 -c "import json; config=json.load(open('$CONFIG_FILE')); print(config.get('camera', {}).get('download_path', '/tmp/photos'))")
else
    DELETE_AFTER="true"
fi

# Si un fichier spécifique est fourni en argument, traiter uniquement ce fichier
if [ "$1" != "" ]; then
    if [ -f "$1" ]; then
        FILES=("$1")
        echo "Mode transfert fichier unique: $1"
    else
        echo "ERREUR: Le fichier spécifié '$1' n'existe pas"
        exit 1
    fi
else
    # Sinon, rechercher tous les fichiers JPG et sans extension dans le répertoire local
    echo "=== Transfert des photos JPG et fichiers sans extension via lftp ==="
    echo "Source: $LOCAL_DIR"
    echo "Destination: $FTP_HOST:$FTP_DIR"

    # Vérifier si le répertoire local existe
    if [ ! -d "$LOCAL_DIR" ]; then
        echo "ERREUR: Le répertoire local $LOCAL_DIR n'existe pas"
        exit 1
    fi

    # Rechercher les fichiers JPG et les fichiers sans extension
    mapfile -t FILES < <(find "$LOCAL_DIR" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o ! -name "*.*" \))
    
    FILES_COUNT=${#FILES[@]}
    if [ "$FILES_COUNT" -eq 0 ]; then
        echo "Aucun fichier JPG ou sans extension à transférer dans $LOCAL_DIR"
        exit 0
    fi

    echo "Trouvé $FILES_COUNT fichiers JPG/sans extension à transférer"
fi

# Traiter chaque fichier JPG
for FILE in "${FILES[@]}"; do
    FILENAME=$(basename "$FILE")
    
    # Si le fichier n'a pas d'extension, ajouter .JPG
    if [[ "$FILENAME" != *.* ]]; then
        FTP_FILENAME="${FILENAME}.JPG"
        echo "Fichier sans extension détecté - ajout de .JPG pour le transfert: $FILENAME -> $FTP_FILENAME"
    else
        FTP_FILENAME="$FILENAME"
    fi
    
    echo "Transfert de $FILENAME vers $FTP_FILENAME..."
    
    # Créer un fichier temporaire de commandes lftp
    LFTP_CMDS=$(mktemp)
    cat > "$LFTP_CMDS" << EOF
# Désactiver les vérifications SSL pour contourner les problèmes TLS
set ssl:verify-certificate no
set ssl:check-hostname no

# Debug
debug 3

# Se connecter au serveur
open -u "$FTP_USER","$FTP_PASS" "ftp://$FTP_HOST"

# Créer le répertoire distant s'il n'existe pas
mkdir -p "$FTP_DIR"

# Aller dans le répertoire distant
cd "$FTP_DIR"

# Transfert du fichier (avec préservation/ajout de l'extension)
put "$FILE" -o "$FTP_FILENAME"

# Quitter
bye
EOF

    # Exécuter lftp avec notre script de commandes
    lftp -f "$LFTP_CMDS"
    RESULT=$?

    # Supprimer le fichier temporaire
    rm -f "$LFTP_CMDS"

    # Vérifier le résultat
    if [ $RESULT -eq 0 ]; then
        echo "✅ Fichier $FILENAME transféré avec succès sous le nom $FTP_FILENAME"
        
        # Supprimer le fichier local si demandé
        if [ "$DELETE_AFTER" = true ]; then
            rm -f "$FILE"
            echo "  Fichier local supprimé: $FILENAME"
        fi
    else
        echo "❌ Échec du transfert de $FILENAME"
    fi
done

exit 0
