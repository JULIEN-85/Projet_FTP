#!/usr/bin/env python3
"""
Script de test pour la détection d'appareil photo
"""

import subprocess
import time
import json
from config_util import load_config

def test_camera_detection():
    """Test la détection d'appareil photo avec différentes méthodes"""
    
    print("=== Test de Détection d'Appareil Photo ===\n")
    
    # 1. Test gphoto2 direct
    print("1. Test gphoto2 --auto-detect:")
    try:
        result = subprocess.run(['gphoto2', '--auto-detect'], 
                              capture_output=True, text=True, timeout=30)
        print(f"Résultat: {result.returncode}")
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            camera_lines = [line for line in lines if line and not line.startswith('-') and 'Model' not in line]
            if camera_lines:
                print(f"✅ Appareil(s) détecté(s):")
                for line in camera_lines:
                    print(f"   {line}")
            else:
                print("❌ Aucun appareil détecté")
        else:
            print("❌ Aucune sortie")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print()
    
    # 2. Test USB
    print("2. Test périphériques USB:")
    try:
        result = subprocess.run(['lsusb'], capture_output=True, text=True)
        usb_devices = result.stdout.strip().split('\n')
        camera_devices = [dev for dev in usb_devices if any(brand in dev.lower() for brand in ['nikon', 'canon', 'sony', 'camera'])]
        
        if camera_devices:
            print("✅ Périphériques caméra USB trouvés:")
            for dev in camera_devices:
                print(f"   {dev}")
        else:
            print("❌ Aucun périphérique caméra USB trouvé")
            print("Périphériques USB détectés:")
            for dev in usb_devices:
                print(f"   {dev}")
    except Exception as e:
        print(f"❌ Erreur USB: {e}")
    
    print()
    
    # 3. Test avec notre configuration
    print("3. Test avec configuration du projet:")
    try:
        config = load_config()
        camera_config = config.get('camera', {})
        print(f"Configuration caméra: {json.dumps(camera_config, indent=2)}")
        
        if camera_config.get('auto_detect', False):
            print("✅ Détection automatique activée")
        else:
            print("❌ Détection automatique désactivée")
            
    except Exception as e:
        print(f"❌ Erreur config: {e}")
    
    print()
    
    # 4. Test dossier download
    print("4. Test dossier de téléchargement:")
    try:
        config = load_config()
        download_path = config.get('camera', {}).get('download_path', '/tmp/photos')
        import os
        
        if os.path.exists(download_path):
            files = os.listdir(download_path)
            print(f"✅ Dossier existe: {download_path}")
            print(f"   Fichiers présents: {len(files)}")
            if files:
                for f in files[:5]:  # Montrer les 5 premiers
                    print(f"   - {f}")
                if len(files) > 5:
                    print(f"   ... et {len(files) - 5} autres")
        else:
            print(f"❌ Dossier n'existe pas: {download_path}")
            
    except Exception as e:
        print(f"❌ Erreur dossier: {e}")
    
    print("\n=== Instructions ===")
    print("Pour tester avec un vrai appareil photo:")
    print("1. Connectez votre Nikon D800 en USB")
    print("2. Allumez l'appareil")
    print("3. Mettez-le en mode 'PC' ou 'USB' dans les réglages")
    print("4. Relancez ce script")
    print("5. Ou utilisez: gphoto2 --auto-detect")

if __name__ == '__main__':
    test_camera_detection()
