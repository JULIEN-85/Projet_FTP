#!/bin/bash
# Test simple de transfert avec lftp pour vérifier la correction

echo "🧪 Test de transfert avec lftp corrigé"
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

# Script lftp avec correction pour éviter les fichiers vides
lftp << EOF
set ftp:ssl-force true
set ftp:ssl-protect-data false
set ssl:verify-certificate false
set net:timeout 30
set net:max-retries 2
open -u julien,2004 192.168.1.22
cd /photos
put "$PHOTO" -o "test_${PHOTO_NAME}"
ls -l "test_${PHOTO_NAME}"
quit
EOF

if [ $? -eq 0 ]; then
    echo "✅ Transfert lftp réussi!"
    echo "🎉 Vérifiez sur le serveur que test_${PHOTO_NAME} a la bonne taille ($PHOTO_SIZE octets)"
else
    echo "❌ Échec du transfert lftp"
    exit 1
fi
