#!/usr/bin/env python3
import json
import os
import subprocess
import time

def main():
    # Assurons-nous que lftp est bien installé
    try:
        subprocess.run(['lftp', '--version'], capture_output=True, check=True)
        print("✅ lftp est installé")
    except:
        print("⚠️ lftp n'est pas installé, installation en cours...")
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'lftp'], check=True)
    
    # Charger la configuration
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Créer un fichier de test
    test_file = '/tmp/test_ftps_fix.txt'
    with open(test_file, 'w') as f:
        f.write(f"Test FTPS fix {time.time()}")
    print(f"✅ Fichier test créé: {test_file}")
    
    # Préparer les paramètres FTPS
    server = config['ftp']['server']
    user = config['ftp']['username']
    password = config['ftp']['password']
    remote_dir = config['ftp']['directory']
    
    # Créer le script lftp pour le transfert FTPS sécurisé
    lftp_commands = f'''
    set ftp:ssl-force true
    set ftp:ssl-protect-data true
    set ssl:verify-certificate false
    open -u {user},{password} {server}
    cd {remote_dir}
    put {test_file}
    bye
    '''
    
    print("📤 Tentative de transfert avec lftp (FTPS)...")
    try:
        result = subprocess.run(['lftp'], input=lftp_commands.encode(), capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Transfert FTPS réussi!")
        else:
            print(f"❌ Échec du transfert FTPS: {result.stderr}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Tester aussi avec un petit fichier image
    test_image = '/tmp/test_image.jpg'
    with open(test_image, 'w') as f:
        # Écrire un en-tête JPEG minimal
        f.write('\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00')
        f.write('Test image content')
    
    print(f"✅ Fichier image de test créé: {test_image}")
    
    # Transférer l'image test
    lftp_commands = f'''
    set ftp:ssl-force true
    set ftp:ssl-protect-data true
    set ssl:verify-certificate false
    open -u {user},{password} {server}
    cd {remote_dir}
    put {test_image}
    bye
    '''
    
    print("📤 Tentative de transfert de l'image avec lftp (FTPS)...")
    try:
        result = subprocess.run(['lftp'], input=lftp_commands.encode(), capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Transfert image FTPS réussi!")
        else:
            print(f"❌ Échec du transfert image FTPS: {result.stderr}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
            
if __name__ == "__main__":
    main()
