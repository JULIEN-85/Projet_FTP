#!/usr/bin/env python3
"""
Script pour supprimer toutes les photos de la carte SD du Nikon D800
Cette approche est nécessaire car le D800 ne supporte pas la commande --delete-all-files
et nécessite de supprimer les fichiers un par un.
"""

import subprocess
import logging
import time
import os
import sys
import re
import signal

# Configuration du logging
LOG_FILE = "/home/server01/projet_ftp/Projet_FTP/logs/d800_delete.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('D800Delete')

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

def reset_usb_device():
    """Reset le périphérique USB pour améliorer la stabilité"""
    try:
        # Obtenir les infos sur les périphériques USB
        result = subprocess.run(['lsusb'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        # Chercher le Nikon
        for line in lines:
            if 'Nikon' in line:
                # Exemple de ligne: Bus 003 Device 005: ID 04b0:0428 Nikon Corp. D800
                match = re.search(r'Bus (\d+) Device (\d+):', line)
                if match:
                    bus = match.group(1)
                    device = match.group(2)
                    
                    # Reset USB
                    logger.info(f"Reset USB pour Nikon: Bus {bus}, Device {device}")
                    
                    # On ne peut pas exécuter directement cette commande sans sudo,
                    # donc on la journalise seulement pour référence manuelle
                    logger.info(f"Pour reset manuellement: sudo sh -c 'echo 0 > /sys/bus/usb/devices/{bus}-{device}/authorized; sleep 2; echo 1 > /sys/bus/usb/devices/{bus}-{device}/authorized'")
    except Exception as e:
        logger.warning(f"Impossible de reset l'USB: {e}")

def test_camera_connection():
    """Vérifier si l'appareil photo est connecté et accessible"""
    try:
        result = subprocess.run(['gphoto2', '--auto-detect'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and 'Nikon' in result.stdout:
            logger.info("Appareil photo Nikon détecté")
            return True
        else:
            logger.error("Aucun appareil photo détecté")
            return False
    except Exception as e:
        logger.error(f"Erreur lors de la détection de l'appareil photo: {e}")
        return False

def get_camera_files():
    """Lister les fichiers disponibles sur l'appareil photo"""
    try:
        result = subprocess.run(['gphoto2', '--list-files'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            files = []
            lines = result.stdout.split('\n')
            
            for line in lines:
                # Format: #1 DSC_0001.JPG etc.
                if line.startswith('#'):
                    try:
                        parts = line.split(' ', 1)
                        if len(parts) > 1:
                            file_num = parts[0][1:]  # Supprimer le # au début
                            file_path = parts[1].strip()
                            files.append((file_num, file_path))
                    except:
                        pass
            
            logger.info(f"Trouvé {len(files)} fichiers sur l'appareil")
            return files
        else:
            if "Could not claim the USB device" in result.stderr:
                logger.error("Impossible d'accéder à l'appareil photo: périphérique USB occupé")
            else:
                logger.error(f"Erreur lors du listage des fichiers: {result.stderr}")
            return []
    except Exception as e:
        logger.error(f"Exception lors du listage des fichiers: {e}")
        return []

def delete_file(file_num):
    """Supprimer un fichier spécifique de l'appareil photo par son numéro"""
    try:
        cmd = ['gphoto2', f'--delete-file={file_num}']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            logger.debug(f"Fichier #{file_num} supprimé")
            return True
        else:
            logger.warning(f"Impossible de supprimer le fichier #{file_num}: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Exception lors de la suppression du fichier #{file_num}: {e}")
        return False

def delete_all_files_individually():
    """Supprimer tous les fichiers de l'appareil photo un par un"""
    # Arrêter les processus qui peuvent interférer
    kill_gvfs_processes()
    time.sleep(2)
    
    # Vérifier la connexion
    if not test_camera_connection():
        logger.error("Appareil photo non connecté, impossible de supprimer les fichiers")
        return False
    
    # Obtenir la liste des fichiers
    files = get_camera_files()
    
    if not files:
        logger.info("Aucun fichier à supprimer sur l'appareil photo")
        return True
    
    # Supprimer chaque fichier individuellement
    logger.info(f"Suppression de {len(files)} fichiers...")
    success_count = 0
    
    for file_num, file_path in files:
        if delete_file(file_num):
            success_count += 1
            # Petite pause pour éviter les problèmes
            time.sleep(0.5)
    
    logger.info(f"{success_count}/{len(files)} fichiers supprimés avec succès")
    
    # Vérifier si tous les fichiers ont été supprimés
    if success_count == len(files):
        return True
    else:
        return False

def signal_handler(signum, frame):
    """Gestionnaire de signal pour arrêt propre"""
    logger.info("Arrêt demandé, nettoyage en cours...")
    sys.exit(0)

if __name__ == "__main__":
    # Gestionnaire de signaux pour arrêt propre
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # S'assurer que le répertoire de logs existe
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    logger.info("Début du processus de suppression des photos de l'appareil")
    
    # Supprimer tous les fichiers
    if delete_all_files_individually():
        logger.info("Tous les fichiers ont été supprimés avec succès")
    else:
        logger.warning("La suppression de certains fichiers a échoué")
