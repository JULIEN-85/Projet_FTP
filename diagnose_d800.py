#!/usr/bin/env python3
"""
Script de diagnostic complet pour le Nikon D800
Ce script permet de tester toutes les étapes du processus :
- Détection de l'appareil photo
- Téléchargement des photos
- Suppression des photos
Le but est de trouver et de résoudre les problèmes avec la suppression des photos.
"""

import os
import sys
import subprocess
import time
import logging
import re
import json

# Configuration du logging
LOG_FILE = "/home/server01/projet_ftp/Projet_FTP/logs/d800_diagnostic.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('D800Diagnostic')

# Assurer que le répertoire de logs existe
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def load_config():
    """Charger la configuration depuis config.json"""
    try:
        CONFIG_FILE = "/home/server01/projet_ftp/Projet_FTP/config.json"
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erreur de chargement de la configuration: {e}")
        return {
            "camera": {
                "download_path": "/tmp/photos",
                "delete_from_camera": True
            }
        }

def run_cmd_with_log(cmd, timeout=30, description="Commande"):
    """Exécuter une commande et journaliser le résultat"""
    logger.info(f"Exécution de: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        
        if result.stdout.strip():
            logger.info(f"{description} - Sortie standard:")
            for line in result.stdout.strip().split('\n'):
                logger.info(f"  {line}")
                
        if result.stderr.strip():
            logger.warning(f"{description} - Erreur standard:")
            for line in result.stderr.strip().split('\n'):
                logger.warning(f"  {line}")
                
        logger.info(f"{description} - Code de retour: {result.returncode}")
        
        return result
    except subprocess.TimeoutExpired:
        logger.error(f"{description} - TIMEOUT après {timeout} secondes")
        return None
    except Exception as e:
        logger.error(f"{description} - Exception: {e}")
        return None

def kill_gvfs_processes():
    """Arrêter les processus gvfs qui peuvent bloquer l'accès à l'appareil photo"""
    processes_to_kill = [
        "gvfs-gphoto2-volume-monitor",
        "gvfs-udisks2-volume-monitor",
        "gvfs-mtp-volume-monitor"
    ]
    
    for process in processes_to_kill:
        try:
            subprocess.run(['pkill', '-f', process], capture_output=True, text=True)
            logger.info(f"Tentative d'arrêt du processus {process}")
        except Exception as e:
            logger.debug(f"Impossible d'arrêter {process}: {e}")

def check_usb_devices():
    """Vérifier les périphériques USB connectés"""
    logger.info("--- Vérification des périphériques USB ---")
    run_cmd_with_log(['lsusb'], description="Liste USB")

def check_camera_detection():
    """Vérifier la détection de l'appareil photo"""
    logger.info("--- Détection de l'appareil photo ---")
    result = run_cmd_with_log(['gphoto2', '--auto-detect'], description="Détection")
    
    if result and result.returncode == 0 and 'Nikon' in result.stdout:
        logger.info("✅ Appareil photo Nikon détecté avec succès")
        return True
    else:
        logger.error("❌ Appareil photo Nikon NON détecté")
        return False

def check_camera_abilities():
    """Vérifier les capacités de l'appareil photo"""
    logger.info("--- Capacités de l'appareil photo ---")
    run_cmd_with_log(['gphoto2', '--abilities'], description="Capacités")

def list_camera_folders():
    """Lister les dossiers sur l'appareil photo"""
    logger.info("--- Structure des dossiers ---")
    run_cmd_with_log(['gphoto2', '--list-folders'], description="Dossiers")

def list_camera_files():
    """Lister les fichiers sur l'appareil photo"""
    logger.info("--- Fichiers sur l'appareil photo ---")
    result = run_cmd_with_log(['gphoto2', '--list-files'], description="Fichiers")
    
    # Compter les fichiers
    if result and result.returncode == 0:
        file_count = 0
        for line in result.stdout.split('\n'):
            if line.startswith('#'):
                file_count += 1
        
        logger.info(f"Nombre de fichiers sur l'appareil: {file_count}")
        return file_count
    
    return 0

def download_single_photo(download_path, filename=None):
    """Télécharger une seule photo pour test"""
    logger.info("--- Test de téléchargement d'un fichier ---")
    
    # Créer le dossier de téléchargement s'il n'existe pas
    os.makedirs(download_path, exist_ok=True)
    
    # Lister les fichiers d'abord
    result = run_cmd_with_log(['gphoto2', '--list-files'], description="Liste des fichiers")
    
    if not result or result.returncode != 0:
        logger.error("❌ Impossible de lister les fichiers")
        return False
    
    # Trouver le premier fichier
    file_num = None
    file_name = None
    
    for line in result.stdout.split('\n'):
        if line.startswith('#'):
            try:
                parts = line.split(' ', 1)
                if len(parts) > 1:
                    file_num = parts[0][1:]  # Supprimer le # au début
                    file_name = parts[1].strip()
                    break
            except:
                pass
    
    if not file_num:
        logger.warning("Aucun fichier trouvé sur l'appareil photo")
        return False
    
    # Télécharger ce fichier
    logger.info(f"Téléchargement du fichier #{file_num}: {file_name}")
    
    # Aller dans le dossier de destination
    original_dir = os.getcwd()
    os.chdir(download_path)
    
    download_result = run_cmd_with_log(['gphoto2', f'--get-file={file_num}'], 
                                      timeout=60, 
                                      description=f"Téléchargement du fichier #{file_num}")
    
    # Restaurer le répertoire original
    os.chdir(original_dir)
    
    if download_result and download_result.returncode == 0:
        logger.info("✅ Fichier téléchargé avec succès")
        return True
    else:
        logger.error("❌ Échec du téléchargement")
        return False

def delete_single_photo(file_num=None):
    """Supprimer une seule photo pour test"""
    logger.info("--- Test de suppression d'un fichier ---")
    
    if file_num is None:
        # Lister les fichiers d'abord pour en trouver un
        result = run_cmd_with_log(['gphoto2', '--list-files'], description="Liste pour suppression")
        
        if not result or result.returncode != 0:
            logger.error("❌ Impossible de lister les fichiers")
            return False
        
        # Trouver le premier fichier
        for line in result.stdout.split('\n'):
            if line.startswith('#'):
                try:
                    parts = line.split(' ', 1)
                    if len(parts) > 1:
                        file_num = parts[0][1:]  # Supprimer le # au début
                        file_name = parts[1].strip()
                        break
                except:
                    pass
    
    if not file_num:
        logger.warning("Aucun fichier trouvé à supprimer")
        return False
    
    # Supprimer ce fichier
    logger.info(f"Suppression du fichier #{file_num}")
    
    delete_result = run_cmd_with_log(['gphoto2', f'--delete-file={file_num}'], 
                                    description=f"Suppression du fichier #{file_num}")
    
    if delete_result and delete_result.returncode == 0:
        logger.info("✅ Fichier supprimé avec succès")
        return True
    else:
        logger.error("❌ Échec de la suppression")
        return False

def try_delete_all():
    """Essayer la commande delete-all-files pour voir le message d'erreur exact"""
    logger.info("--- Test de delete-all-files ---")
    run_cmd_with_log(['gphoto2', '--delete-all-files'], description="Tentative de suppression globale")

def test_individual_deletions():
    """Tester la suppression de plusieurs fichiers un par un"""
    logger.info("--- Test de suppressions individuelles ---")
    
    # Lister les fichiers d'abord
    result = run_cmd_with_log(['gphoto2', '--list-files'], description="Liste pour suppressions multiples")
    
    if not result or result.returncode != 0:
        logger.error("❌ Impossible de lister les fichiers")
        return False
    
    # Collecter tous les numéros de fichiers
    file_nums = []
    for line in result.stdout.split('\n'):
        if line.startswith('#'):
            try:
                parts = line.split(' ', 1)
                if len(parts) > 1:
                    file_num = parts[0][1:]  # Supprimer le # au début
                    file_nums.append(file_num)
            except:
                pass
    
    if not file_nums:
        logger.warning("Aucun fichier trouvé à supprimer")
        return False
    
    logger.info(f"Tentative de suppression de {len(file_nums)} fichiers, un par un")
    
    success_count = 0
    for idx, file_num in enumerate(file_nums[:5]):  # Limiter à 5 fichiers pour le test
        logger.info(f"Suppression du fichier #{file_num} ({idx+1}/{min(5, len(file_nums))})")
        
        delete_result = run_cmd_with_log(['gphoto2', f'--delete-file={file_num}'], 
                                       description=f"Suppression du fichier #{file_num}")
        
        if delete_result and delete_result.returncode == 0:
            success_count += 1
        
        # Petite pause entre les suppressions
        time.sleep(1)
    
    logger.info(f"Résultat: {success_count}/{min(5, len(file_nums))} fichiers supprimés avec succès")
    return success_count > 0

def test_full_process():
    """Tester le processus complet : télécharger puis supprimer"""
    config = load_config()
    download_path = config.get('camera', {}).get('download_path', '/tmp/photos')
    
    logger.info("=== TEST DU PROCESSUS COMPLET ===")
    logger.info(f"1. Téléchargement vers {download_path}")
    logger.info("2. Suppression des fichiers de la carte SD")
    
    # Assurer que rien ne bloque l'accès USB
    kill_gvfs_processes()
    time.sleep(2)
    
    # Détection de l'appareil
    if not check_camera_detection():
        logger.error("Impossible de continuer sans appareil photo")
        return False
    
    # Lister les fichiers
    file_count = list_camera_files()
    if file_count == 0:
        logger.warning("Aucun fichier à traiter")
        return False
    
    # Télécharger une photo
    if not download_single_photo(download_path):
        logger.error("Échec du téléchargement, test arrêté")
        return False
    
    # Supprimer cette photo
    if not delete_single_photo():
        logger.error("Échec de la suppression")
        return False
    
    logger.info("✅ Le processus complet a réussi!")
    return True

def test_d800_delete_script():
    """Tester le script d800_delete.py"""
    logger.info("=== TEST DU SCRIPT D800_DELETE ===")
    
    # Assurer que rien ne bloque l'accès USB
    kill_gvfs_processes()
    time.sleep(2)
    
    run_cmd_with_log(['python3', '/home/server01/projet_ftp/Projet_FTP/d800_delete.py'], 
                   timeout=60,
                   description="Script de suppression")

def check_ftp_transfer():
    """Vérifie le traitement des extensions de fichiers pendant le transfert FTP"""
    logger.info("--- Vérification du transfert FTP ---")
    
    # Créer un fichier test
    test_dir = "/tmp/ftp_test"
    os.makedirs(test_dir, exist_ok=True)
    
    # Créer deux fichiers test: un avec extension .JPG, un sans extension
    test_file_with_ext = os.path.join(test_dir, "test_with_extension.JPG")
    test_file_no_ext = os.path.join(test_dir, "test_no_extension")
    
    # Créer des fichiers tests
    with open(test_file_with_ext, "w") as f:
        f.write("Test file with extension")
    with open(test_file_no_ext, "w") as f:
        f.write("Test file without extension")
    
    logger.info("Fichiers tests créés:")
    logger.info(f"  - {test_file_with_ext}")
    logger.info(f"  - {test_file_no_ext}")
    
    # Tester le script de transfert FTP
    logger.info("Test du script lftp_send_jpg.sh avec fichier avec extension")
    lftp_script = "/home/server01/projet_ftp/Projet_FTP/lftp_send_jpg.sh"
    
    # 1. Test avec fichier avec extension
    ext_result = run_cmd_with_log([lftp_script, test_file_with_ext], 
                              timeout=30, 
                              description="Transfert FTP avec extension")
    
    # 2. Test avec fichier sans extension
    no_ext_result = run_cmd_with_log([lftp_script, test_file_no_ext], 
                                 timeout=30, 
                                 description="Transfert FTP sans extension")
    
    # Analyser le script lftp_send_jpg.sh
    logger.info("Analyse du script de transfert FTP")
    with open(lftp_script, "r") as f:
        content = f.read()
        
    if "put \"$FILE\" -o \"$FILENAME\"" in content:
        logger.warning("⚠️ Le script utilise 'put \"$FILE\" -o \"$FILENAME\"' qui peut ne pas préserver l'extension")
        logger.warning("Correction suggérée: Utiliser basename pour extraire le nom de fichier correctement")
    
    return True

def main():
    """Fonction principale de diagnostic"""
    logger.info("\n" + "="*60)
    logger.info("DÉBUT DU DIAGNOSTIC NIKON D800")
    logger.info("="*60)
    
    # 1. Vérifier l'environnement
    check_usb_devices()
    
    # 2. Arrêter les services qui peuvent interférer
    kill_gvfs_processes()
    time.sleep(2)
    
    # 3. Vérifier la détection de l'appareil
    if not check_camera_detection():
        logger.error("DIAGNOSTIC ARRÊTÉ: Appareil photo non détecté!")
        return
    
    # 4. Vérifier les capacités
    check_camera_abilities()
    
    # 5. Explorer la structure
    list_camera_folders()
    list_camera_files()
    
    # 6. Tester les commandes de suppression
    try_delete_all()
    test_individual_deletions()
    
    # 7. Tester le processus complet
    test_full_process()
    
    # 8. Tester le nouveau script de suppression
    test_d800_delete_script()
    
    # 9. Vérifier le transfert FTP (extension de fichier)
    check_ftp_transfer()
    
    # 9. Vérifier le transfert FTP
    check_ftp_transfer()
    
    logger.info("\n" + "="*60)
    logger.info("FIN DU DIAGNOSTIC")
    logger.info("="*60)

if __name__ == "__main__":
    main()
