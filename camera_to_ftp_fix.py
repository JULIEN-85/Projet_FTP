#!/usr/bin/env python3
"""
Script de réparation pour le transfert photo caméra vers FTP
Contourne les problèmes de corruption/transfert
"""

import os
import sys
import json
import subprocess
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('CameraToFTP')

def load_config():
    """Charge la configuration depuis config.json"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erreur lors du chargement de la configuration: {e}")
        sys.exit(1)

def download_from_camera(download_path):
    """Télécharge les photos depuis la caméra avec gphoto2"""
    logger.info("Recherche de la caméra...")
    
    try:
        # Vérifier si une caméra est connectée
        result = subprocess.run(['gphoto2', '--auto-detect'], 
                           capture_output=True, text=True, timeout=10)
        
        if "Model" not in result.stdout or len(result.stdout.strip().split('\n')) <= 2:
            logger.error("❌ Aucune caméra détectée")
            return []
        
        camera_info = [line for line in result.stdout.split('\n') if 'usb:' in line.lower()]
        if camera_info:
            logger.info(f"✅ Caméra détectée: {camera_info[0].split()[0]}")
        else:
            logger.info("✅ Caméra détectée")
        
        # Créer le dossier de téléchargement si nécessaire
        os.makedirs(download_path, exist_ok=True)
        
        # Compter les fichiers avant téléchargement
        files_before = set(os.listdir(download_path))
        
        # Télécharger toutes les nouvelles photos
        logger.info("📷 Téléchargement des photos...")
        result = subprocess.run([
            'gphoto2', 
            '--get-all-files',
            '--skip-existing', 
            '--filename', os.path.join(download_path, '%f')  # %f préserve l'extension
        ], capture_output=True, text=True, timeout=120)
        
        # Vérifier si des erreurs se sont produites
        if result.returncode != 0:
            logger.warning(f"⚠️ Le téléchargement a retourné un code d'erreur: {result.returncode}")
            logger.warning(f"Erreur: {result.stderr}")
        
        # Compter les nouveaux fichiers
        files_after = set(os.listdir(download_path))
        new_files = files_after - files_before
        
        # Vérifier l'extension des fichiers
        photos = []
        for filename in new_files:
            file_path = os.path.join(download_path, filename)
            # Vérifier par extension
            if any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.nef', '.raw', '.cr2']):
                photos.append(file_path)
            # Détecter et corriger les fichiers sans extension
            elif os.path.isfile(file_path) and os.path.getsize(file_path) > 100:
                try:
                    with open(file_path, 'rb') as img_file:
                        header = img_file.read(10)
                        # En-tête JPEG: FF D8 FF
                        if header[0:3] == b'\xff\xd8\xff':
                            new_path = file_path + '.jpg'
                            os.rename(file_path, new_path)
                            photos.append(new_path)
                            logger.info(f"✅ Fichier JPEG détecté et renommé: {filename} -> {filename}.jpg")
                except Exception as e:
                    logger.warning(f"⚠️ Erreur lors de la vérification du fichier {filename}: {e}")
                    
        if photos:
            logger.info(f"✅ {len(photos)} photos téléchargées avec succès")
            return photos
        else:
            logger.info("ℹ️ Aucune nouvelle photo trouvée")
            return []
        
    except subprocess.TimeoutExpired:
        logger.error("❌ Timeout lors de la communication avec la caméra")
        return []
    except Exception as e:
        logger.error(f"❌ Erreur lors de la détection/téléchargement: {e}")
        return []

def upload_to_ftp(config, photo_paths):
    """Upload les photos vers le serveur FTP en utilisant lftp"""
    if not photo_paths:
        logger.info("Pas de photos à transférer")
        return 0
    
    logger.info(f"📤 Transfert de {len(photo_paths)} photos vers le serveur FTP")
    
    ftp_config = config['ftp']
    
    # Vérifier que lftp est disponible
    try:
        subprocess.run(['lftp', '--version'], capture_output=True, check=True)
    except:
        logger.error("❌ lftp n'est pas installé")
        return 0
    
    successful_transfers = 0
    
    for photo_path in photo_paths:
        filename = os.path.basename(photo_path)
        
        # Créer les commandes lftp
        use_ftps = ftp_config.get('use_ftps', True)
        
        commands = []
        
        if use_ftps:
            commands.extend([
                'set ftp:ssl-force true',
                'set ftp:ssl-protect-data true',
                'set ssl:verify-certificate false'
            ])
        
        commands.extend([
            f'open -u {ftp_config["username"]},{ftp_config["password"]} {ftp_config["server"]}',
            f'cd {ftp_config["directory"]}',
            f'put "{photo_path}" -o "{filename}"',
            'quit'
        ])
        
        lftp_script = '\n'.join(commands)
        
        try:
            logger.info(f"Transfert de {filename}...")
            result = subprocess.run(['lftp'], input=lftp_script.encode(), 
                                 capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logger.info(f"✅ Transfert réussi: {filename}")
                successful_transfers += 1
                
                # Optionnellement: supprimer après upload
                if config['camera'].get('delete_after_upload', False):
                    os.unlink(photo_path)
                    logger.info(f"🗑️ Fichier supprimé localement: {filename}")
            else:
                logger.error(f"❌ Échec du transfert: {filename}")
                logger.error(f"Erreur: {result.stderr}")
        except Exception as e:
            logger.error(f"❌ Erreur lors du transfert de {filename}: {e}")
    
    return successful_transfers

def main():
    """Fonction principale"""
    logger.info("🚀 Démarrage du script de transfert caméra-FTP")
    
    # Charger la configuration
    config = load_config()
    
    # Télécharger les photos depuis la caméra
    download_path = config['camera'].get('download_path', '/tmp/photos')
    photos = download_from_camera(download_path)
    
    # Transférer les photos vers le serveur FTP
    successful = upload_to_ftp(config, photos)
    
    logger.info(f"✅ Transfert terminé: {successful}/{len(photos)} photos transférées")

if __name__ == "__main__":
    main()
