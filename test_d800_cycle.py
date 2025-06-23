#!/usr/bin/env python3
"""
Script de test pour simuler le cycle complet avec le Nikon D800
Ce script exécute manuellement toutes les étapes du processus:
1. Vérification de la connexion de l'appareil
2. Téléchargement des photos dans /tmp/photos
3. Ajout des extensions JPG aux fichiers qui n'en ont pas
4. Suppression des fichiers de la carte SD
"""

import os
import sys
import subprocess
import time
import logging
import json

# Ajouter le chemin du projet pour importer les modules
PROJECT_PATH = "/home/server01/projet_ftp/Projet_FTP"
sys.path.append(PROJECT_PATH)

# Import des modules nécessaires
from d800_auto_download import (
    load_config, 
    kill_gvfs_processes, 
    check_camera_connection, 
    download_new_photos,
    add_jpg_extension_to_files
)

# Configuration du logging
LOG_FILE = os.path.join(PROJECT_PATH, "logs/d800_test.log")

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('D800Test')

def print_separator():
    """Affiche un séparateur dans les logs pour plus de lisibilité"""
    logger.info("=" * 60)

def test_camera_connection():
    """Test de la connexion à l'appareil photo"""
    print_separator()
    logger.info("ÉTAPE 1: Vérification de la connexion à l'appareil photo")
    
    # Tuer les processus qui peuvent interférer
    kill_gvfs_processes()
    time.sleep(2)
    
    # Vérifier la connexion
    if check_camera_connection():
        logger.info("✅ Appareil photo Nikon détecté")
        return True
    else:
        logger.error("❌ Appareil photo non détecté")
        return False

def test_download_photos(download_path):
    """Test du téléchargement des photos"""
    print_separator()
    logger.info(f"ÉTAPE 2: Téléchargement des photos vers {download_path}")
    
    # Téléchargement
    downloaded = download_new_photos(download_path)
    
    if downloaded > 0:
        logger.info(f"✅ {downloaded} photo(s) téléchargée(s) avec succès")
        return True
    elif downloaded == 0:
        logger.info("ℹ️ Aucune nouvelle photo à télécharger")
        return False
    else:
        logger.error("❌ Erreur lors du téléchargement")
        return False

def test_add_extension(download_path):
    """Test de l'ajout d'extensions JPG aux fichiers"""
    print_separator()
    logger.info(f"ÉTAPE 3: Ajout des extensions JPG aux fichiers")
    
    # Compter les fichiers sans extension
    files_without_ext = []
    for filename in os.listdir(download_path):
        file_path = os.path.join(download_path, filename)
        if os.path.isfile(file_path):
            name, ext = os.path.splitext(filename)
            if ext == '' and not filename.startswith('.'):
                files_without_ext.append(filename)
    
    # S'il y a des fichiers sans extension
    if files_without_ext:
        logger.info(f"Trouvé {len(files_without_ext)} fichier(s) sans extension")
        add_jpg_extension_to_files(download_path)
        logger.info("✅ Extensions ajoutées")
        return True
    else:
        logger.info("ℹ️ Tous les fichiers ont déjà une extension")
        return False

def test_delete_photos():
    """Test de la suppression des photos"""
    print_separator()
    logger.info("ÉTAPE 4: Suppression des photos de l'appareil photo")
    
    # Appeler le script de suppression spécifique
    cmd = ['python3', os.path.join(PROJECT_PATH, 'd800_delete.py')]
    
    try:
        logger.info("Exécution du script de suppression...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        # Afficher la sortie du script
        for line in result.stdout.split('\n'):
            if line.strip():
                logger.info(f"  {line}")
        
        if result.stderr:
            for line in result.stderr.split('\n'):
                if line.strip():
                    logger.warning(f"  {line}")
        
        if result.returncode == 0:
            logger.info("✅ Script de suppression exécuté avec succès")
            return True
        else:
            logger.error(f"❌ Échec du script de suppression (code {result.returncode})")
            return False
            
    except Exception as e:
        logger.error(f"❌ Exception lors de la suppression: {e}")
        return False

def count_files_in_directory(path):
    """Compte les fichiers JPG dans un répertoire"""
    try:
        if not os.path.exists(path):
            return 0
            
        jpg_count = 0
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            if os.path.isfile(file_path):
                name, ext = os.path.splitext(filename)
                if ext.lower() in ['.jpg', '.jpeg']:
                    jpg_count += 1
        return jpg_count
    except Exception as e:
        logger.error(f"Erreur lors du comptage des fichiers: {e}")
        return -1

def main():
    """Fonction principale"""
    print_separator()
    logger.info("DÉBUT DU TEST DU CYCLE COMPLET AVEC LE NIKON D800")
    print_separator()
    
    # Charger la configuration
    config = load_config()
    download_path = config.get('camera', {}).get('download_path', '/tmp/photos')
    
    # S'assurer que le répertoire existe
    os.makedirs(download_path, exist_ok=True)
    
    # Étape 1: Vérifier la connexion
    if not test_camera_connection():
        logger.error("Test arrêté: Appareil photo non détecté")
        return False
    
    # Compter les fichiers JPG initiaux
    initial_count = count_files_in_directory(download_path)
    logger.info(f"Nombre initial de fichiers JPG dans {download_path}: {initial_count}")
    
    # Étape 2: Télécharger les photos
    download_success = test_download_photos(download_path)
    
    # Compter les fichiers JPG après téléchargement
    if download_success:
        new_count = count_files_in_directory(download_path)
        logger.info(f"Nombre de fichiers JPG après téléchargement: {new_count}")
        logger.info(f"Nombre de nouvelles photos: {max(0, new_count - initial_count)}")
    
    # Étape 3: Ajouter les extensions
    test_add_extension(download_path)
    
    # Étape 4: Supprimer les photos de l'appareil
    delete_success = test_delete_photos()
    
    # Résumé
    print_separator()
    logger.info("RÉSUMÉ DU TEST:")
    logger.info(f"Téléchargement: {'✅ Réussi' if download_success else '❌ Échoué'}")
    logger.info(f"Suppression: {'✅ Réussi' if delete_success else '❌ Échoué'}")
    print_separator()
    
    return download_success and delete_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
