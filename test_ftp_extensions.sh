#!/bin/bash
#
# Script de test pour vérifier le transfert FTP avec extensions
#

# Créer un répertoire de test
TEST_DIR="/tmp/ftp_test"
mkdir -p "$TEST_DIR"

# Créer différents types de fichiers test
echo "Test file 1" > "$TEST_DIR/file1.JPG"
echo "Test file 2" > "$TEST_DIR/file2.jpg"
echo "Test file 3" > "$TEST_DIR/file3"

echo "=== Test du transfert FTP avec préservation des extensions ==="
echo ""
echo "Fichiers de test créés:"
echo " - $TEST_DIR/file1.JPG (extension majuscule)"
echo " - $TEST_DIR/file2.jpg (extension minuscule)"
echo " - $TEST_DIR/file3 (sans extension)"
echo ""

# Sauvegarder le script original
cp /home/server01/projet_ftp/Projet_FTP/lftp_send_jpg.sh /home/server01/projet_ftp/Projet_FTP/lftp_send_jpg.sh.bak
echo "Script original sauvegardé: lftp_send_jpg.sh.bak"

echo ""
echo "=== Test avec l'ancien script ==="
echo "Transfert de file3 (sans extension) avec l'ancien script:"
/home/server01/projet_ftp/Projet_FTP/lftp_send_jpg.sh "$TEST_DIR/file3"

echo ""
echo "=== Test avec le nouveau script ==="
echo "Transfert de file3 (sans extension) avec le nouveau script:"
/home/server01/projet_ftp/Projet_FTP/lftp_send_jpg_fixed.sh "$TEST_DIR/file3"

echo ""
echo "=== Test avec l'ancien script ==="
echo "Transfert de file2.jpg (extension minuscule) avec l'ancien script:"
/home/server01/projet_ftp/Projet_FTP/lftp_send_jpg.sh "$TEST_DIR/file2.jpg"

echo ""
echo "=== Test avec le nouveau script ==="
echo "Transfert de file2.jpg (extension minuscule) avec le nouveau script:"
/home/server01/projet_ftp/Projet_FTP/lftp_send_jpg_fixed.sh "$TEST_DIR/file2.jpg"

echo ""
echo "Test terminé. Vérifiez votre serveur FTP pour les résultats."
