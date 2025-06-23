#!/usr/bin/env python3
"""
Script de surveillance automatique qui détecte les fichiers JPG dans /tmp/photos
et les transfère immédiatement via FTP vers le serveur configuré.
Utilise le script lftp_send_photos.sh en mode fichier unique pour les transferts.
"""
import os
import time
import subprocess
import logging
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration
CONFIG_FILE = "/home/server01/projet_ftp/Projet_FTP/config.json"
LOCAL_DIR = "/tmp/photos"
FTP_SCRIPT = "/home/server01/projet_ftp/Projet_FTP/lftp_send_jpg_fixed.sh"  # Utiliser la version corrigée

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='/home/server01/projet_ftp/Projet_FTP/logs/auto_transfer.log')
logger = logging.getLogger('AutoTransfer')

# Charger la configuration
def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erreur de chargement de la configuration: {e}")
        return {
            "ftp": {
                "server": "192.168.1.22",
                "port": 21,
                "username": "julien",
                "password": "2004",
                "directory": "/photos"
            },
            "camera": {
                "download_path": "/tmp/photos"
            }
        }

config = load_config()
LOCAL_DIR = config.get('camera', {}).get('download_path', '/tmp/photos')

# Gestionnaire d'événements pour nouveaux fichiers
class NewPhotoHandler(FileSystemEventHandler):
    def __init__(self):
        self.processing = set()  # Garde la trace des fichiers en cours de traitement
        
    def on_created(self, event):
        # Ignorer les événements de répertoire
        if event.is_directory:
            return
            
        # Vérifier s'il s'agit d'un fichier JPG
        if self._is_jpg_file(event.src_path):
            self._handle_new_jpg(event.src_path)
    
    def on_modified(self, event):
        # Certains systèmes génèrent un événement modified après created
        if event.is_directory or event.src_path in self.processing:
            return
            
        # Vérifier s'il s'agit d'un fichier JPG
        if self._is_jpg_file(event.src_path):
            self._handle_new_jpg(event.src_path)
    
    def _is_jpg_file(self, path):
        """Vérifie si le fichier est une image JPG ou un fichier sans extension."""
        # Vérifier l'extension
        _, ext = os.path.splitext(path.lower())
        if ext in ['.jpg', '.jpeg'] or ext == '':
            # Vérifier qu'il s'agit bien d'un fichier complet (pas en cours d'écriture)
            # Une façon simple est de vérifier si la taille reste stable pendant un court délai
            try:
                size1 = os.path.getsize(path)
                time.sleep(0.5)  # Attendre un peu
                size2 = os.path.getsize(path)
                return size1 == size2 and size1 > 0
            except (FileNotFoundError, OSError):
                return False
        return False
    
    def _handle_new_jpg(self, jpg_path):
        """Gère un nouveau fichier JPG détecté."""
        # Éviter de traiter plusieurs fois
        if jpg_path in self.processing:
            return
        
        try:
            self.processing.add(jpg_path)
            
            filename = os.path.basename(jpg_path)
            logger.info(f"Nouveau fichier JPG détecté: {filename}")
            
            # Attendre que le fichier soit complètement écrit
            time.sleep(1)
            
            # Transférer le fichier via FTP
            if self._transfer_file(jpg_path):
                # Supprimer la photo de l'appareil photo après transfert
                delete_photo_from_camera(filename)
        finally:
            # Retirer de la liste des traitements en cours
            if jpg_path in self.processing:
                self.processing.remove(jpg_path)
    
    def _transfer_file(self, file_path):
        """Transfère un fichier via FTP en utilisant le script lftp_send_jpg.sh."""
        filename = os.path.basename(file_path)
        logger.info(f"Transfert FTP de {filename}...")
        
        try:
            # Utiliser le script lftp_send_jpg.sh pour le transfert d'un seul fichier
            cmd = [FTP_SCRIPT, file_path]
            
            # Exécuter le script shell avec le chemin du fichier en paramètre
            process = subprocess.Popen(cmd, 
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
            stdout, stderr = process.communicate(timeout=60)
            
            if process.returncode == 0:
                logger.info(f"Transfert FTP réussi: {filename}")
                # Note: La suppression de l'appareil photo se fait maintenant après téléchargement
                return True
            else:
                logger.error(f"Échec du transfert FTP pour {filename}: {stderr.decode()}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout lors du transfert de {filename}")
            return False
        except Exception as e:
            logger.error(f"Erreur lors du transfert de {filename}: {e}")
            return False

def delete_photo_from_camera(filename):
    """Supprimer une photo spécifique de l'appareil photo"""
    try:
        # Extraire le nom de base sans extension pour la recherche
        base_name = os.path.splitext(filename)[0]
        
        logger.info(f"Tentative de suppression de {base_name} de l'appareil photo...")
        
        # Lister les fichiers de l'appareil pour trouver celui qui correspond
        result = subprocess.run(['gphoto2', '--list-files'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Chercher le fichier correspondant dans la liste
            lines = result.stdout.split('\n')
            for line in lines:
                if base_name in line and ('.JPG' in line or '.jpg' in line):
                    # Extraire le chemin du fichier (format: #N filename ...)
                    parts = line.split()
                    if len(parts) >= 2 and parts[0].startswith('#'):
                        file_number = parts[0][1:]  # Enlever le #
                        
                        # Supprimer le fichier par son numéro
                        delete_cmd = ['gphoto2', '--delete-file', file_number]
                        delete_result = subprocess.run(delete_cmd, 
                                                     capture_output=True, text=True, timeout=30)
                        
                        if delete_result.returncode == 0:
                            logger.info(f"Photo {base_name} supprimée de l'appareil photo")
                            return True
                        else:
                            logger.warning(f"Échec suppression {base_name} de l'appareil: {delete_result.stderr}")
                            return False
            
            logger.info(f"Photo {base_name} non trouvée sur l'appareil photo (déjà supprimée?)")
            return True
        else:
            logger.warning(f"Impossible de lister les fichiers de l'appareil: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout lors de la suppression de {filename} de l'appareil")
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de {filename} de l'appareil: {e}")
        return False

def main():
    """Point d'entrée principal du script."""
    # S'assurer que le répertoire de surveillance existe
    os.makedirs(LOCAL_DIR, exist_ok=True)
    
    # S'assurer que le répertoire de logs existe
    os.makedirs('/home/server01/projet_ftp/Projet_FTP/logs', exist_ok=True)
    
    logger.info(f"Démarrage surveillance auto-transfert JPG dans {LOCAL_DIR}")
    logger.info(f"Configuration: {config}")
    
    # Créer l'observateur et le gestionnaire
    event_handler = NewPhotoHandler()
    observer = Observer()
    observer.schedule(event_handler, LOCAL_DIR, recursive=False)
    observer.start()
    
    # Vérifier les fichiers existants au démarrage
    logger.info("Vérification des fichiers JPG existants...")
    for filename in os.listdir(LOCAL_DIR):
        file_path = os.path.join(LOCAL_DIR, filename)
        if os.path.isfile(file_path) and event_handler._is_jpg_file(file_path):
            logger.info(f"Fichier JPG existant trouvé: {filename}")
            event_handler._handle_new_jpg(file_path)
    
    try:
        # Garder le script en cours d'exécution
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Arrêt demandé par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}")
    finally:
        observer.stop()
        observer.join()

if __name__ == "__main__":
    main()
