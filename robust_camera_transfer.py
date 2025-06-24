#!/usr/bin/env python3
"""
Script robuste pour le téléchargement et transfert de photos depuis Nikon D800
Résout les problèmes de fichiers corrompus et transfert FTP/FTPS
"""

import os
import sys
import json
import logging
import subprocess
import time
import shutil
from datetime import datetime
from pathlib import Path
import tempfile

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/robust_transfer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('RobustTransfer')

class RobustCameraTransfer:
    """Classe pour gérer le téléchargement et transfert robuste depuis Nikon D800"""
    
    def __init__(self, config_path="config.json"):
        """Initialisation avec config"""
        # Charger la configuration
        self.config = self._load_config(config_path)
        self.download_path = self.config['camera'].get('download_path', '/tmp/photos')
        self.backup_path = "/tmp/photos_backup_{}".format(int(time.time()))
        
        # S'assurer que les répertoires existent
        os.makedirs(self.download_path, exist_ok=True)
        os.makedirs('logs', exist_ok=True)
    
    def _load_config(self, config_path):
        """Charge la configuration depuis le fichier"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erreur chargement configuration: {e}")
            # Configuration par défaut
            return {
                'ftp': {
                    'server': '192.168.1.22',
                    'port': 21,
                    'username': 'julien',
                    'password': '2004',
                    'directory': '/photos',
                    'use_ftps': True
                },
                'camera': {
                    'auto_detect': True,
                    'download_path': '/tmp/photos',
                    'delete_after_upload': False
                },
                'system': {
                    'log_level': 'INFO',
                    'check_interval': 5
                }
            }
    
    def clean_bad_files(self):
        """Nettoie les fichiers corrompus ou vides"""
        logger.info("🔍 Vérification et nettoyage des fichiers corrompus...")
        
        deleted = 0
        for file_path in Path(self.download_path).glob('*'):
            if not file_path.is_file():
                continue
                
            # Vérifier la taille
            size = os.path.getsize(file_path)
            if size == 0:
                logger.warning(f"Suppression fichier vide: {file_path}")
                os.unlink(file_path)
                deleted += 1
                continue
                
            # Vérifier l'intégrité des JPG
            if file_path.suffix.lower() in ['.jpg', '.jpeg'] or file_path.name.lower().startswith('dsc'):
                try:
                    with open(file_path, 'rb') as f:
                        header = f.read(3)
                        # Aller à la fin du fichier pour vérifier le footer JPEG
                        f.seek(-2, os.SEEK_END)
                        footer = f.read(2)
                        
                    # En-tête JPEG doit être FF D8 FF
                    if header != b'\xff\xd8\xff':
                        logger.warning(f"Fichier {file_path} n'a pas un en-tête JPEG valide")
                        # Créer une sauvegarde au lieu de supprimer
                        os.makedirs(self.backup_path, exist_ok=True)
                        shutil.move(file_path, os.path.join(self.backup_path, file_path.name))
                        deleted += 1
                        
                    # Footer JPEG doit être FF D9
                    elif footer != b'\xff\xd9':
                        logger.warning(f"Fichier {file_path} n'a pas un footer JPEG valide")
                        # Créer une sauvegarde au lieu de supprimer
                        os.makedirs(self.backup_path, exist_ok=True)
                        shutil.move(file_path, os.path.join(self.backup_path, file_path.name))
                        deleted += 1
                except Exception as e:
                    logger.error(f"Erreur vérification fichier {file_path}: {e}")
        
        logger.info(f"Nettoyage terminé: {deleted} fichiers déplacés/supprimés")
        return deleted
    
    def kill_interfering_processes(self):
        """Tue les processus qui peuvent interférer avec gphoto2"""
        processes = ['gphoto2', 'gvfs-gphoto2-volume-monitor']
        
        logger.info("🛑 Arrêt des processus qui pourraient interférer...")
        
        for proc in processes:
            try:
                subprocess.run(['pkill', '-f', proc], capture_output=True)
                time.sleep(1)  # Attendre que les processus soient bien arrêtés
            except Exception as e:
                logger.debug(f"Erreur lors de l'arrêt de {proc}: {e}")
    
    def detect_camera(self):
        """Détecte si une caméra compatible est connectée"""
        logger.info("🔍 Recherche d'appareils photo...")
        
        try:
            result = subprocess.run(
                ['gphoto2', '--auto-detect'],
                capture_output=True, 
                text=True,
                timeout=10
            )
            
            if "usb:" in result.stdout and result.returncode == 0:
                camera_info = [line for line in result.stdout.split('\n') 
                              if line.strip() and 'usb:' in line.lower()]
                
                if camera_info:
                    logger.info(f"📷 Caméra détectée: {camera_info[0].strip()}")
                    return True
            
            logger.warning("❌ Aucune caméra compatible détectée")
            return False
            
        except subprocess.TimeoutExpired:
            logger.error("⏱️ Timeout lors de la détection de caméra")
            return False
        except Exception as e:
            logger.error(f"❌ Erreur lors de la détection: {e}")
            return False
    
    def download_from_camera(self):
        """Télécharge les photos depuis la caméra"""
        logger.info("📥 Téléchargement des photos depuis la caméra...")
        
        files_before = set(os.listdir(self.download_path))
        
        try:
            # Utiliser gphoto2 avec les options optimales pour éviter la corruption
            cmd = [
                'gphoto2',
                '--get-all-files',
                '--skip-existing',
                '--filename', os.path.join(self.download_path, '%f')  # %f préserve l'extension
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True,
                text=True, 
                timeout=300  # Temps suffisant même pour beaucoup de photos
            )
            
            # Vérifier le résultat
            if "*** Error" in result.stdout or "*** Error" in result.stderr:
                logger.warning(f"⚠️ Problème potentiel: {result.stderr}")
            
            # Compter les nouveaux fichiers
            files_after = set(os.listdir(self.download_path))
            new_files = files_after - files_before
            
            # Vérifier et corriger les extensions manquantes
            fixed_files = []
            for filename in new_files:
                file_path = os.path.join(self.download_path, filename)
                
                # Vérifier si le fichier a une extension connue
                if not any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.nef', '.raw']):
                    # Tenter d'identifier le type de fichier
                    try:
                        with open(file_path, 'rb') as f:
                            header = f.read(10)
                            
                            # Vérifier s'il s'agit d'un JPEG (header FF D8 FF)
                            if header[0:3] == b'\xff\xd8\xff':
                                new_path = file_path + '.jpg'
                                os.rename(file_path, new_path)
                                logger.info(f"✅ Fichier JPEG renommé: {filename} → {filename}.jpg")
                                fixed_files.append(new_path)
                            else:
                                # Type inconnu, garder le fichier original
                                fixed_files.append(file_path)
                    except Exception as e:
                        logger.warning(f"⚠️ Erreur lors de l'identification du fichier {filename}: {e}")
                        fixed_files.append(file_path)
                else:
                    # Fichier avec extension correcte
                    fixed_files.append(file_path)
            
            logger.info(f"✅ {len(fixed_files)} photos téléchargées/traitées")
            return fixed_files
            
        except subprocess.TimeoutExpired:
            logger.error("⏱️ Timeout lors du téléchargement")
            return []
        except Exception as e:
            logger.error(f"❌ Erreur: {e}")
            return []
    
    def transfer_photos_lftp(self, file_paths):
        """Transfère les photos via lftp (plus fiable pour FTPS)"""
        if not file_paths:
            logger.info("Aucune photo à transférer")
            return 0
        
        logger.info(f"📤 Transfert de {len(file_paths)} photos via lftp...")
        
        # Vérifier que lftp est installé
        try:
            subprocess.run(['which', 'lftp'], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            logger.error("❌ lftp n'est pas installé. Installation avec: sudo apt install lftp")
            return 0
        
        ftp_config = self.config['ftp']
        successful = 0
        
        for file_path in file_paths:
            filename = os.path.basename(file_path)
            
            # Vérifier l'intégrité du fichier avant transfert
            if os.path.getsize(file_path) == 0:
                logger.warning(f"⚠️ Fichier vide, ignoré: {filename}")
                continue
                
            # Configuration du script lftp
            use_ftps = ftp_config.get('use_ftps', True)
            
            # Préparer les commandes lftp
            lftp_commands = []
            
            # Configuration selon le mode TLS/SSL
            if use_ftps:
                lftp_commands.extend([
                    'set ftp:ssl-force true',
                    'set ftp:ssl-protect-data true',
                    'set ssl:verify-certificate false'  # Nécessaire pour les certificats auto-signés
                ])
            
            # Commandes de base
            lftp_commands.extend([
                f'open -u {ftp_config["username"]},{ftp_config["password"]} {ftp_config["server"]}',
                f'cd {ftp_config["directory"]}',
                f'put "{file_path}" -o "{filename}"',
                'quit'
            ])
            
            lftp_script = '\n'.join(lftp_commands)
            
            try:
                logger.info(f"📤 Transfert de {filename}...")
                result = subprocess.run(
                    ['lftp'], 
                    input=lftp_script.encode(), 
                    capture_output=True,
                    text=True,
                    timeout=120  # 2 minutes de timeout par fichier
                )
                
                if result.returncode == 0:
                    logger.info(f"✅ Transfert réussi: {filename}")
                    successful += 1
                    
                    # Supprimer après transfert si configuré
                    if self.config['camera'].get('delete_after_upload', False):
                        try:
                            os.unlink(file_path)
                            logger.info(f"🗑️ Fichier local supprimé: {filename}")
                        except Exception as e:
                            logger.warning(f"⚠️ Impossible de supprimer le fichier local: {e}")
                else:
                    logger.error(f"❌ Échec du transfert: {filename}")
                    logger.error(f"Erreur: {result.stderr}")
            except Exception as e:
                logger.error(f"❌ Erreur lors du transfert de {filename}: {e}")
                
        logger.info(f"✅ Transfert terminé: {successful}/{len(file_paths)} photos transférées")
        return successful
    
    def purge_photos(self):
        """Supprime toutes les photos du répertoire de téléchargement"""
        logger.info(f"🗑️ Suppression de toutes les photos dans {self.download_path}...")
        
        try:
            count = 0
            for file_path in Path(self.download_path).glob('*'):
                if file_path.is_file():
                    file_path.unlink()
                    count += 1
            
            logger.info(f"✅ {count} fichiers supprimés")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la suppression: {e}")
            return False
    
    def run_workflow(self, purge_first=False):
        """Exécute le workflow complet"""
        logger.info("🚀 Démarrage du workflow de transfert robuste")
        
        # Étape 0: Purger si demandé
        if purge_first:
            self.purge_photos()
            
        # Étape 1: Nettoyer les processus interférents
        self.kill_interfering_processes()
        
        # Étape 2: Nettoyer les fichiers corrompus
        self.clean_bad_files()
        
        # Étape 3: Détecter la caméra
        if self.detect_camera():
            # Étape 4: Télécharger depuis la caméra
            photo_files = self.download_from_camera()
            
            # Étape 5: Transférer les photos
            if photo_files:
                transferred = self.transfer_photos_lftp(photo_files)
                return transferred > 0
        
        return False

# Point d'entrée si exécuté directement
if __name__ == "__main__":
    # Parser les arguments
    import argparse
    parser = argparse.ArgumentParser(description="Transfert robuste d'appareil photo vers FTP")
    parser.add_argument('--purge', action='store_true', help="Purger les photos avant téléchargement")
    parser.add_argument('--config', default='config.json', help="Chemin du fichier de configuration")
    args = parser.parse_args()
    
    # Exécuter le workflow
    transfer = RobustCameraTransfer(config_path=args.config)
    success = transfer.run_workflow(purge_first=args.purge)
    
    # Code de sortie pour intégration avec d'autres scripts
    sys.exit(0 if success else 1)
