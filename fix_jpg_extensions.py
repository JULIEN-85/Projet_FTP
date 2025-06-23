#!/usr/bin/env python3
"""
Script pour corriger les extensions des fichiers JPG dans le dossier de téléchargement
Certains fichiers téléchargés par gphoto2 peuvent ne pas avoir d'extension
Ce script les identifie et ajoute l'extension .JPG appropriée
"""

import os
import sys
import logging
import json
import argparse

# Configuration
CONFIG_FILE = "/home/server01/projet_ftp/Projet_FTP/config.json"
LOG_FILE = "/home/server01/projet_ftp/Projet_FTP/logs/fix_extensions.log"

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('FixExtensions')

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
            }
        }

def is_jpeg_file(file_path):
    """Vérifie si un fichier est au format JPEG en analysant son contenu"""
    try:
        with open(file_path, 'rb') as f:
            # Les JPEG commencent par les octets FF D8 FF
            header = f.read(3)
            return header == b'\xff\xd8\xff'
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse du fichier {file_path}: {e}")
        return False

def fix_extensions(directory, dry_run=False, force=False):
    """Corrige les extensions des fichiers JPG dans le répertoire spécifié"""
    logger.info(f"Analyse du répertoire: {directory}")
    logger.info(f"Mode simulation: {'Oui' if dry_run else 'Non'}")
    
    # S'assurer que le répertoire existe
    if not os.path.exists(directory):
        logger.error(f"Le répertoire {directory} n'existe pas!")
        return 0
    
    fixed_count = 0
    total_files = 0
    
    # Parcourir tous les fichiers du répertoire
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if not os.path.isfile(file_path) or filename.startswith('.'):
            continue
            
        total_files += 1
        name, ext = os.path.splitext(filename)
        
        # Cas 1: Fichier sans extension
        if ext == '':
            if is_jpeg_file(file_path) or force:
                new_path = file_path + '.JPG'
                if dry_run:
                    logger.info(f"[SIMULATION] Ajout de l'extension JPG: {filename} -> {os.path.basename(new_path)}")
                    fixed_count += 1
                else:
                    try:
                        os.rename(file_path, new_path)
                        logger.info(f"Extension JPG ajoutée: {filename} -> {os.path.basename(new_path)}")
                        fixed_count += 1
                    except Exception as e:
                        logger.error(f"Impossible d'ajouter l'extension à {filename}: {e}")
            else:
                logger.warning(f"Fichier sans extension ignoré (n'est pas un JPEG): {filename}")
                
        # Cas 2: Extension en minuscule à normaliser
        elif ext.lower() in ['.jpg', '.jpeg'] and ext != '.JPG':
            new_path = os.path.join(directory, name + '.JPG')
            if dry_run:
                logger.info(f"[SIMULATION] Normalisation de l'extension: {filename} -> {os.path.basename(new_path)}")
                fixed_count += 1
            else:
                try:
                    os.rename(file_path, new_path)
                    logger.info(f"Extension normalisée: {filename} -> {os.path.basename(new_path)}")
                    fixed_count += 1
                except Exception as e:
                    logger.error(f"Impossible de normaliser l'extension de {filename}: {e}")
    
    logger.info(f"Total de fichiers analysés: {total_files}")
    logger.info(f"Fichiers corrigés: {fixed_count}")
    
    return fixed_count

def main():
    """Fonction principale"""
    # Analyser les arguments de la ligne de commande
    parser = argparse.ArgumentParser(description='Corriger les extensions des fichiers JPG')
    parser.add_argument('-d', '--directory', help='Répertoire à traiter (par défaut, utilise le répertoire de config)')
    parser.add_argument('--dry-run', action='store_true', help='Simuler sans effectuer de modifications')
    parser.add_argument('-f', '--force', action='store_true', help='Forcer l\'ajout de .JPG à tous les fichiers sans extension')
    args = parser.parse_args()
    
    # S'assurer que le répertoire de logs existe
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    # Charger la configuration
    config = load_config()
    
    # Déterminer le répertoire à traiter
    directory = args.directory
    if not directory:
        directory = config.get('camera', {}).get('download_path', '/tmp/photos')
    
    logger.info("Début de la correction des extensions de fichiers")
    fixed = fix_extensions(directory, dry_run=args.dry_run, force=args.force)
    logger.info(f"Fin du traitement. {fixed} fichier(s) corrigé(s).")

if __name__ == "__main__":
    main()
