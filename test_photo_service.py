#!/usr/bin/env python3
"""
Test du service de détection d'appareil photo du projet
"""

import sys
import logging
from simple_main import SimpleFTPService

# Configuration du logging pour voir les détails
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_photo_service():
    """Test le service photo du projet"""
    
    print("=== Test du Service Photo ===\n")
    
    try:
        # Créer le service
        print("1. Création du service photo...")
        service = SimpleFTPService()
        print("✅ Service créé avec succès")
        
        # Tester la détection
        print("\n2. Test de détection d'appareil photo...")
        cameras = service.detect_cameras()
        
        if cameras:
            print(f"✅ {len(cameras)} appareil(s) détecté(s):")
            for i, camera in enumerate(cameras):
                print(f"   {i+1}. {camera}")
        else:
            print("❌ Aucun appareil photo détecté")
        
        # Tester la méthode de vérification
        print("\n3. Test de vérification de photos...")
        has_photos = service.check_for_new_photos()
        print(f"Photos disponibles: {has_photos}")
        
        # Afficher la configuration
        print("\n4. Configuration actuelle:")
        camera_config = service.config.get('camera', {})
        print(f"   - Détection auto: {camera_config.get('auto_detect', False)}")
        print(f"   - Dossier download: {camera_config.get('download_path', 'N/A')}")
        print(f"   - Suppression après upload: {camera_config.get('delete_after_upload', False)}")
        
        # Tester la connexion FTP
        print("\n5. Test de connexion FTP...")
        ftp_connected = service.transfer.connect()
        if ftp_connected:
            print("✅ Connexion FTP réussie")
            service.transfer.disconnect()
        else:
            print("❌ Connexion FTP échouée")
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_photo_service()
