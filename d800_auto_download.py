#!/usr/bin/env python3
"""
Script de récupération automatique des photos depuis le Nikon D800
Utilise gphoto2 pour télécharger les nouvelles photos dans /tmp/photos
Le système de surveillance existant se charge ensuite du transfert FTP
"""

import os
import time
import subprocess
import logging
import json
import signal
import sys
from datetime import datetime

# Configuration
CONFIG_FILE = "/home/server01/projet_ftp/Projet_FTP/config.json"
LOG_FILE = "/home/server01/projet_ftp/Projet_FTP/logs/d800_download.log"

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('D800Download')

def load_config():
    """Charger la configuration depuis config.json"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erreur de chargement de la configuration: {e}")
        return {
            "camera": {
                "download_path": "/tmp/photos",
                "check_interval": 30
            }
        }

def kill_gvfs_processes():
    """Arrêter les processus gvfs qui peuvent bloquer l'accès à l'appareil photo"""
    processes_to_kill = [
        "gvfs-gphoto2-volume-monitor",
        "gvfs-udisks2-volume-monitor",
        "gvfs-mtp-volume-monitor"
    ]
    
    for process in processes_to_kill:
        try:
            result = subprocess.run(['pkill', '-f', process], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Processus {process} arrêté")
        except Exception as e:
            logger.debug(f"Impossible d'arrêter {process}: {e}")

def check_camera_connection():
    """Vérifier si l'appareil photo est connecté et accessible"""
    try:
        result = subprocess.run(['gphoto2', '--auto-detect'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and 'Nikon' in result.stdout:
            logger.debug("Appareil photo Nikon détecté")
            return True
        else:
            logger.debug("Aucun appareil photo détecté")
            return False
    except Exception as e:
        logger.debug(f"Erreur lors de la détection de l'appareil photo: {e}")
        return False

def download_new_photos(download_path):
    """Télécharger les nouvelles photos depuis l'appareil photo"""
    try:
        # S'assurer que le répertoire de destination existe
        os.makedirs(download_path, exist_ok=True)
        
        # Changer vers le répertoire de destination et télécharger
        original_dir = os.getcwd()
        os.chdir(download_path)
        
        # Commande pour télécharger les nouvelles photos avec noms originaux
        # On utilise --filename=%f.%C pour forcer gphoto2 à ajouter l'extension du fichier 
        # en se basant sur le type MIME du fichier
        cmd = [
            'gphoto2',
            '--get-all-files',
            '--skip-existing',
            '--filename=%f.%C'  # %f=nom du fichier original, %C=extension basée sur le type MIME
        ]
        
        logger.info("Téléchargement des nouvelles photos...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            # Compter le nombre de fichiers téléchargés
            lines = result.stdout.split('\n')
            downloaded_count = 0
            
            for line in lines:
                if 'Saving file as' in line:
                    downloaded_count += 1
            
            if downloaded_count > 0:
                logger.info(f"{downloaded_count} nouvelle(s) photo(s) téléchargée(s)")
                return downloaded_count
            else:
                logger.debug("Aucune nouvelle photo à télécharger")
                return 0
        else:
            logger.error(f"Erreur lors du téléchargement: {result.stderr}")
            return -1
            
    except subprocess.TimeoutExpired:
        logger.error("Timeout lors du téléchargement des photos")
        return -1
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement: {e}")
        return -1
    finally:
        # Restaurer le répertoire de travail original
        try:
            os.chdir(original_dir)
        except:
            pass

def cleanup_old_photos(download_path, max_age_hours=24):
    """Nettoyer les anciennes photos si elles n'ont pas été transférées"""
    try:
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for filename in os.listdir(download_path):
            file_path = os.path.join(download_path, filename)
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > max_age_seconds:
                    os.remove(file_path)
                    logger.info(f"Ancienne photo supprimée: {filename}")
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage: {e}")

def rename_files_without_extension(download_path):
    """Renomme tous les fichiers sans extension en .jpg dans le dossier donné."""
    for filename in os.listdir(download_path):
        file_path = os.path.join(download_path, filename)
        if os.path.isfile(file_path):
            name, ext = os.path.splitext(filename)
            if ext == '':
                new_path = file_path + '.jpg'
                try:
                    os.rename(file_path, new_path)
                    logger.info(f"Fichier renommé (auto): {filename} -> {os.path.basename(new_path)}")
                except Exception as e:
                    logger.warning(f"Impossible de renommer {file_path}: {e}")

def add_jpg_extension_to_files(download_path):
    """Ajoute l'extension .JPG aux fichiers qui n'en ont pas et vérifie les types MIME"""
    try:
        added_count = 0
        logger.info("Vérification des extensions des fichiers téléchargés...")
        
        for filename in os.listdir(download_path):
            file_path = os.path.join(download_path, filename)
            if os.path.isfile(file_path) and not filename.startswith('.'):
                name, ext = os.path.splitext(filename)
                
                # Cas 1: Fichier sans extension
                if ext == '':
                    # Vérifier si c'est bien une image JPEG en examinant les premiers octets du fichier
                    try:
                        with open(file_path, 'rb') as f:
                            header = f.read(11)
                            # Vérifier la signature JPEG (commence par FF D8 FF)
                            is_jpeg = header[0:3] == b'\xff\xd8\xff'
                        
                        if is_jpeg:
                            new_path = file_path + '.JPG'
                            os.rename(file_path, new_path)
                            logger.info(f"Extension JPG ajoutée (fichier JPEG détecté): {filename} -> {os.path.basename(new_path)}")
                            added_count += 1
                        else:
                            # Si ce n'est pas un JPEG, essayer de déduire le type
                            # Mais par défaut, considérer comme JPG pour la compatibilité
                            new_path = file_path + '.JPG'
                            os.rename(file_path, new_path)
                            logger.warning(f"Extension JPG ajoutée par défaut (type non détecté): {filename}")
                            added_count += 1
                    except Exception as e:
                        logger.error(f"Erreur lors de l'analyse du fichier {filename}: {e}")
                
                # Cas 2: Extension en minuscules (pour normalisation)
                elif ext.lower() in ['.jpg', '.jpeg'] and ext != '.JPG':
                    # Normaliser l'extension en .JPG
                    new_path = os.path.join(download_path, name + '.JPG')
                    try:
                        os.rename(file_path, new_path)
                        logger.debug(f"Extension normalisée: {filename} -> {os.path.basename(new_path)}")
                        added_count += 1
                    except Exception as e:
                        logger.warning(f"Impossible de normaliser l'extension de {filename}: {e}")
        
        if added_count > 0:
            logger.info(f"{added_count} fichier(s) ont été corrigés avec l'extension .JPG")
        else:
            logger.debug("Aucun fichier à corriger (tous possèdent déjà l'extension correcte)")
            
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des extensions: {e}")

def delete_photos_from_camera():
    """Supprimer toutes les photos de l'appareil photo après téléchargement réussi"""
    try:
        logger.info("Suppression des photos de l'appareil photo...")
        
        # D'abord, tuer les processus gvfs qui peuvent bloquer
        kill_gvfs_processes()
        time.sleep(1)
        
        # Utiliser le script spécialisé pour la suppression des fichiers un par un
        # car le D800 ne supporte pas la commande --delete-all-files
        cmd = ['python3', '/home/server01/projet_ftp/Projet_FTP/d800_delete.py']
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            logger.info("Photos supprimées de l'appareil photo avec succès")
            return True
        else:
            logger.warning(f"Erreur lors de la suppression des photos de l'appareil: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("Timeout lors de la suppression des photos de l'appareil")
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la suppression des photos de l'appareil: {e}")
        return False

def signal_handler(signum, frame):
    """Gestionnaire de signal pour arrêt propre"""
    logger.info("Arrêt demandé, nettoyage en cours...")
    sys.exit(0)

def main():
    """Fonction principale"""
    # Gestionnaire de signaux pour arrêt propre
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Charger la configuration
    config = load_config()
    download_path = config.get('camera', {}).get('download_path', '/tmp/photos')
    check_interval = config.get('camera', {}).get('check_interval', 30)
    delete_from_camera = config.get('camera', {}).get('delete_from_camera', False)
    
    logger.info(f"Démarrage du téléchargement automatique D800")
    logger.info(f"Répertoire de destination: {download_path}")
    logger.info(f"Intervalle de vérification: {check_interval} secondes")
    logger.info(f"Suppression de l'appareil photo: {'Activée' if delete_from_camera else 'Désactivée'}")
    
    # S'assurer que le répertoire de logs existe
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    # S'assurer que le répertoire de destination existe
    os.makedirs(download_path, exist_ok=True)
    
    # Compteur d'échecs consécutifs
    consecutive_failures = 0
    max_consecutive_failures = 3
    
    while True:
        try:
            # Libérer l'accès USB
            kill_gvfs_processes()
            
            # Attendre un peu que les processus se terminent
            time.sleep(2)
            
            # Vérifier si l'appareil photo est connecté
            if check_camera_connection():
                # Télécharger les nouvelles photos
                downloaded = download_new_photos(download_path)
                
                # Toujours ajouter/vérifier les extensions JPG 
                # même si gphoto2 devrait maintenant le faire correctement avec --filename=%f.%C
                add_jpg_extension_to_files(download_path)
                
                if downloaded > 0:
                    logger.info(f"Téléchargement terminé: {downloaded} photo(s)")
                    # Réinitialiser le compteur d'échecs
                    consecutive_failures = 0
                    
                    # Supprimer IMMÉDIATEMENT les photos de l'appareil pour éviter les re-téléchargements
                    if delete_from_camera:
                        try:
                            delete_success = delete_photos_from_camera()
                            if not delete_success:
                                logger.warning("La suppression des photos de l'appareil a échoué.")
                                # Si la suppression échoue mais que les photos sont téléchargées,
                                # nous continuons quand même pour ne pas bloquer le processus
                        except Exception as del_error:
                            logger.error(f"Exception lors de la suppression des photos: {del_error}")
                elif downloaded == -1:
                    consecutive_failures += 1
                    logger.warning(f"Erreur lors du téléchargement ({consecutive_failures}/{max_consecutive_failures})")
                    
                    if consecutive_failures >= max_consecutive_failures:
                        logger.error(f"Trop d'échecs consécutifs, redémarrage du processus gphoto2")
                        # Forcer le redémarrage de gphoto2
                        os.system("pkill -9 gphoto2")
                        consecutive_failures = 0
                        time.sleep(30)
                    else:
                        time.sleep(10)
                    continue
            else:
                logger.debug("Aucun appareil photo connecté")
                consecutive_failures = 0  # Réinitialiser, ce n'est pas un échec de connexion
            
            # Nettoyer les anciennes photos si nécessaire
            cleanup_old_photos(download_path)
            
            # Attendre avant la prochaine vérification
            time.sleep(check_interval)
            
        except KeyboardInterrupt:
            logger.info("Arrêt demandé par l'utilisateur")
            break
        except Exception as e:
            logger.error(f"Erreur inattendue: {e}")
            consecutive_failures += 1
            time.sleep(10)

if __name__ == "__main__":
    main()
