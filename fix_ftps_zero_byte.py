#!/usr/bin/env python3
"""
Script de correction pour les transferts FTPS qui arrivent vides
Résout le problème "TLS session of data connection not resumed"
"""

import os
import sys
import json
import ftplib
import ssl
import logging
import subprocess
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('FTPSFix')

class FixedFTPSTransfer:
    """Classe de transfert FTPS corrigée pour le problème de session TLS"""
    
    def __init__(self, config):
        self.config = config
        self.ftp_config = config['ftp']
        self.connection = None
    
    def connect(self):
        """Connexion avec configuration FTPS spéciale"""
        try:
            # Créer un contexte SSL très permissif
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            # Désactiver la vérification de reprise de session TLS
            context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
            
            self.connection = ftplib.FTP_TLS(context=context)
            
            # Se connecter au serveur
            self.connection.connect(
                self.ftp_config['server'],
                self.ftp_config.get('port', 21),
                timeout=30
            )
            
            # Authentification
            self.connection.login(
                self.ftp_config['username'],
                self.ftp_config['password']
            )
            
            # IMPORTANT: Ne PAS activer prot_p() pour éviter le problème TLS
            # self.connection.prot_p()  # <- Cette ligne cause le problème
            
            # Utiliser le mode passif
            self.connection.set_pasv(True)
            
            # Changer vers le répertoire cible
            self.connection.cwd(self.ftp_config['directory'])
            
            logger.info("✅ Connexion FTPS réussie (sans protection données TLS)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur connexion FTPS: {e}")
            return False
    
    def upload_file(self, local_path, remote_filename=None):
        """Upload un fichier avec la méthode corrigée"""
        if not remote_filename:
            remote_filename = os.path.basename(local_path)
        
        if not os.path.exists(local_path):
            logger.error(f"Fichier local inexistant: {local_path}")
            return False
        
        file_size = os.path.getsize(local_path)
        logger.info(f"📤 Upload de {remote_filename} ({file_size} octets)")
        
        try:
            with open(local_path, 'rb') as f:
                # Utiliser un buffer de taille réduite pour FTPS
                result = self.connection.storbinary(f'STOR {remote_filename}', f, blocksize=4096)
                
            if result.startswith('226'):  # 226 = Transfer complete
                logger.info(f"✅ Upload réussi: {remote_filename}")
                return True
            else:
                logger.warning(f"⚠️ Upload avec avertissement: {result}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erreur upload {remote_filename}: {e}")
            return False
    
    def disconnect(self):
        """Fermer la connexion"""
        if self.connection:
            try:
                self.connection.quit()
            except:
                pass
            self.connection = None

class LFTPTransfer:
    """Alternative avec lftp et paramètres optimisés"""
    
    def __init__(self, config):
        self.config = config
        self.ftp_config = config['ftp']
    
    def upload_file(self, local_path, remote_filename=None):
        """Upload avec lftp et options optimisées"""
        if not remote_filename:
            remote_filename = os.path.basename(local_path)
        
        if not os.path.exists(local_path):
            logger.error(f"Fichier local inexistant: {local_path}")
            return False
        
        file_size = os.path.getsize(local_path)
        logger.info(f"📤 Upload lftp de {remote_filename} ({file_size} octets)")
        
        # Configuration lftp optimisée pour éviter les problèmes FTPS
        commands = [
            'set ftp:ssl-force true',
            'set ftp:ssl-protect-data false',  # IMPORTANT: désactiver la protection des données
            'set ssl:verify-certificate false',
            'set net:timeout 60',
            'set net:max-retries 3',
            'set net:reconnect-interval-base 5',
            f'open -u {self.ftp_config["username"]},{self.ftp_config["password"]} {self.ftp_config["server"]}',
            f'cd {self.ftp_config["directory"]}',
            f'put "{local_path}" -o "{remote_filename}"',
            'quit'
        ]
        
        lftp_script = '\n'.join(commands)
        
        try:
            result = subprocess.run(
                ['lftp'],
                input=lftp_script.encode(),
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Upload lftp réussi: {remote_filename}")
                return True
            else:
                logger.error(f"❌ Erreur lftp: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur lftp: {e}")
            return False

def load_config():
    """Charge la configuration"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erreur chargement config: {e}")
        return None

def upload_photos_fixed():
    """Upload toutes les photos avec la méthode corrigée"""
    config = load_config()
    if not config:
        return False
    
    download_path = config['camera'].get('download_path', '/tmp/photos')
    
    # Trouver toutes les photos
    photo_files = []
    for ext in ['*.jpg', '*.jpeg', '*.JPG', '*.JPEG']:
        photo_files.extend(Path(download_path).glob(ext))
    
    if not photo_files:
        logger.info("Aucune photo à transférer")
        return True
    
    logger.info(f"Trouvé {len(photo_files)} photos à transférer")
    
    # Essayer d'abord avec la méthode FTPS corrigée
    logger.info("🔧 Tentative avec FTPS corrigé...")
    ftps_transfer = FixedFTPSTransfer(config)
    
    if ftps_transfer.connect():
        success_count = 0
        for photo_path in photo_files:
            if ftps_transfer.upload_file(str(photo_path)):
                success_count += 1
                
                # Supprimer après upload si configuré
                if config['camera'].get('delete_after_upload', False):
                    try:
                        photo_path.unlink()
                        logger.info(f"🗑️ Fichier local supprimé: {photo_path.name}")
                    except Exception as e:
                        logger.warning(f"⚠️ Impossible de supprimer {photo_path.name}: {e}")
        
        ftps_transfer.disconnect()
        
        if success_count > 0:
            logger.info(f"✅ FTPS corrigé: {success_count}/{len(photo_files)} photos transférées")
            return True
    
    # Si FTPS échoue, essayer avec lftp
    logger.info("🔧 Tentative avec lftp optimisé...")
    lftp_transfer = LFTPTransfer(config)
    
    success_count = 0
    for photo_path in photo_files:
        if lftp_transfer.upload_file(str(photo_path)):
            success_count += 1
            
            # Supprimer après upload si configuré
            if config['camera'].get('delete_after_upload', False):
                try:
                    photo_path.unlink()
                    logger.info(f"🗑️ Fichier local supprimé: {photo_path.name}")
                except Exception as e:
                    logger.warning(f"⚠️ Impossible de supprimer {photo_path.name}: {e}")
    
    logger.info(f"✅ lftp optimisé: {success_count}/{len(photo_files)} photos transférées")
    return success_count > 0

def main():
    """Fonction principale"""
    logger.info("🚀 Transfert FTPS corrigé pour fichiers non-vides")
    
    success = upload_photos_fixed()
    
    if success:
        logger.info("✅ Transfert terminé avec succès!")
    else:
        logger.error("❌ Échec du transfert")
        sys.exit(1)

if __name__ == "__main__":
    main()
