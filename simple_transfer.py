#!/usr/bin/env python3
"""
Module de transfert simplifié pour FTP et SFTP
Version légère et facile à maintenir
"""

import os
import ftplib
import logging
import re
import socket
from typing import Optional, Dict, Any

# Import SFTP avec gestion d'erreur
try:
    import paramiko
    SFTP_SUPPORT = True
except ImportError:
    SFTP_SUPPORT = False
    paramiko = None

class SimpleTransfer:
    """Classe simplifiée pour le transfert FTP/SFTP"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.connection = None
        self.protocol = self._determine_protocol()
        
    def _determine_protocol(self) -> str:
        """Utilise le protocole choisi par l'utilisateur"""
        ftp_config = self.config.get('ftp', {})
        
        # Protocole explicitement choisi par l'utilisateur
        protocol = ftp_config.get('protocol', 'ftp').lower()
        
        if protocol not in ['ftp', 'sftp']:
            self.logger.warning(f"Protocole invalide '{protocol}', utilisation de FTP par défaut")
            return 'ftp'
        
        if protocol == 'sftp' and not SFTP_SUPPORT:
            self.logger.error("SFTP demandé mais Paramiko non disponible, utilisation de FTP")
            return 'ftp'
        
        return protocol
    
    def connect(self) -> bool:
        """Se connecte au serveur avec le protocole choisi"""
        self.logger.info(f"Connexion {self.protocol.upper()} (protocole choisi par l'utilisateur)")
        
        success = self._try_connect(self.protocol)
        if success:
            self.logger.info(f"Connexion {self.protocol.upper()} réussie")
            return True
        else:
            self.logger.error(f"Échec de connexion {self.protocol.upper()}")
            return False
    
    def _try_connect(self, protocol):
        """Essaie de se connecter avec un protocole spécifique"""
        try:
            if protocol == 'sftp' and SFTP_SUPPORT:
                return self._connect_sftp()
            else:
                return self._connect_ftp()
        except Exception as e:
            self.logger.debug(f"Échec de connexion {protocol.upper()}: {e}")
            return False
    
    def _connect_ftp(self) -> bool:
        """Connexion FTP avec support FTPS (FTP over SSL) robuste"""
        try:
            ftp_config = self.config.get('ftp', {})
            
            # Vérifier si FTPS est demandé
            use_ftps = ftp_config.get('use_ftps', False)
            
            if use_ftps:
                # Utiliser FTPS (FTP over SSL) avec configuration robuste
                from ftplib import FTP_TLS
                import ssl
                
                # Créer contexte SSL avec vérification désactivée pour compatibilité
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                
                self.connection = FTP_TLS(context=context)
                self.logger.info("Connexion FTPS (FTP over SSL)")
            else:
                # Utiliser FTP standard
                self.connection = ftplib.FTP()
                self.logger.info("Connexion FTP standard")
            
            # Connexion au serveur
            self.connection.connect(
                ftp_config.get('server', 'localhost'),
                ftp_config.get('port', 21),
                timeout=15  # Timeout plus long pour FTPS
            )
            
            # Pour FTPS, établir la connexion sécurisée
            if use_ftps:
                self.connection.auth()  # Authentification SSL
                self.connection.prot_p()  # Protection des données
            
            # Login
            self.connection.login(
                ftp_config.get('username', ''),
                ftp_config.get('password', '')
            )
            
            # Set socket timeout for data transfers
            import socket
            self.connection.sock.settimeout(30)  # 30 second timeout for data transfers
            
            if ftp_config.get('passive_mode', True):
                self.connection.set_pasv(True)
            
            # Changer vers le répertoire de destination
            directory = ftp_config.get('directory', '')
            if directory and directory != '/':
                self.connection.cwd(directory)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur de connexion FTP: {e}")
            
            # Si FTPS échoue avec erreur SSL, essayer FTPS en mode implicite
            if use_ftps and any(keyword in str(e).lower() for keyword in ['ssl', 'tls', 'gnutls']):
                self.logger.warning("Erreur SSL détectée, tentative FTPS implicite...")
                try:
                    from ftplib import FTP_TLS
                    import ssl
                    
                    # Fermer la connexion précédente
                    if self.connection:
                        try:
                            self.connection.quit()
                        except:
                            pass
                    
                    # Essayer avec port 990 (FTPS implicite)
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    
                    self.connection = FTP_TLS(context=context)
                    
                    # Connexion sur port 990 avec SSL immédiat
                    self.connection.connect(
                        ftp_config.get('server', 'localhost'),
                        990,  # Port FTPS implicite
                        timeout=15
                    )
                    
                    # Pas besoin d'AUTH car SSL est déjà établi
                    self.connection.prot_p()  # Protection des données
                    
                    self.connection.login(
                        ftp_config.get('username', ''),
                        ftp_config.get('password', '')
                    )
                    
                    if ftp_config.get('passive_mode', True):
                        self.connection.set_pasv(True)
                    
                    directory = ftp_config.get('directory', '')
                    if directory and directory != '/':
                        self.connection.cwd(directory)
                    
                    self.logger.info("Connexion FTPS implicite (port 990) réussie")
                    return True
                    
                except Exception as e2:
                    self.logger.error(f"Échec FTPS implicite: {e2}")
            
            # Si FTPS échoue complètement, essayer FTP standard
            if use_ftps:
                self.logger.warning("Tentative FTP standard comme fallback...")
                try:
                    if self.connection:
                        try:
                            self.connection.quit()
                        except:
                            pass
                    
                    self.connection = ftplib.FTP()
                    self.connection.connect(
                        ftp_config.get('server', 'localhost'),
                        ftp_config.get('port', 21),
                        timeout=10
                    )
                    
                    self.connection.login(
                        ftp_config.get('username', ''),
                        ftp_config.get('password', '')
                    )
                    
                    if ftp_config.get('passive_mode', True):
                        self.connection.set_pasv(True)
                    
                    directory = ftp_config.get('directory', '')
                    if directory and directory != '/':
                        self.connection.cwd(directory)
                    
                    self.logger.info("Connexion FTP standard (fallback) réussie")
                    return True
                    
                except Exception as e3:
                    self.logger.error(f"Échec FTP fallback: {e3}")
            
            if self.connection:
                try:
                    self.connection.quit()
                except:
                    pass
                self.connection = None
            return False
    
    def _connect_sftp(self) -> bool:
        """Connexion SFTP"""
        if not SFTP_SUPPORT:
            self.logger.error("Paramiko non disponible pour SFTP")
            return False
        
        try:
            ftp_config = self.config.get('ftp', {})
            
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            ssh.connect(
                hostname=ftp_config.get('server', 'localhost'),
                port=ftp_config.get('port', 22),
                username=ftp_config.get('username', ''),
                password=ftp_config.get('password', ''),
                timeout=10
            )
            
            self.connection = ssh.open_sftp()
            
            # Changer vers le répertoire de destination
            directory = ftp_config.get('directory', '')
            if directory:
                try:
                    self.connection.chdir(directory)
                except:
                    # Créer le répertoire s'il n'existe pas
                    self.connection.mkdir(directory)
                    self.connection.chdir(directory)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur de connexion SFTP: {e}")
            if hasattr(self, 'connection') and self.connection:
                try:
                    self.connection.close()
                except:
                    pass
                self.connection = None
            return False
    
    def upload_file(self, local_path: str, remote_filename: Optional[str] = None) -> bool:
        """Upload un fichier avec gestion d'erreur améliorée et retry"""
        if not os.path.exists(local_path):
            self.logger.error(f"Fichier local non trouvé: {local_path}")
            return False

        # Vérifier la connexion et se reconnecter si nécessaire
        if not self.is_connected():
            self.logger.info("Reconnexion nécessaire...")
            if not self.connect():
                self.logger.error("Impossible de se reconnecter au serveur")
                return False

        if not remote_filename:
            remote_filename = os.path.basename(local_path)

        # Essayer plusieurs stratégies
        strategies = [
            {'blocksize': 8192, 'timeout': 60, 'name': 'Standard'},
            {'blocksize': 4096, 'timeout': 30, 'name': 'Petit buffer'},
            {'blocksize': 1024, 'timeout': 15, 'name': 'Très petit buffer'},
        ]
        
        for strategy in strategies:
            try:
                self.logger.info(f"Upload de {local_path} vers {remote_filename} (stratégie: {strategy['name']})")
                
                # Configurer timeout sur la socket
                if hasattr(self.connection, 'sock') and self.connection.sock:
                    self.connection.sock.settimeout(strategy['timeout'])
                
                if self.protocol == 'sftp':
                    self.connection.put(local_path, remote_filename)
                else:
                    with open(local_path, 'rb') as file:
                        # Fonction de callback pour suivre le progrès
                        def callback(data):
                            pass  # On pourrait logger le progrès ici
                        
                        # Upload avec buffer personnalisé
                        self.connection.storbinary(
                            f'STOR {remote_filename}', 
                            file, 
                            blocksize=strategy['blocksize'],
                            callback=callback
                        )
                
                self.logger.info(f"Upload réussi: {remote_filename} (stratégie: {strategy['name']})")
                return True
                
            except Exception as e:
                self.logger.warning(f"Échec avec stratégie {strategy['name']}: {e}")
                # Fermer et rouvrir la connexion pour la stratégie suivante
                self.disconnect()
                if not self.connect():
                    continue
                
        # Toutes les stratégies ont échoué
        self.logger.error(f"Échec d'upload après toutes les tentatives: {remote_filename}")
        self.disconnect()
        return False
    
    def upload_file_with_fallback(self, local_path: str, remote_filename: Optional[str] = None) -> bool:
        """Upload avec fallback automatique vers SFTP si FTPS échoue"""
        
        # Essayer d'abord avec le protocole configuré
        if self.upload_file(local_path, remote_filename):
            return True
        
        # Si échec et fallback activé, essayer SFTP
        ftp_config = self.config.get('ftp', {})
        if ftp_config.get('backup_protocol') == 'sftp' and SFTP_SUPPORT:
            self.logger.info("Tentative de fallback vers SFTP...")
            
            # Sauvegarder la config actuelle
            original_protocol = self.protocol
            original_connection = self.connection
            
            try:
                # Temporairement changer vers SFTP
                self.protocol = 'sftp'
                self.connection = None
                
                # Essayer de se connecter en SFTP
                if self._connect_sftp():
                    result = self.upload_file(local_path, remote_filename)
                    if result:
                        self.logger.info("Upload réussi via fallback SFTP")
                        return True
                        
            except Exception as e:
                self.logger.error(f"Échec du fallback SFTP: {e}")
            finally:
                # Restaurer la configuration originale
                self.protocol = original_protocol
                self.connection = original_connection
        
        return False
    
    def list_files(self) -> list:
        """Liste les fichiers du répertoire distant"""
        if not self.connection:
            return []
        
        try:
            if self.protocol == 'sftp':
                return self.connection.listdir()
            else:
                return self.connection.nlst()
        except Exception as e:
            self.logger.error(f"Erreur lors du listage: {e}")
            return []
    
    def disconnect(self):
        """Se déconnecte du serveur"""
        if self.connection:
            try:
                if self.protocol == 'sftp':
                    self.connection.close()
                else:
                    self.connection.quit()
            except:
                pass
            finally:
                self.connection = None
    
    def test_connection(self) -> Dict[str, Any]:
        """Test la connexion et retourne les détails"""
        result = {
            'success': False,
            'protocol': self.protocol,
            'message': '',
            'files_count': 0
        }
        
        try:
            if self.connect():
                files = self.list_files()
                result.update({
                    'success': True,
                    'protocol': self.protocol,
                    'message': f'Connexion réussie ({self.protocol.upper()})',
                    'files_count': len(files)
                })
                # On garde la connexion ouverte pour les opérations suivantes
                # self.disconnect() # Commenté pour éviter la déconnexion immédiate
            else:
                result['message'] = 'Connexion échouée'
        except Exception as e:
            result['message'] = f'Erreur: {str(e)}'
        
        return result
    
    def is_connected(self) -> bool:
        """Vérifie si la connexion est active"""
        if not self.connection:
            return False
        
        try:
            # Test simple selon le protocole
            if self.protocol == 'sftp':
                # Pour SFTP, on essaie de lister le répertoire actuel
                self.connection.listdir('.')
            else:
                # Pour FTP, on essaie un NOOP (No Operation)
                self.connection.voidcmd('NOOP')
            return True
        except:
            return False

    def ensure_dir(self, remote_dir: str) -> bool:
        """Assure que le répertoire distant existe, le créant si nécessaire"""
        if not self.connection:
            self.logger.error("Pas de connexion active pour créer le répertoire")
            return False
            
        try:
            if self.protocol == 'sftp':
                # Pour SFTP, utiliser makedirs-like functionality
                try:
                    # Tenter de créer le répertoire
                    self.connection.mkdir(remote_dir)
                    self.logger.info(f"Répertoire SFTP créé: {remote_dir}")
                    return True
                except Exception as e:
                    # Le répertoire existe peut-être déjà
                    try:
                        self.connection.stat(remote_dir)
                        self.logger.info(f"Répertoire SFTP existe déjà: {remote_dir}")
                        return True
                    except:
                        self.logger.error(f"Impossible de créer/vérifier le répertoire SFTP {remote_dir}: {e}")
                        return False
            else:
                # Pour FTP
                try:
                    # Tenter de changer vers le répertoire
                    current_dir = self.connection.pwd()
                    self.connection.cwd(remote_dir)
                    self.connection.cwd(current_dir)  # Revenir au répertoire original
                    self.logger.info(f"Répertoire FTP existe: {remote_dir}")
                    return True
                except ftplib.error_perm:
                    # Le répertoire n'existe pas, essayer de le créer
                    try:
                        self.connection.mkd(remote_dir)
                        self.logger.info(f"Répertoire FTP créé: {remote_dir}")
                        return True
                    except ftplib.error_perm as e:
                        self.logger.error(f"Impossible de créer le répertoire FTP {remote_dir}: {e}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Erreur lors de la création du répertoire {remote_dir}: {e}")
            return False
    
    def upload_file_local_backup(self, local_path: str, remote_filename: Optional[str] = None) -> bool:
        """Mode backup local - copie les fichiers localement pour les tests"""
        
        ftp_config = self.config.get('ftp', {})
        if not ftp_config.get('local_backup_mode', False):
            return False
            
        backup_path = ftp_config.get('local_backup_path', '/tmp/ftp_backup')
        
        try:
            import shutil
            os.makedirs(backup_path, exist_ok=True)
            
            if not remote_filename:
                remote_filename = os.path.basename(local_path)
                
            dest_path = os.path.join(backup_path, remote_filename)
            shutil.copy2(local_path, dest_path)
            
            self.logger.info(f"Fichier sauvegardé localement: {dest_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur backup local: {e}")
            return False
