#!/usr/bin/env python3
"""
Script de transfert FTPS robuste : détecte les fichiers dans /tmp/photos 
et les envoie sur le serveur FTPS dans C:\FTP\photos en gérant les problèmes TLS
"""
import os
import ssl
import time
import logging
from ftplib import FTP_TLS

# Configuration
FTP_HOST = "192.168.1.22"
FTP_USER = "julien"
FTP_PASS = "2004"
FTP_DIR = "/photos"  # correspond à C:\FTP\photos côté serveur
LOCAL_DIR = "/tmp/photos"

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("FTPS-Transfer")

class CustomFTP_TLS(FTP_TLS):
    """Classe FTP_TLS personnalisée avec gestion améliorée des sessions TLS"""
    
    def ntransfercmd(self, cmd, rest=None):
        """Surcharge pour améliorer la compatibilité TLS"""
        conn, size = super().ntransfercmd(cmd, rest)
        
        # Désactiver la vérification du certificat sur le canal de données
        # C'est un contournement pour le problème "TLS session not resumed"
        if self._prot_p:
            conn.context = ssl.create_default_context()
            conn.context.check_hostname = False
            conn.context.verify_mode = ssl.CERT_NONE
            conn = conn.context.wrap_socket(conn, server_hostname=self.host)
            
        return conn, size

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

def upload_file(ftp, local_path, file_name):
    """Upload un fichier avec plusieurs tentatives"""
    for attempt in range(3):  # 3 tentatives
        try:
            logger.info(f"Transfert de {file_name} (tentative {attempt+1})")
            
            # Essayer avec différentes tailles de buffer
            buffer_size = 8192 if attempt == 0 else (4096 if attempt == 1 else 1024)
            
            with open(local_path, 'rb') as file:
                ftp.storbinary(f'STOR {file_name}', file, blocksize=buffer_size)
            
            logger.info(f"✅ Transfert réussi: {file_name}")
            return True
        
        except Exception as e:
            logger.warning(f"Échec du transfert (tentative {attempt+1}): {e}")
            time.sleep(1)  # Attendre avant de réessayer
            try:
                # Réinitialiser la connexion
                ftp.voidcmd('NOOP')
            except:
                # Reconnexion complète si nécessaire
                return False
    
    return False

def main():
    """Script principal"""
    logger.info("Démarrage du transfert FTPS robuste")
    
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
    
    # Connexion FTPS
    ftp = None
    try:
        # Créer le contexte SSL pour la connexion principale
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        # Connexion avec notre classe personnalisée
        ftp = CustomFTP_TLS(context=context)
        ftp.connect(FTP_HOST, 21, timeout=30)
        ftp.login(FTP_USER, FTP_PASS)
        
        # Activer les protections TLS
        ftp.prot_p()
        
        # Se positionner dans le bon répertoire
        if not ensure_dir(ftp, FTP_DIR):
            logger.error("Impossible d'accéder ou créer le répertoire distant")
            ftp.quit()
            return
            
        ftp.cwd(FTP_DIR)
        
        # Transfert des fichiers
        success_count = 0
        for file_name in files:
            local_path = os.path.join(LOCAL_DIR, file_name)
            
            if upload_file(ftp, local_path, file_name):
                success_count += 1
                
                # Supprimer le fichier local après transfert réussi ?
                try:
                    os.remove(local_path)
                    logger.info(f"Fichier local supprimé: {file_name}")
                except Exception as e:
                    logger.warning(f"Impossible de supprimer le fichier local {file_name}: {e}")
        
        logger.info(f"Transfert terminé: {success_count}/{len(files)} fichiers transférés avec succès")
        
    except Exception as e:
        logger.error(f"Erreur lors du transfert FTPS: {e}")
    finally:
        if ftp:
            try:
                ftp.quit()
            except:
                pass

if __name__ == "__main__":
    main()
