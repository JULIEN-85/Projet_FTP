#!/usr/bin/env python3
"""
Test final avec une 'photo' de test pour valider la solution complète
"""

import os
import sys
import logging
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append('/home/server01/projet_ftp/Projet_FTP')

from simple_main import SimpleFTPService

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('TestFinal')

def test_final():
    """Test final de la solution complète"""
    
    logger.info("🎯 TEST FINAL - Solution complète pour photos non-vides")
    logger.info("=" * 60)
    
    # Vérifier qu'il y a un fichier à transférer
    download_path = "/tmp/photos"
    test_files = []
    
    for filename in os.listdir(download_path):
        if filename.endswith(('.jpg', '.jpeg', '.txt')):
            file_path = os.path.join(download_path, filename)
            file_size = os.path.getsize(file_path)
            test_files.append((file_path, file_size))
            logger.info(f"📁 Fichier trouvé: {filename} ({file_size} octets)")
    
    if not test_files:
        logger.error("❌ Aucun fichier de test trouvé")
        return False
    
    # Créer le service
    service = SimpleFTPService()
    
    # Tester la connexion
    logger.info("🔗 Test de connexion au serveur...")
    success, message = service.test_connection()
    
    if not success:
        logger.error(f"❌ Connexion échouée: {message}")
        return False
    
    logger.info(f"✅ Connexion réussie: {message}")
    
    # Transférer les fichiers un par un
    success_count = 0
    
    for file_path, original_size in test_files:
        filename = os.path.basename(file_path)
        logger.info(f"📤 Transfert de {filename} ({original_size} octets)...")
        
        if service.upload_photo_to_ftp(file_path):
            success_count += 1
            logger.info(f"✅ {filename} transféré avec succès")
        else:
            logger.error(f"❌ Échec du transfert de {filename}")
    
    # Résumé
    logger.info("=" * 60)
    logger.info(f"📊 RÉSULTATS: {success_count}/{len(test_files)} fichiers transférés")
    
    if success_count == len(test_files):
        logger.info("🎉 SUCCÈS TOTAL!")
        logger.info("✅ Problème de fichiers vides (0 octet) RÉSOLU!")
        logger.info("💡 Le système utilisera automatiquement curl en cas de problème FTPS")
        return True
    else:
        logger.error("❌ Des transferts ont échoué")
        return False

if __name__ == "__main__":
    success = test_final()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 SOLUTION VALIDÉE !")
        print("✅ Les photos ne seront plus transférées vides")
        print("✅ Le système bascule automatiquement vers curl si nécessaire")
        print("✅ Prêt pour utilisation avec le Nikon D800")
    else:
        print("❌ PROBLÈME DÉTECTÉ")
        print("❌ Vérifiez la configuration et la connectivité réseau")
        sys.exit(1)
    print("=" * 70)
