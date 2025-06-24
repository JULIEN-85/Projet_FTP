#!/bin/bash
# Test avec curl pour contourner les problèmes FTPS

echo "🧪 Test de transfert avec curl"
echo

# Vérifier qu'il y a des photos
if [ ! "$(ls /tmp/photos/*.jpg 2>/dev/null)" ]; then
    echo "❌ Aucune photo trouvée dans /tmp/photos"
    exit 1
fi

# Prendre la première photo
PHOTO=$(ls /tmp/photos/*.jpg | head -1)
PHOTO_NAME=$(basename "$PHOTO")
PHOTO_SIZE=$(stat -c%s "$PHOTO")

echo "📤 Test avec: $PHOTO_NAME ($PHOTO_SIZE octets)"

# Test avec différentes méthodes curl
echo "🔧 Tentative 1: FTP simple"
curl -T "$PHOTO" ftp://julien:2004@192.168.1.22/photos/test_curl_ftp_"$PHOTO_NAME"

if [ $? -eq 0 ]; then
    echo "✅ FTP simple réussi!"
else
    echo "⚠️ FTP simple échoué, tentative FTPS..."
    
    echo "🔧 Tentative 2: FTPS avec curl"
    curl -k --ftp-ssl-reqd -T "$PHOTO" ftp://julien:2004@192.168.1.22/photos/test_curl_ftps_"$PHOTO_NAME"
    
    if [ $? -eq 0 ]; then
        echo "✅ FTPS avec curl réussi!"
    else
        echo "❌ Toutes les tentatives curl ont échoué"
        exit 1
    fi
fi

echo "🎉 Vérifiez sur le serveur la taille des fichiers transférés"