def create_transfer(config: Dict[str, Any]) -> SimpleTransfer:
    """Factory function pour créer une instance SimpleTransfer"""
    return SimpleTransfer(config)


# Fonctions de diagnostic
def test_ftp_connection(server: str, port: int = 21, timeout: int = 5) -> bool:
    """Test rapide de connexion FTP"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((server, port))
            return result == 0
    except:
        return False


def test_sftp_connection(server: str, port: int = 22, timeout: int = 5) -> bool:
    """Test rapide de connexion SFTP/SSH"""
    if not SFTP_SUPPORT:
        return False
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((server, port))
            return result == 0
    except:
        return False


def get_protocol_info() -> Dict[str, Any]:
    """Retourne les informations sur les protocoles supportés"""
    return {
        'ftp_support': True,
        'sftp_support': SFTP_SUPPORT,
        'paramiko_version': paramiko.__version__ if SFTP_SUPPORT else None
    }


if __name__ == '__main__':
    # Test simple
    logging.basicConfig(level=logging.INFO)
    
    test_config = {
        'ftp': {
            'server': 'localhost',
            'port': 21,
            'username': 'test',
            'password': 'test',
            'directory': '/uploads'
        }
    }
    
    transfer = SimpleTransfer(test_config)
    result = transfer.test_connection()
    print(f"Test de connexion: {result}")
