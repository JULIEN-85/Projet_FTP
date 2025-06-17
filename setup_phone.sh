#!/bin/bash
# Script de détection et configuration pour téléphones
# Alternative aux appareils photo classiques

echo "📱 CONFIGURATION TÉLÉPHONE POUR GPHOTO2"
echo "========================================"
echo ""

# Fonction de vérification des permissions
check_permissions() {
    echo "🔧 Vérification des permissions..."
    
    # Vérifier que l'utilisateur est dans le groupe plugdev
    if groups $USER | grep -q plugdev; then
        echo "✅ Utilisateur dans le groupe plugdev"
    else
        echo "⚠️  Ajout au groupe plugdev nécessaire"
        sudo usermod -a -G plugdev $USER
        echo "✅ Utilisateur ajouté au groupe plugdev"
        echo "🔄 Redémarrage de session recommandé"
    fi
}

# Fonction de détection USB
detect_usb_devices() {
    echo ""
    echo "🔍 Détection des périphériques USB..."
    
    echo "📋 Tous les périphériques USB :"
    lsusb
    
    echo ""
    echo "📱 Téléphones potentiels détectés :"
    lsusb | grep -E "(Samsung|Google|Huawei|OnePlus|Xiaomi|LG|Sony|Motorola)" || echo "   Aucun téléphone reconnu"
    
    echo ""
    echo "📊 Détails des périphériques Android :"
    lsusb | grep -E "(Samsung|Google)" | while read line; do
        vendor_id=$(echo $line | sed 's/.*ID \([0-9a-f]*\):.*/\1/')
        echo "   Vendor ID: $vendor_id"
    done
}

# Fonction de test gPhoto2
test_gphoto2() {
    echo ""
    echo "📸 Test gPhoto2..."
    
    if ! command -v gphoto2 &> /dev/null; then
        echo "❌ gPhoto2 non installé"
        echo "🔧 Installation en cours..."
        sudo apt update
        sudo apt install -y gphoto2 libgphoto2-dev
    else
        echo "✅ gPhoto2 installé"
    fi
    
    echo ""
    echo "🔍 Détection automatique gPhoto2 :"
    gphoto2 --auto-detect
    
    echo ""
    echo "📋 Résumé de détection :"
    if gphoto2 --auto-detect | grep -q "usb:"; then
        echo "✅ Appareil détecté en mode PTP"
        
        # Informations détaillées sur l'appareil
        echo ""
        echo "📱 Informations de l'appareil :"
        gphoto2 --summary 2>/dev/null || echo "   Informations détaillées non disponibles"
        
        # Test de liste des fichiers
        echo ""
        echo "📁 Test d'accès aux fichiers :"
        gphoto2 --list-folders 2>/dev/null | head -10 || echo "   Impossible de lister les dossiers"
        
    else
        echo "❌ Aucun appareil détecté"
        echo ""
        echo "💡 Vérifications à faire sur le téléphone :"
        echo "   1. Connecter via câble USB (pas Bluetooth/WiFi)"
        echo "   2. Déverrouiller le téléphone"
        echo "   3. Choisir 'Transfert de fichiers' ou 'PTP' dans la notification USB"
        echo "   4. Activer les Options développeur :"
        echo "      - Paramètres → À propos → Taper 7x sur 'Numéro de build'"
        echo "      - Options développeur → Débogage USB (ON)"
        echo "   5. Autoriser le débogage USB depuis ce PC"
    fi
}

# Fonction de test MTP (alternative)
test_mtp() {
    echo ""
    echo "📂 Test MTP (alternative)..."
    
    if ! command -v mtp-detect &> /dev/null; then
        echo "🔧 Installation des outils MTP..."
        sudo apt install -y mtp-tools
    fi
    
    echo "🔍 Détection MTP :"
    mtp-detect 2>/dev/null || echo "   Aucun périphérique MTP détecté"
    
    echo ""
    echo "📁 Liste des fichiers MTP :"
    mtp-files 2>/dev/null | head -10 || echo "   Impossible de lister les fichiers MTP"
}

# Fonction de création des règles udev
create_udev_rules() {
    echo ""
    echo "⚙️  Configuration des règles udev..."
    
    UDEV_FILE="/etc/udev/rules.d/99-phone-gphoto.rules"
    
    if [ -f "$UDEV_FILE" ]; then
        echo "✅ Règles udev déjà présentes"
    else
        echo "📝 Création des règles udev pour téléphones..."
        
        sudo tee "$UDEV_FILE" > /dev/null << 'EOF'
# Règles udev pour téléphones avec gPhoto2
# Samsung
SUBSYSTEM=="usb", ATTR{idVendor}=="04e8", MODE="0664", GROUP="plugdev", TAG+="uaccess"
# Google Pixel
SUBSYSTEM=="usb", ATTR{idVendor}=="18d1", MODE="0664", GROUP="plugdev", TAG+="uaccess"
# Huawei
SUBSYSTEM=="usb", ATTR{idVendor}=="12d1", MODE="0664", GROUP="plugdev", TAG+="uaccess"
# OnePlus
SUBSYSTEM=="usb", ATTR{idVendor}=="2a70", MODE="0664", GROUP="plugdev", TAG+="uaccess"
# Xiaomi
SUBSYSTEM=="usb", ATTR{idVendor}=="2717", MODE="0664", GROUP="plugdev", TAG+="uaccess"
# LG
SUBSYSTEM=="usb", ATTR{idVendor}=="1004", MODE="0664", GROUP="plugdev", TAG+="uaccess"
EOF
        
        echo "✅ Règles udev créées"
        
        # Recharger les règles
        sudo udevadm control --reload
        sudo udevadm trigger
        echo "🔄 Règles udev rechargées"
    fi
}

