#!/usr/bin/env python3
from ftplib import FTP
import sys
import os

def test_ftp():
    try:
        print("Tentative de connexion FTP simple...")
        ftp = FTP()
        ftp.connect('192.168.1.22', 21, timeout=10)
        ftp.login('julien', '2004')
        print(f"Connexion réussie, répertoire actuel: {ftp.pwd()}")
        
        try:
            ftp.cwd('/photos')
            print(f"Changement de répertoire vers /photos réussi")
            print("Listage des fichiers:", ftp.nlst())
        except Exception as e:
            print(f"Erreur lors du changement de répertoire: {e}")
        
        # Créer un petit fichier test
        test_file = '/tmp/test_upload.txt'
        with open(test_file, 'w') as f:
            f.write("Contenu de test pour FTP " + os.path.basename(test_file))
        
        print(f"Tentative d'upload du fichier {test_file}...")
        with open(test_file, 'rb') as f:
            upload_result = ftp.storbinary(f'STOR test_upload.txt', f)
            print(f"Résultat de l'upload: {upload_result}")
        
        print("Déconnexion propre...")
        ftp.quit()
        return True
        
    except Exception as e:
        print(f"Erreur lors du test FTP: {e}")
        return False

if __name__ == "__main__":
    success = test_ftp()
    sys.exit(0 if success else 1)
