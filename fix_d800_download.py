#!/usr/bin/env python3
"""
Script de correction pour le téléchargement depuis Nikon D800
- Assure le téléchargement complet des fichiers
- Renomme avec les extensions correctes
- Vérifie l'intégrité des fichiers
"""

import os
import subprocess
import logging
import time
import shutil
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='/tmp/nikon_d800_fix.log',
    filemode='w'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)
logger = logging.getLogger('D800Fix')

def kill_interfering_processes():
    """Tue les processus qui peuvent interférer avec gphoto2"""
    processes = ['gphoto2', 'gvfs-gphoto2-volume-monitor', 'gvfs-mtp-volume-monitor']
    
    logger.info("Arrêt des processus qui pourraient interférer...")
    for proc in processes:
        try:
            subprocess.run(['pkill', '-f', proc], capture_output=True)
        except Exception as e:
            logger.debug(f"Erreur lors de l'arrêt de {proc}: {e}")

def prepare_directory():
    """Prépare le répertoire de destination"""
    download_dir = "/tmp/photos"
    if os.path.exists(download_dir):
        # Sauvegarde des anciennes photos
        backup_dir = f"/tmp/photos_backup_{int(time.time())}"
        if os.listdir(download_dir):
            logger.info(f"Sauvegarde des anciennes photos dans {backup_dir}")
            os.makedirs(backup_dir, exist_ok=True)
            for item in os.listdir(download_dir):
                src = os.path.join(download_dir, item)
                dst = os.path.join(backup_dir, item)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
    else:
        os.makedirs(download_dir, exist_ok=True)
        
    logger.info(f"Répertoire de téléchargement: {download_dir}")
    return download_dir

def check_camera():
    """Vérifie si la caméra est connectée et fonctionnelle"""
    logger.info("Vérification de la caméra...")
    try:
        result = subprocess.run(
            ['gphoto2', '--auto-detect'],
            capture_output=True, 
            text=True
        )
        
        if "Nikon" in result.stdout and "usb:" in result.stdout:
            camera_model = [line for line in result.stdout.splitlines() 
                           if "Nikon" in line and "usb:" in line][0].split()[0:2]
            logger.info(f"Caméra détectée: {' '.join(camera_model)}")
            return True
        else:
            logger.error("Aucune caméra Nikon détectée")
            print(result.stdout)
            return False
    except Exception as e:
        logger.error(f"Erreur lors de la détection de la caméra: {e}")
        return False

def download_photos(download_dir, with_thumbnails=False):
    """Télécharge les photos depuis la caméra"""
    logger.info("Téléchargement des photos...")
    
    files_before = set(os.listdir(download_dir))
    
    # Utilise --filename avec %f pour préserver l'extension
    cmd = [
        'gphoto2',
        '--get-all-files',
        '--skip-existing',
        '--filename', os.path.join(download_dir, '%f')
    ]
    
    if with_thumbnails:
        cmd.append('--capture-preview')
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            logger.error(f"Erreur lors du téléchargement: {result.stderr}")
            return []
            
        files_after = set(os.listdir(download_dir))
        new_files = files_after - files_before
        
        logger.info(f"{len(new_files)} nouvelles photos téléchargées")
        return [os.path.join(download_dir, f) for f in new_files]
        
    except subprocess.TimeoutExpired:
        logger.error("Timeout lors du téléchargement")
        return []
    except Exception as e:
        logger.error(f"Erreur: {e}")
        return []

def verify_and_fix_files(file_list):
    """Vérifie et corrige les problèmes de fichiers"""
    logger.info("Vérification de l'intégrité des fichiers...")
    
    valid_files = []
    for file_path in file_list:
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        
        if file_size == 0:
            logger.error(f"Fichier vide: {filename}")
            continue
            
        # Vérifier si le fichier a une extension
        name, ext = os.path.splitext(filename)
        if not ext:
            # Détecter le type de fichier et ajouter l'extension
            try:
                with open(file_path, 'rb') as f:
                    header = f.read(10)
                    if header.startswith(b'\xff\xd8\xff'):
                        new_path = file_path + '.jpg'
                        os.rename(file_path, new_path)
                        file_path = new_path
                        logger.info(f"Fichier renommé: {filename} -> {filename}.jpg")
            except Exception as e:
                logger.error(f"Erreur lors de la vérification du fichier {filename}: {e}")
                
        # Vérifier si c'est un fichier image
        try:
            result = subprocess.run(
                ['file', file_path], 
                capture_output=True, 
                text=True
            )
            
            if "JPEG image" in result.stdout:
                logger.info(f"Image valide: {os.path.basename(file_path)} ({file_size} octets)")
                valid_files.append(file_path)
            else:
                logger.warning(f"Fichier non reconnu comme JPEG: {os.path.basename(file_path)}")
        except Exception as e:
            logger.error(f"Erreur lors de la vérification: {e}")
    
    return valid_files

def main():
    logger.info("=== Démarrage du script de correction pour Nikon D800 ===")
    
    # Arrêter les processus qui pourraient interférer
    kill_interfering_processes()
    
    # Préparer le répertoire de destination
    download_dir = prepare_directory()
    
    # Vérifier si la caméra est connectée
    if not check_camera():
        logger.error("Impossible de continuer sans caméra")
        return
    
    # Télécharger les photos
    new_files = download_photos(download_dir)
    
    if not new_files:
        logger.warning("Aucune nouvelle photo téléchargée")
        return
    
    # Vérifier et corriger les fichiers
    valid_files = verify_and_fix_files(new_files)
    
    logger.info(f"Terminé: {len(valid_files)}/{len(new_files)} fichiers valides")
    
    # Afficher le résultat
    for file in valid_files:
        size = os.path.getsize(file)
        size_str = f"{size / (1024*1024):.2f} MB" if size > 1024*1024 else f"{size / 1024:.2f} KB"
        print(f"✓ {os.path.basename(file)} - {size_str}")

if __name__ == "__main__":
    main()
