#!/usr/bin/env python3
"""
Script pour vérifier et corriger les photos corrompues dans /tmp/photos
Détecte les fichiers vides, sans extension ou avec des en-têtes/pieds JPEG invalides
"""

import os
import sys
import shutil
import logging
from pathlib import Path
import argparse
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger('FixCorruptPhotos')

class PhotoFixer:
    """Classe pour vérifier et réparer les photos"""
    
    def __init__(self, photos_dir, backup_dir=None):
        """Initialisation avec le répertoire des photos"""
        self.photos_dir = photos_dir
        
        # Créer le répertoire de backup si nécessaire
        if backup_dir:
            self.backup_dir = backup_dir
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.backup_dir = f"/tmp/corrupt_photos_backup_{timestamp}"
        
        os.makedirs(self.photos_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def check_and_fix_files(self, delete_corrupt=False, add_extension=True):
        """Vérifie et répare les fichiers"""
        logger.info(f"Vérification des photos dans {self.photos_dir}")
        
        stats = {
            'total': 0,
            'valid': 0,
            'empty': 0,
            'corrupt_header': 0,
            'corrupt_footer': 0,
            'fixed_extension': 0,
            'backed_up': 0,
            'deleted': 0
        }
        
        # Parcourir tous les fichiers
        files = list(Path(self.photos_dir).glob('*'))
        stats['total'] = len(files)
        
        for file_path in files:
            if not file_path.is_file():
                continue
                
            filename = file_path.name
            file_size = os.path.getsize(file_path)
            
            # Vérifier les fichiers vides
            if file_size == 0:
                logger.warning(f"Fichier vide trouvé: {filename}")
                stats['empty'] += 1
                
                if delete_corrupt:
                    os.unlink(file_path)
                    stats['deleted'] += 1
                    logger.info(f"Supprimé fichier vide: {filename}")
                else:
                    # Backup
                    shutil.move(file_path, os.path.join(self.backup_dir, filename))
                    stats['backed_up'] += 1
                    logger.info(f"Déplacé fichier vide vers backup: {filename}")
                
                continue
            
            # Vérifier si c'est un fichier JPEG sans extension
            is_jpg = False
            
            try:
                with open(file_path, 'rb') as f:
                    header = f.read(3)
                    is_jpg = header == b'\xff\xd8\xff'
                    
                    # Vérifier le footer pour les fichiers JPEG
                    if is_jpg:
                        # Lire le pied de fichier JPEG (les 2 derniers octets)
                        f.seek(-2, os.SEEK_END)
                        footer = f.read(2)
                        
                        if footer != b'\xff\xd9':
                            logger.warning(f"Fichier JPEG avec pied invalide: {filename}")
                            stats['corrupt_footer'] += 1
                            
                            if delete_corrupt:
                                os.unlink(file_path)
                                stats['deleted'] += 1
                                logger.info(f"Supprimé fichier corrompu: {filename}")
                            else:
                                shutil.move(file_path, os.path.join(self.backup_dir, filename))
                                stats['backed_up'] += 1
                                logger.info(f"Déplacé fichier corrompu vers backup: {filename}")
                            
                            continue
                        
                        # C'est un JPEG valide
                        stats['valid'] += 1
                        
                        # Ajouter l'extension .jpg si demandé et si elle manque
                        if add_extension and not any(file_path.name.lower().endswith(ext) 
                                                    for ext in ['.jpg', '.jpeg']):
                            # Renommer avec extension .jpg
                            new_path = str(file_path) + '.jpg'
                            os.rename(file_path, new_path)
                            stats['fixed_extension'] += 1
                            logger.info(f"Renommé avec extension .jpg: {filename} → {filename}.jpg")
                    else:
                        # Ce n'est pas un JPEG ou l'en-tête est invalide
                        logger.warning(f"Fichier avec en-tête invalide: {filename}")
                        stats['corrupt_header'] += 1
                        
                        if delete_corrupt:
                            os.unlink(file_path)
                            stats['deleted'] += 1
                            logger.info(f"Supprimé fichier non-JPEG: {filename}")
                        else:
                            shutil.move(file_path, os.path.join(self.backup_dir, filename))
                            stats['backed_up'] += 1
                            logger.info(f"Déplacé fichier non-JPEG vers backup: {filename}")
                            
            except Exception as e:
                logger.error(f"Erreur lors de l'analyse de {filename}: {e}")
                
                # Backup en cas d'erreur
                try:
                    shutil.move(file_path, os.path.join(self.backup_dir, filename))
                    stats['backed_up'] += 1
                    logger.info(f"Déplacé fichier problématique vers backup: {filename}")
                except Exception as e2:
                    logger.error(f"Impossible de déplacer {filename}: {e2}")
        
        # Résumé
        logger.info(f"Vérification terminée")
        logger.info(f"Total: {stats['total']} fichiers")
        logger.info(f"Valides: {stats['valid']} fichiers")
        logger.info(f"Vides: {stats['empty']} fichiers")
        logger.info(f"En-têtes corrompus: {stats['corrupt_header']} fichiers")
        logger.info(f"Pieds corrompus: {stats['corrupt_footer']} fichiers")
        logger.info(f"Extensions ajoutées: {stats['fixed_extension']} fichiers")
        logger.info(f"Fichiers sauvegardés: {stats['backed_up']} fichiers")
        logger.info(f"Fichiers supprimés: {stats['deleted']} fichiers")
        
        return stats

def main():
    # Parser les arguments
    parser = argparse.ArgumentParser(description="Vérifie et corrige les photos corrompues")
    parser.add_argument('--dir', default='/tmp/photos', 
                        help="Répertoire contenant les photos à vérifier")
    parser.add_argument('--backup-dir', 
                        help="Répertoire où déplacer les fichiers corrompus")
    parser.add_argument('--delete', action='store_true',
                        help="Supprimer les fichiers corrompus au lieu de les sauvegarder")
    parser.add_argument('--no-extension', action='store_true',
                        help="Ne pas ajouter l'extension .jpg aux fichiers JPEG sans extension")
    args = parser.parse_args()
    
    # Exécuter la vérification
    fixer = PhotoFixer(args.dir, args.backup_dir)
    fixer.check_and_fix_files(
        delete_corrupt=args.delete,
        add_extension=not args.no_extension
    )

if __name__ == "__main__":
    main()
