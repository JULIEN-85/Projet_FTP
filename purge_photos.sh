#!/bin/bash
# Script pour purger (supprimer) toutes les photos dans /tmp/photos

# Couleurs pour une meilleure lisibilité
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour purger les photos
purge_photos() {
    local dir="$1"
    
    if [ ! -d "$dir" ]; then
        echo -e "${RED}Le répertoire $dir n'existe pas!${NC}"
        exit 1
    fi
    
    # Compter les fichiers avant
    local count_before=$(find "$dir" -type f | wc -l)
    
    echo -e "${YELLOW}Suppression de tous les fichiers dans $dir...${NC}"
    
    # Supprimer tous les fichiers (pas les sous-répertoires)
    find "$dir" -type f -delete
    
    # Compter les fichiers après
    local count_after=$(find "$dir" -type f | wc -l)
    local deleted=$((count_before - count_after))
    
    echo -e "${GREEN}$deleted fichiers supprimés avec succès.${NC}"
    
    # Vérifier les permissions du répertoire
    if [ ! -w "$dir" ]; then
        echo -e "${YELLOW}Attention: le répertoire $dir n'est pas accessible en écriture.${NC}"
        echo "Correction des permissions..."
        chmod 755 "$dir"
        echo -e "${GREEN}Permissions corrigées.${NC}"
    fi
}

# Afficher l'en-tête
echo -e "${BLUE}=== Purge des Photos ===${NC}"
echo

# Chercher le chemin dans la configuration
PHOTO_PATH=$(grep -o '"download_path"[[:space:]]*:[[:space:]]*"[^"]*"' config.json 2>/dev/null | sed 's/"download_path"[[:space:]]*:[[:space:]]*"\([^"]*\)"/\1/')

# Si non trouvé, utiliser la valeur par défaut
if [ -z "$PHOTO_PATH" ]; then
    PHOTO_PATH="/tmp/photos"
    echo -e "${YELLOW}Aucun chemin trouvé dans config.json, utilisation de $PHOTO_PATH${NC}"
else
    echo -e "${YELLOW}Chemin trouvé dans config.json: $PHOTO_PATH${NC}"
fi

# Option pour spécifier un répertoire différent
if [ "$1" == "-d" ] || [ "$1" == "--dir" ]; then
    if [ -n "$2" ]; then
        PHOTO_PATH="$2"
        echo -e "${YELLOW}Utilisation du répertoire spécifié: $PHOTO_PATH${NC}"
    else
        echo -e "${RED}Erreur: argument manquant pour -d/--dir${NC}"
        echo "Usage: $0 [-d|--dir RÉPERTOIRE]"
        exit 1
    fi
fi

# Vérifier si l'option force est utilisée
if [ "$1" == "-f" ] || [ "$1" == "--force" ]; then
    echo -e "${YELLOW}Suppression forcée sans confirmation${NC}"
else
    # Demander confirmation
    read -p "Êtes-vous sûr de vouloir supprimer toutes les photos dans $PHOTO_PATH? (o/N) " confirm
    if [[ "$confirm" != [oO]* ]]; then
        echo -e "${YELLOW}Opération annulée.${NC}"
        exit 0
    fi
fi

# Purger les photos
purge_photos "$PHOTO_PATH"

echo
echo -e "${BLUE}=== Opération terminée ===${NC}"
