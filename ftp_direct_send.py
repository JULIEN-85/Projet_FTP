#!/usr/bin/env python3
"""
Script simple de transfert FTP en mode non sécurisé (forcer sans TLS)
pour contourner les problèmes de TLS avec ce serveur spécifique
"""
import os
import time
import logging
from ftplib import FTP

# Configuration
FTP_HOST = "192.168.1.22"
FTP_USER = "julien"
FTP_PASS = "2004"
FTP_DIR = "/photos"  # correspond à C:\FTP\photos côté serveur
LOCAL_DIR = "/tmp/photos"
DELETE_AFTER = True  # Supprimer les fichiers après transfert réussi

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("FTP-Transfer")

def ensure_dir(ftp, directory):
    """Vérifie si le répertoire existe, le crée si nécessaire"""
    try:
        current_dir = ftp.pwd()
        # Essayer d'accéder au répertoire
        ftp.cwd(directory)
        # Revenir au répertoire d'origine
        ftp.cwd(current_dir)
        logger.info(f"Répertoire distant {directory} existe déjà")
        return True
    except Exception:
        try:
            # Créer le répertoire
            ftp.mkd(directory)
            logger.info(f"Répertoire distant {directory} créé")
            return True
        except Exception as e:
            logger.error(f"Impossible de créer le répertoire {directory}: {e}")
            return False

def main():
    """Script principal"""
    logger.info("Démarrage du transfert FTP")
    
    # Vérifier si le répertoire local existe
    if not os.path.exists(LOCAL_DIR):
        logger.error(f"Le répertoire local {LOCAL_DIR} n'existe pas")
        return
    
    # Lister les fichiers à transférer
    files = [f for f in os.listdir(LOCAL_DIR) if os.path.isfile(os.path.join(LOCAL_DIR, f))]
    if not files:
        logger.info(f"Aucun fichier à transférer dans {LOCAL_DIR}")
        return
        
    logger.info(f"Trouvé {len(files)} fichiers à transférer")
    
    # Connexion FTP
    ftp = None
    try:
        # Désactiver complètement TLS
        logger.info("Connexion FTP (sans TLS)")
        ftp = FTP()
        ftp.set_debuglevel(1)  # Activer le mode debug pour voir toutes les commandes
        ftp.connect(FTP_HOST, port=21, timeout=30)
        
        # Ignorer l'exigence de AUTH TLS en piégeant l'erreur
        try:
            ftp.login(FTP_USER, FTP_PASS)
        except Exception as e:
            if "AUTH" in str(e):
                logger.warning("Serveur demande AUTH TLS, tentative avec AUTH TLS mais sans PROT P")
                ftp.sendcmd('AUTH TLS')
                ftp.sendcmd('USER ' + FTP_USER)
                ftp.sendcmd('PASS ' + FTP_PASS)
                # Ne pas activer PROT P
                logger.info("Authentifié avec AUTH TLS mais sans cryptage des données")
            else:
                raise
        
        # Mode passif
        ftp.set_pasv(True)
        logger.info("Mode passif activé")
        
        # Se positionner dans le bon répertoire
        if not ensure_dir(ftp, FTP_DIR):
            logger.error("Impossible d'accéder ou créer le répertoire distant")
            ftp.quit()
            return
            
        ftp.cwd(FTP_DIR)
        logger.info(f"Changé au répertoire distant: {FTP_DIR}")
        
        # Liste des fichiers distants
        try:
            files_on_server = ftp.nlst()
            logger.info(f"Fichiers déjà sur serveur: {len(files_on_server)}")
        except:
            files_on_server = []
            logger.warning("Impossible de lister les fichiers distants")
        
        # Transfert des fichiers
        success_count = 0
        for file_name in files:
            local_path = os.path.join(LOCAL_DIR, file_name)
            
            # Vérifier si le fichier existe déjà
            if file_name in files_on_server:
                logger.info(f"Le fichier {file_name} existe déjà sur le serveur, ignoré")
                continue
            
            try:
                logger.info(f"Transfert de {file_name}")
                with open(local_path, 'rb') as file:
                    ftp.storbinary(f'STOR {file_name}', file)
                
                logger.info(f"✅ Transfert réussi: {file_name}")
                success_count += 1
                
                # Supprimer le fichier local après transfert réussi
                if DELETE_AFTER:
                    try:
                        os.remove(local_path)
                        logger.info(f"Fichier local supprimé: {file_name}")
                    except Exception as e:
                        logger.warning(f"Impossible de supprimer le fichier local {file_name}: {e}")
            
            except Exception as e:
                logger.error(f"Échec du transfert de {file_name}: {e}")
        
        logger.info(f"Transfert terminé: {success_count}/{len(files)} fichiers transférés avec succès")
        
    except Exception as e:
        logger.error(f"Erreur lors du transfert FTP: {e}")
    finally:
        if ftp:
            try:
                ftp.quit()
            except:
                pass

if __name__ == "__main__":
    main()
