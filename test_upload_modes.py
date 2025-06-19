#!/usr/bin/env python3
"""
Script de configuration et test des modes d'upload
"""

import json
import os
from simple_transfer import SimpleTransfer

def test_upload_modes():
    """Test différents modes d'upload"""
    
    print("=== Test des Modes d'Upload ===\n")
    
    # Créer un fichier de test
    test_file = '/tmp/test_upload_modes.txt'
    with open(test_file, 'w') as f:
        f.write("Test des modes d'upload")
    
    # Charger la config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    print("1. Test FTPS (mode normal):")
    try:
        # Config pour FTPS
        config['ftp']['local_backup_mode'] = False
        transfer = SimpleTransfer(config)
        
        if transfer.connect():
            result = transfer.upload_file(test_file, 'test_ftps.txt')
            print(f"   ✅ FTPS: {'Réussi' if result else 'Échoué'}")
            transfer.disconnect()
        else:
            print("   ❌ FTPS: Connexion échouée")
    except Exception as e:
        print(f"   ❌ FTPS: Erreur - {e}")
    
    print("\n2. Test SFTP (fallback):")
    try:
        # Tester SFTP
        config['ftp']['protocol'] = 'sftp'
        config['ftp']['port'] = 22
        transfer = SimpleTransfer(config)
        
        if transfer.connect():
            result = transfer.upload_file(test_file, 'test_sftp.txt')
            print(f"   ✅ SFTP: {'Réussi' if result else 'Échoué'}")
            transfer.disconnect()
        else:
            print("   ❌ SFTP: Connexion échouée")
    except Exception as e:
        print(f"   ❌ SFTP: Erreur - {e}")
    
    print("\n3. Test Backup Local:")
    try:
        # Config pour backup local
        config['ftp']['local_backup_mode'] = True
        transfer = SimpleTransfer(config)
        
        result = transfer.upload_file_local_backup(test_file, 'test_local.txt')
        print(f"   ✅ Local: {'Réussi' if result else 'Échoué'}")
    except Exception as e:
        print(f"   ❌ Local: Erreur - {e}")
    
    # Nettoyer
    try:
        os.unlink(test_file)
    except:
        pass
    
    print("\n=== Recommandations ===")
    print("Pour utiliser FTPS en production:")
    print("1. Résolvez le problème de firewall/réseau")
    print("2. Modifiez config.json: 'local_backup_mode': false")
    print("3. Testez avec: gphoto2 + upload automatique")
    
    print("\nPour utiliser SFTP (alternative):")
    print("1. Installez SSH sur 192.168.1.22")
    print("2. Modifiez config.json: 'protocol': 'sftp', 'port': 22")
    print("3. Désactivez: 'local_backup_mode': false")

if __name__ == '__main__':
    test_upload_modes()
