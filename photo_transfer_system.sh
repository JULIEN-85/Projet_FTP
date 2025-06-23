#!/bin/bash
#
# Script principal de gestion du système complet
# Démarre les services de téléchargement D800 et de transfert FTP
#

echo "=== Système de transfert automatique D800 vers FTP ==="

# Vérifier que tous les scripts sont présents
REQUIRED_FILES=(
    "/home/server01/projet_ftp/Projet_FTP/d800_auto_download.py"
    "/home/server01/projet_ftp/Projet_FTP/auto_jpg_transfer.py"
    "/home/server01/projet_ftp/Projet_FTP/lftp_send_jpg.sh"
    "/home/server01/projet_ftp/Projet_FTP/config.json"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Fichier manquant: $file"
        exit 1
    fi
done

echo "✅ Tous les fichiers requis sont présents"

# Créer les répertoires nécessaires
mkdir -p /tmp/photos
mkdir -p /home/server01/projet_ftp/Projet_FTP/logs

# Fonction pour démarrer un script en arrière-plan
start_service() {
    local script_name="$1"
    local script_path="$2"
    local log_suffix="$3"
    
    echo "Démarrage de $script_name..."
    
    # Vérifier si le script n'est pas déjà en cours d'exécution
    if pgrep -f "$script_path" > /dev/null; then
        echo "⚠️  $script_name est déjà en cours d'exécution"
        return 0
    fi
    
    # Démarrer le script
    nohup python3 "$script_path" > "/home/server01/projet_ftp/Projet_FTP/logs/${script_name}_${log_suffix}.log" 2>&1 &
    
    sleep 2
    
    # Vérifier que le script a bien démarré
    if pgrep -f "$script_path" > /dev/null; then
        echo "✅ $script_name démarré avec succès"
        return 0
    else
        echo "❌ Échec du démarrage de $script_name"
        return 1
    fi
}

# Fonction pour arrêter les services
stop_services() {
    echo "Arrêt des services..."
    pkill -f "d800_auto_download.py"
    pkill -f "auto_jpg_transfer.py"
    echo "Services arrêtés"
}

# Fonction pour afficher le statut
show_status() {
    echo "=== Statut des services ==="
    
    if pgrep -f "d800_auto_download.py" > /dev/null; then
        echo "✅ Service téléchargement D800: ACTIF"
    else
        echo "❌ Service téléchargement D800: INACTIF"
    fi
    
    if pgrep -f "auto_jpg_transfer.py" > /dev/null; then
        echo "✅ Service transfert FTP: ACTIF"
    else
        echo "❌ Service transfert FTP: INACTIF"
    fi
    
    echo "Nombre de photos dans /tmp/photos: $(find /tmp/photos -name "*.jpg" -o -name "*.jpeg" | wc -l)"
}

# Traitement des arguments
case "$1" in
    start)
        echo "Démarrage du système complet..."
        start_service "D800Download" "/home/server01/projet_ftp/Projet_FTP/d800_auto_download.py" "$(date +%Y%m%d)"
        start_service "FTPTransfer" "/home/server01/projet_ftp/Projet_FTP/auto_jpg_transfer.py" "$(date +%Y%m%d)"
        show_status
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        sleep 3
        start_service "D800Download" "/home/server01/projet_ftp/Projet_FTP/d800_auto_download.py" "$(date +%Y%m%d)"
        start_service "FTPTransfer" "/home/server01/projet_ftp/Projet_FTP/auto_jpg_transfer.py" "$(date +%Y%m%d)"
        show_status
        ;;
    status)
        show_status
        ;;
    test)
        echo "Test de connexion D800..."
        /home/server01/projet_ftp/Projet_FTP/test_d800_connection.sh
        ;;
    logs)
        echo "=== Logs récents du téléchargement D800 ==="
        tail -n 20 /home/server01/projet_ftp/Projet_FTP/logs/d800_download.log 2>/dev/null || echo "Aucun log disponible"
        echo ""
        echo "=== Logs récents du transfert FTP ==="
        tail -n 20 /home/server01/projet_ftp/Projet_FTP/logs/auto_transfer.log 2>/dev/null || echo "Aucun log disponible"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|test|logs}"
        echo ""
        echo "Commandes disponibles:"
        echo "  start   - Démarrer le système complet"
        echo "  stop    - Arrêter tous les services"
        echo "  restart - Redémarrer tous les services"
        echo "  status  - Afficher le statut des services"
        echo "  test    - Tester la connexion avec le D800"
        echo "  logs    - Afficher les logs récents"
        exit 1
        ;;
esac
