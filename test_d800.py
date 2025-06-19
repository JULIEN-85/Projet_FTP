#!/usr/bin/env python3
"""
Script de test pour la détection automatique du Nikon D800
"""

import subprocess
import os
import time

def test_gphoto2_detection():
    """Test la détection du D800 avec gphoto2"""
    print("=== Test de détection du Nikon D800 ===\n")
    
    print("1. Recherche des caméras connectées...")
    try:
        result = subprocess.run(['gphoto2', '--auto-detect'], 
                              capture_output=True, text=True, timeout=10)
        print("Sortie gphoto2:")
        print(result.stdout)
        
        if "D800" in result.stdout or "Nikon" in result.stdout:
            print("✅ Nikon D800 détecté!")
            return True
        elif "Model" in result.stdout and len(result.stdout.strip().split('\n')) > 2:
            print("✅ Caméra détectée (pas forcément D800)")
            return True
        else:
            print("❌ Aucune caméra détectée")
            print("Vérifiez que:")
            print("- Le D800 est allumé")
            print("- Le câble USB est connecté")
            print("- La caméra est en mode PTP/MTP")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_camera_capabilities():
    """Test les capacités de la caméra"""
    print("\n2. Test des capacités de la caméra...")
    try:
        result = subprocess.run(['gphoto2', '--abilities'], 
                              capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            print("✅ Capacités de la caméra:")
            # Afficher seulement les lignes importantes
            lines = result.stdout.split('\n')
            for line in lines:
                if any(keyword in line.lower() for keyword in ['model', 'driver', 'capture', 'config']):
                    print(f"  {line}")
        else:
            print("❌ Impossible d'obtenir les capacités")
    except Exception as e:
        print(f"❌ Erreur: {e}")

def test_file_listing():
    """Test du listage des fichiers sur la caméra"""
    print("\n3. Test du listage des fichiers...")
    try:
        result = subprocess.run(['gphoto2', '--list-files'], 
                              capture_output=True, text=True, timeout=20)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            image_files = [line for line in lines if any(ext in line.lower() 
                          for ext in ['.jpg', '.jpeg', '.nef', '.raw'])]
            
            if image_files:
                print(f"✅ {len(image_files)} fichier(s) image trouvé(s):")
                for i, file_line in enumerate(image_files[:5]):  # Afficher max 5
                    print(f"  {file_line.strip()}")
                if len(image_files) > 5:
                    print(f"  ... et {len(image_files) - 5} autres")
            else:
                print("ℹ️ Aucun fichier image sur la caméra")
        else:
            print("❌ Impossible de lister les fichiers")
            print(f"Erreur: {result.stderr}")
    except Exception as e:
        print(f"❌ Erreur: {e}")

def test_download():
    """Test de téléchargement"""
    print("\n4. Test de téléchargement (simulation)...")
    
    # Créer un dossier de test
    test_dir = "/tmp/test_d800"
    os.makedirs(test_dir, exist_ok=True)
    
    try:
        # Compter les fichiers avant
        files_before = set(os.listdir(test_dir))
        
        print(f"Dossier de test: {test_dir}")
        print("Tentative de téléchargement des nouvelles photos...")
        
        result = subprocess.run([
            'gphoto2', 
            '--get-all-files',
            '--skip-existing',
            '--filename', os.path.join(test_dir, '%f')
        ], capture_output=True, text=True, timeout=60)
        
        # Compter les fichiers après
        files_after = set(os.listdir(test_dir))
        new_files = files_after - files_before
        
        if new_files:
            print(f"✅ {len(new_files)} fichier(s) téléchargé(s):")
            for file in new_files:
                print(f"  {file}")
        else:
            print("ℹ️ Aucun nouveau fichier téléchargé (peut-être déjà présents)")
            
        if result.stderr:
            print(f"Messages: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement: {e}")

if __name__ == "__main__":
    print("🔍 Test de compatibilité Nikon D800 avec gphoto2\n")
    
    if test_gphoto2_detection():
        test_camera_capabilities()
        test_file_listing()
        test_download()
    
    print("\n" + "="*50)
    print("📋 RÉSUMÉ:")
    print("Si votre D800 est détecté, le système peut:")
    print("✅ Détecter automatiquement les nouvelles photos")
    print("✅ Les télécharger vers /tmp/photos")
    print("✅ Les envoyer automatiquement vers votre serveur FTP")
    print("✅ Supprimer les photos après envoi (si configuré)")
    print("\nConnectez votre D800 et relancez ce test !")
