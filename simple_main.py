#!/usr/bin/env python3
"""
Système de transfert automatique de photos via Raspberry Pi
Version simplifiée et légère
"""

import os
import sys
import time
import logging
import subprocess
import threading
import signal
from datetime import datetime
from pathlib import Path

# Imports simplifiés
from config_util import load_config, save_config
from simple_transfer import SimpleTransfer, create_transfer

# Configurer le logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/photo_transfer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('PhotoTransfer')

class SimpleFTPService:
    """Service de transfert de photos simplifié"""
    
    def __init__(self, config_path="config.json"):
        """Initialise le service avec la configuration"""
        self.config_path = config_path
        self.running = False
        self.transfer_thread = None
        self.config = None
        
        # Créer le répertoire de logs s'il n'existe pas
        os.makedirs('logs', exist_ok=True)
        
        # Charger la configuration
        self.reload_config()
        
        # Appliquer le niveau de log configuré
        self._configure_logging()
        
        # Créer le transfert
        self.transfer = create_transfer(self.config)
        
    def _configure_logging(self):
        """Configure le niveau de log selon la configuration"""
        if self.config and 'system' in self.config and 'log_level' in self.config['system']:
            level = self._parse_log_level(self.config['system']['log_level'])
            logger.setLevel(level)
            
            # Appliquer à tous les handlers
            for handler in logging.getLogger().handlers:
                handler.setLevel(level)
                
            logger.debug(f"Niveau de log configuré: {self.config['system']['log_level']}")
    
    def _parse_log_level(self, level_name):
        """Convertit un nom de niveau de log en constante"""
        levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        return levels.get(level_name.upper(), logging.INFO)
    
    def reload_config(self):
        """Recharge la configuration depuis le fichier"""
        try:
            self.config = load_config(self.config_path)
            logger.info("Configuration chargée avec succès")
            self._configure_logging()
            # Recharger aussi le module de transfert
            self.reload_transfer()
        except Exception as e:
            logger.error(f"Erreur chargement configuration: {e}")
            # Créer une configuration minimale
            self.config = {
                'ftp': {'server': 'localhost', 'port': 21, 'username': 'user', 
                       'password': 'password', 'directory': 'photos'},
                'camera': {'auto_detect': True, 'download_path': '/tmp/photos'},
                'system': {'log_level': 'INFO', 'check_interval': 5}
            }
    
    def reload_transfer(self):
        """Recharge le module de transfert avec la configuration actuelle"""
        try:
            self.transfer = create_transfer(self.config)
            logger.info("Module de transfert rechargé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors du rechargement du module de transfert: {e}")
            self.transfer = None
    
    def start(self):
        """Démarre le service de transfert"""
        if self.running:
            logger.warning("Le service est déjà en cours d'exécution")
            return
            
        self.running = True
        self.transfer_thread = threading.Thread(target=self._monitoring_loop)
        self.transfer_thread.daemon = True
        self.transfer_thread.start()
        
        logger.info("Service de transfert démarré")
    
    def stop(self):
        """Arrête le service de transfert"""
        if not self.running:
            logger.warning("Le service n'est pas en cours d'exécution")
            return
            
        logger.info("Arrêt du service de transfert...")
        self.running = False
        
        if self.transfer_thread:
            self.transfer_thread.join(timeout=5.0)
            if self.transfer_thread.is_alive():
                logger.warning("Le thread de transfert ne s'est pas arrêté proprement")
    
    def _monitoring_loop(self):
        """Boucle principale de surveillance et transfert"""
        logger.info("Démarrage de la boucle de surveillance")
        
        while self.running:
            try:
                # Vérifier la présence de photos à transférer
                photos = self._scan_for_photos()
                
                if photos:
                    logger.info(f"Trouvé {len(photos)} photos à transférer")
                    self._upload_photos(photos)
                
                # Attendre avant la prochaine vérification
                check_interval = self.config['system'].get('check_interval', 5)
                time.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Erreur dans la boucle de surveillance: {e}")
                time.sleep(10)  # Attendre un peu plus long en cas d'erreur
    
    def _scan_for_photos(self):
        """Recherche les photos disponibles dans le dossier configuré et sur la caméra"""
        photos = []
        
        try:
            # 1. Détecter et télécharger depuis la caméra si activé
            if self.config['camera'].get('auto_detect', True):
                new_photos = self._detect_and_download_from_camera()
                photos.extend(new_photos)
                if new_photos:
                    logger.info(f"Nouvelles photos téléchargées depuis la caméra: {len(new_photos)}")
            
            # 2. Rechercher les fichiers dans le dossier de téléchargement
            download_path = self.config['camera'].get('download_path', '/tmp/photos')
            
            # Créer le répertoire s'il n'existe pas
            os.makedirs(download_path, exist_ok=True)
            
            # Rechercher les fichiers images
            extensions = ['.jpg', '.jpeg', '.png', '.raw', '.cr2', '.nef']
            
            for ext in extensions:
                for photo in Path(download_path).glob(f"*{ext}"):
                    photo_path = str(photo)
                    if photo_path not in photos:  # Éviter les doublons
                        photos.append(photo_path)
                for photo in Path(download_path).glob(f"*{ext.upper()}"):
                    photo_path = str(photo)
                    if photo_path not in photos:  # Éviter les doublons
                        photos.append(photo_path)
            
            logger.debug(f"Total photos trouvées: {len(photos)}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de photos: {e}")
        
        return photos
    
    def _upload_photos(self, photos):
        """Upload les photos trouvées vers le serveur"""
        if not photos:
            return
            
        # Se connecter au serveur
        if not self.transfer.connect():
            logger.error("Impossible de se connecter au serveur, abandon du transfert")
            return
            
        # Créer le répertoire distant si nécessaire
        remote_dir = self.config['ftp']['directory']
        if not self.transfer.ensure_dir(remote_dir):
            logger.error(f"Impossible de créer/accéder au répertoire {remote_dir}")
            self.transfer.disconnect()
            return
        
        # Transférer chaque photo
        success_count = 0
        
        for photo_path in photos:
            try:
                # Déterminer le nom du fichier distant
                filename = os.path.basename(photo_path)
                remote_path = os.path.join(remote_dir, filename).replace('\\', '/')
                
                # Upload du fichier
                logger.info(f"Upload de {filename}...")
                
                if self.transfer.upload_file(photo_path, remote_path):
                    logger.info(f"Upload réussi: {filename}")
                    success_count += 1
                    
                    # Supprimer le fichier local si configuré
                    if self.config['camera'].get('delete_after_upload', False):
                        try:
                            os.unlink(photo_path)
                            logger.info(f"Fichier local supprimé: {photo_path}")
                        except Exception as e:
                            logger.warning(f"Impossible de supprimer le fichier local: {e}")
                else:
                    logger.error(f"Échec de l'upload: {filename}")
                    
            except Exception as e:
                logger.error(f"Erreur lors de l'upload de {photo_path}: {e}")
        
        # Déconnecter
        self.transfer.disconnect()
        
        # Résumé
        logger.info(f"Transfert terminé: {success_count}/{len(photos)} photos transférées")
    
    def test_connection(self):
        """Test la connexion au serveur FTP/SFTP"""
        logger.info("Test de la connexion au serveur...")
        
        try:
            result = self.transfer.test_connection()
            success = result['success']
            message = result['message']
            
            if success:
                logger.info(f"Test réussi: {message}")
            else:
                logger.error(f"Test échoué: {message}")
                
            return success, message
            
        except Exception as e:
            error_msg = f"Erreur lors du test de connexion: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def upload_photo_to_ftp(self, photo_path):
        """Upload manuel d'une photo vers le serveur"""
        if not os.path.isfile(photo_path):
            logger.error(f"Le fichier n'existe pas: {photo_path}")
            return False
            
        try:
            # Se connecter
            if not self.transfer.connect():
                logger.error("Impossible de se connecter au serveur")
                return False
                
            # Déterminer le nom du fichier distant
            filename = os.path.basename(photo_path)
            remote_dir = self.config['ftp']['directory']
            remote_path = os.path.join(remote_dir, filename).replace('\\', '/')
            
            # S'assurer que le répertoire existe
            if not self.transfer.ensure_dir(remote_dir):
                logger.error(f"Impossible de créer/accéder au répertoire {remote_dir}")
                self.transfer.disconnect()
                return False
            
            # Upload avec fallbacks
            logger.info(f"Upload manuel de {filename}...")
            
            # 1. Essayer l'upload normal
            result = self.transfer.upload_file(photo_path, remote_path)
            
            # 2. Si échec, essayer le fallback SFTP
            if not result and hasattr(self.transfer, 'upload_file_with_fallback'):
                logger.info("Tentative de fallback SFTP...")
                result = self.transfer.upload_file_with_fallback(photo_path, remote_path)
            
            # 3. Si échec, utiliser le backup local (mode test)
            if not result and hasattr(self.transfer, 'upload_file_local_backup'):
                logger.info("Utilisation du backup local...")
                result = self.transfer.upload_file_local_backup(photo_path, filename)
            
            # Déconnecter
            self.transfer.disconnect()
            
            if result:
                logger.info(f"Upload manuel réussi: {filename}")
            else:
                logger.error(f"Échec de l'upload manuel: {filename}")
                
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de l'upload manuel: {e}")
            return False
    
    def _detect_and_download_from_camera(self):
        """Détecte et télécharge les nouvelles photos depuis la caméra avec gphoto2"""
        photos_downloaded = []
        
        try:
            # Vérifier si une caméra est connectée
            import subprocess
            result = subprocess.run(['gphoto2', '--auto-detect'], 
                                 capture_output=True, text=True, timeout=10)
            
            if "Model" not in result.stdout or len(result.stdout.strip().split('\n')) <= 2:
                logger.debug("Aucune caméra détectée")
                return photos_downloaded
            
            camera_info = [line for line in result.stdout.split('\n') if 'usb:' in line.lower()]
            if camera_info:
                logger.info(f"Caméra détectée: {camera_info[0].split()[0]}")
            else:
                logger.info("Caméra détectée")
            
            # Obtenir le chemin de téléchargement
            download_path = self.config['camera'].get('download_path', '/tmp/photos')
            os.makedirs(download_path, exist_ok=True)
            
            # Méthode simple : télécharger toutes les nouvelles photos
            logger.info("Téléchargement des nouvelles photos...")
            
            # Compter les fichiers avant téléchargement
            files_before = set(os.listdir(download_path))
            
            # Télécharger toutes les nouvelles photos (celles pas encore téléchargées)
            download_result = subprocess.run([
                'gphoto2', 
                '--get-all-files',
                '--skip-existing', 
                '--filename', os.path.join(download_path, '%f')
            ], capture_output=True, text=True, timeout=120)
            
            # Compter les nouveaux fichiers
            files_after = set(os.listdir(download_path))
            new_files = files_after - files_before
            
            if download_result.returncode == 0 or new_files:
                photos_downloaded = [os.path.join(download_path, f) for f in new_files 
                                   if any(f.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.nef', '.raw', '.cr2'])]
                
                if photos_downloaded:
                    logger.info(f"Photos téléchargées avec succès: {len(photos_downloaded)}")
                else:
                    logger.debug("Aucune nouvelle photo à télécharger")
            else:
                logger.warning(f"Problème lors du téléchargement: {download_result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("Timeout lors de la communication avec la caméra")
        except Exception as e:
            logger.error(f"Erreur lors de la détection de caméra: {e}")
        
        return photos_downloaded

# Point d'entrée principal si exécuté directement
if __name__ == "__main__":
    # Créer le service
    service = SimpleFTPService()
    
    # Gérer l'arrêt propre avec les signaux
    def signal_handler(sig, frame):
        logger.info("Signal d'arrêt reçu, arrêt en cours...")
        service.stop()
        sys.exit(0)
    
    # Enregistrer le gestionnaire de signal
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Démarrer le service
    service.start()
    
    # Maintenir le processus en vie
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Interruption clavier, arrêt en cours...")
        service.stop()
