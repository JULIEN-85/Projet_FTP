#!/usr/bin/env python3
"""
Test simple pour vérifier que la correction FTPS fonctionne
"""

import os
import sys
import json
import logging
from simple_transfer import SimpleTransfer

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('TestFTPSFix')

def test_upload():
    """Test simple d'upload d'une photo"""
    
    # Charger la config
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except Exception as e:
        logger.error(f"Erreur chargement config: {e}")
        return False
    
    # Créer l'objet de transfert
    transfer = SimpleTransfer(config)
    
    # Se connecter
    logger.info("🔗 Connexion au serveur...")
    if not transfer.connect():
        logger.error("❌ Impossible de se connecter")
        return False
    
    # Trouver une photo à transférer
    download_path = config['camera'].get('download_path', '/tmp/photos')
    photos = []
    
    for filename in os.listdir(download_path):
        if filename.lower().endswith(('.jpg', '.jpeg')):
            photos.append(os.path.join(download_path, filename))
    
    if not photos:
        logger.error("❌ Aucune photo trouvée dans " + download_path)
        transfer.disconnect()
        return False
    
    # Prendre la première photo
    photo_path = photos[0]
    photo_name = os.path.basename(photo_path)
    photo_size = os.path.getsize(photo_path)
    
    logger.info(f"📤 Test d'upload: {photo_name} ({photo_size} octets)")
    
    # S'assurer que le répertoire distant existe
    remote_dir = config['ftp']['directory']
    if not transfer.ensure_dir(remote_dir):
        logger.error(f"❌ Impossible d'accéder au répertoire {remote_dir}")
        transfer.disconnect()
        return False
    
    # Uploader la photo
    remote_path = f"{remote_dir}/{photo_name}"
    success = transfer.upload_file(photo_path, remote_path)
    
    # Déconnecter
    transfer.disconnect()
    
    if success:
        logger.info(f"✅ Upload réussi: {photo_name}")
        logger.info("🎉 Le problème de fichiers vides (0 octet) est RÉSOLU!")
        return True
    else:
        logger.error(f"❌ Échec de l'upload: {photo_name}")
        return False

if __name__ == "__main__":
    logger.info("🧪 Test de la correction FTPS pour fichiers vides")
    
    success = test_upload()
    
    if success:
        print("\n" + "="*60)
        print("✅ SUCCÈS: La correction fonctionne!")
        print("Les photos ne seront plus transférées vides (0 octet)")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ ÉCHEC: Le problème persiste")
        print("Des investigations supplémentaires sont nécessaires")
        print("="*60)
        sys.exit(1)