# Fonction de test de workflow complet
test_phone_workflow() {
    echo ""
    echo "🔄 Test du workflow complet avec téléphone..."
    
    if ! gphoto2 --auto-detect | grep -q "usb:"; then
        echo "❌ Aucun téléphone détecté - impossible de tester le workflow"
        return 1
    fi
    
    echo "✅ Téléphone détecté, test du workflow..."
    
    # Test 1: Lister les fichiers
    echo "📁 Test 1: Liste des fichiers..."
    if gphoto2 --list-files | grep -q -E "\.(jpg|jpeg|png)" 2>/dev/null; then
        echo "✅ Photos trouvées sur le téléphone"
        
        # Compter les photos
        photo_count=$(gphoto2 --list-files 2>/dev/null | grep -c -E "\.(jpg|jpeg|png)" || echo "0")
        echo "📊 Nombre de photos détectées: $photo_count"
        
    else
        echo "⚠️  Aucune photo trouvée ou accès limité"
    fi
    
    # Test 2: Téléchargement test (sans suppression)
    echo ""
    echo "📥 Test 2: Téléchargement test..."
    
    TEST_DIR="phone_test_photos"
    mkdir -p "$TEST_DIR"
    
    if gphoto2 --get-file 1 --filename "$TEST_DIR/test_photo.jpg" 2>/dev/null; then
        echo "✅ Test de téléchargement réussi"
        
        if [ -f "$TEST_DIR/test_photo.jpg" ]; then
            file_size=$(stat -c%s "$TEST_DIR/test_photo.jpg" 2>/dev/null || echo "0")
            echo "📏 Taille du fichier: $file_size bytes"
            
            # Vérification du format
            if file "$TEST_DIR/test_photo.jpg" | grep -q "JPEG"; then
                echo "✅ Format JPEG valide"
            else
                echo "⚠️  Format de fichier inattendu"
            fi
        fi
        
        # Nettoyage
        rm -rf "$TEST_DIR"
        
    else
        echo "❌ Échec du téléchargement test"
        echo "💡 Vérifiez que :"
        echo "   - Le téléphone est déverrouillé"
        echo "   - L'autorisation de débogage USB est accordée"
        echo "   - Des photos sont présentes sur le téléphone"
    fi
}

# Fonction de génération de configuration
generate_phone_config() {
    echo ""
    echo "⚙️  Génération de la configuration pour téléphone..."
    
    cat > config_phone.json << 'EOF'
{
    "ftp": {
        "server": "",
        "port": 21,
        "username": "",
        "password": "",
        "directory": "/uploads",
        "passive_mode": true
    },
    "camera": {
        "auto_detect": true,
        "device_type": "phone",
        "download_path": "phone_photos",
        "delete_after_upload": false,
        "phone_mode": {
            "connection_type": "PTP",
            "wait_for_unlock": true,
            "retry_connection": 5,
            "check_interval": 10
        }
    },
    "system": {
        "log_level": "INFO",
        "check_interval": 10,
        "max_retries": 5,
        "web_port": 8080,
        "web_host": "0.0.0.0"
    }
}
EOF
    
    echo "✅ Configuration téléphone créée: config_phone.json"
    echo ""
    echo "📝 Différences avec configuration appareil photo classique :"
    echo "   - delete_after_upload: false (sécurité)"
    echo "   - check_interval: 10s (plus lent)"
    echo "   - retry_connection: 5 (plus de tentatives)"
    echo "   - device_type: phone (mode spécial)"
}

# Fonction principale
main() {
    echo "🎯 Configuration automatique téléphone + gPhoto2"
    echo ""
    
    # Menu interactif
    echo "Choisissez une action :"
    echo "1. Test complet (recommandé)"
    echo "2. Détection USB seulement"
    echo "3. Test gPhoto2 seulement"
    echo "4. Configuration système"
    echo "5. Génération config téléphone"
    echo "6. Quitter"
    echo ""
    
    read -p "Votre choix (1-6): " choice
    
    case $choice in
        1)
            echo "🚀 Test complet en cours..."
            check_permissions
            detect_usb_devices
            test_gphoto2
            test_mtp
            create_udev_rules
            test_phone_workflow
            generate_phone_config
            ;;
        2)
            detect_usb_devices
            ;;
        3)
            test_gphoto2
            ;;
        4)
            check_permissions
            create_udev_rules
            ;;
        5)
            generate_phone_config
            ;;
        6)
            echo "👋 Au revoir !"
            exit 0
            ;;
        *)
            echo "❌ Choix invalide"
            ;;
    esac
    
    echo ""
    echo "========================================="
    echo "📋 RÉSUMÉ ET PROCHAINES ÉTAPES"
    echo "========================================="
    echo ""
    echo "✅ Si votre téléphone a été détecté :"
    echo "   1. Utilisez config_phone.json comme base"
    echo "   2. Configurez vos paramètres FTP"
    echo "   3. Testez avec: python3 main.py"
    echo "   4. Surveillez l'interface web"
    echo ""
    echo "❌ Si votre téléphone n'est pas détecté :"
    echo "   1. Vérifiez le mode PTP sur le téléphone"
    echo "   2. Activez le débogage USB"
    echo "   3. Essayez un autre câble USB"
    echo "   4. Redémarrez et relancez ce script"
    echo ""
    echo "💡 Pour une meilleure fiabilité, considérez :"
    echo "   - Un appareil photo dédié (Canon, Nikon, Sony)"
    echo "   - Un adaptateur WiFi/SD pour appareils photo"
    echo "   - Une tablette Android en mode PTP"
    echo ""
    echo "📞 Support : Consultez la documentation gPhoto2"
    echo "   http://gphoto.org/doc/remote/"
}

# Point d'entrée
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
