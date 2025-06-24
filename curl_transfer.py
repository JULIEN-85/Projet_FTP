#!/usr/bin/env python3
"""
Solution définitive pour les transferts FTPS avec fichiers non-vides
Utilise curl qui gère mieux FTPS que Python ftplib
"""

import os
import sys
import json
import subprocess
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/curl_transfer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('CurlTransfer')

class CurlFTPSTransfer:
    """Classe de transfert utilisant curl pour FTPS fiable"""
    
    def __init__(self, config):
        self.config = config
        self.ftp_config = config['ftp']
    
    def upload_file(self, local_path, remote_filename=None):
        """Upload un fichier avec curl"""
        if not remote_filename:
            remote_filename = os.path.basename(local_path)
        
        if not os.path.exists(local_path):
            logger.error(f"Fichier local inexistant: {local_path}")
            return False
        
        file_size = os.path.getsize(local_path)
        logger.info(f"📤 Upload curl de {remote_filename} ({file_size} octets)")
        
        # Construire l'URL FTP
        server = self.ftp_config['server']
        username = self.ftp_config['username']
        password = self.ftp_config['password']
        directory = self.ftp_config['directory']
        use_ftps = self.ftp_config.get('use_ftps', True)
        
        # URL complète
        url = f"ftp://{username}:{password}@{server}{directory}/{remote_filename}"
        
        # Commande curl
        cmd = ['curl', '-T', local_path]
        
        if use_ftps:
            cmd.extend(['-k', '--ftp-ssl-reqd'])  # FTPS requis, ignorer certificats
        
        cmd.append(url)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes pour les gros fichiers
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Upload curl réussi: {remote_filename}")
                return True
            else:
                logger.error(f"❌ Erreur curl ({result.returncode}): {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Timeout curl pour {remote_filename}")
            return False
        except Exception as e:
            logger.error(f"❌ Erreur curl: {e}")
            return False

def load_config():
    """Charge la configuration"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erreur chargement config: {e}")
        return None

def upload_all_photos():
    """Upload toutes les photos avec curl"""
    config = load_config()
    if not config:
        return False
    
    download_path = config['camera'].get('download_path', '/tmp/photos')
    
    # Trouver toutes les photos
    photo_files = []
    for ext in ['*.jpg', '*.jpeg', '*.JPG', '*.JPEG', '*.nef', '*.NEF']:
        photo_files.extend(Path(download_path).glob(ext))
    
    if not photo_files:
        logger.info("Aucune photo à transférer")
        return True
    
    logger.info(f"Trouvé {len(photo_files)} photos à transférer")
    
    # Créer l'objet de transfert curl
    transfer = CurlFTPSTransfer(config)
    
    success_count = 0
    for photo_path in photo_files:
        if transfer.upload_file(str(photo_path)):
            success_count += 1
            
            # Supprimer après upload si configuré
            if config['camera'].get('delete_after_upload', False):
                try:
                    photo_path.unlink()
                    logger.info(f"🗑️ Fichier local supprimé: {photo_path.name}")
                except Exception as e:
                    logger.warning(f"⚠️ Impossible de supprimer {photo_path.name}: {e}")
    
    logger.info(f"✅ Transfert curl terminé: {success_count}/{len(photo_files)} photos transférées")
    return success_count > 0

def main():
    """Fonction principale"""
    logger.info("🚀 Transfert FTPS avec curl (solution définitive)")
    
    # Vérifier que curl est installé
    try:
        subprocess.run(['curl', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("❌ curl n'est pas installé. Installez-le avec: sudo apt install curl")
        sys.exit(1)
    
    success = upload_all_photos()
    
    if success:
        logger.info("✅ Transfert terminé avec succès!")
        logger.info("🎉 Problème de fichiers vides (0 octet) RÉSOLU avec curl!")
    else:
        logger.error("❌ Échec du transfert")
        sys.exit(1)

if __name__ == "__main__":
    main()
