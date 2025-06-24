#!/usr/bin/env python3
"""
Test rapide du transfert avec la nouvelle solution intégrée
"""

import os
import sys
sys.path.append('/home/server01/projet_ftp/Projet_FTP')

from simple_transfer import SimpleTransfer
from config_util import load_config
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_integrated_solution():
    """Test de la solution intégrée avec fallback curl"""
    
    # Charger la config
    config = load_config('config.json')
    if not config:
        print("❌ Impossible de charger la configuration")
        return False
    
    # Créer l'objet de transfert
    transfer = SimpleTransfer(config)
    
    # Se connecter
    print("🔗 Test de connexion...")
    if not transfer.connect():
        print("❌ Connexion échouée")
        return False
    
    # S'assurer que le répertoire distant existe
    remote_dir = config['ftp']['directory']
    if not transfer.ensure_dir(remote_dir):
        print(f"❌ Impossible d'accéder au répertoire {remote_dir}")
        transfer.disconnect()
        return False
    
    # Tester l'upload du fichier de test
    test_file = "/tmp/photos/test_transfer.txt"
    if not os.path.exists(test_file):
        print(f"❌ Fichier de test inexistant: {test_file}")
        transfer.disconnect()
        return False
    
    print(f"📤 Test d'upload: {os.path.basename(test_file)}")
    
    # Uploader (ceci devrait utiliser curl en fallback)
    remote_path = f"{remote_dir}/test_transfer.txt"
    success = transfer.upload_file(test_file, "test_transfer.txt")
    
    transfer.disconnect()
    
    if success:
        print("✅ Test d'upload réussi!")
        print("🎉 La solution intégrée avec fallback curl fonctionne!")
        return True
    else:
        print("❌ Test d'upload échoué")
        return False

if __name__ == "__main__":
    print("🧪 Test de la solution intégrée (FTPS + fallback curl)")
    print("="*60)
    
    success = test_integrated_solution()
    
    print("="*60)
    if success:
        print("✅ SUCCÈS: Solution intégrée fonctionnelle!")
    else:
        print("❌ ÉCHEC: Problème dans la solution intégrée")
        sys.exit(1)
