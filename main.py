#!/usr/bin/env python3
"""
Système de transfert automatique de photos via Raspberry Pi
Script principal pour la surveillance et le transfert des photos
"""

import os
import sys
import json
import time
import logging
import subprocess
import threading
from datetime import datetime
from pathlib import Path
import ftplib
import signal
import queue

class PhotoTransferService:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self.running = False
        self.logger = self.setup_logging()
        self.photo_queue = queue.Queue()
        self.stats = {
            "photos_transferred": 0,
            "last_photo": None,
            "last_transfer_time": None,
            "errors": 0,
            "status": "Stopped"
        }
        
        # Créer le dossier de téléchargement s'il n'existe pas
        os.makedirs(self.config["camera"]["download_path"], exist_ok=True)
        
    def load_config(self):
        """Charge la configuration depuis le fichier JSON"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error(f"Fichier de configuration {self.config_path} non trouvé")
            sys.exit(1)
        except json.JSONDecodeError as e:
            self.logger.error(f"Erreur dans le fichier de configuration: {e}")
            sys.exit(1)
    
    def setup_logging(self):
        """Configure le système de logs"""
        log_level = getattr(logging, self.config["system"]["log_level"])
        
        # Créer le dossier logs s'il n'existe pas
        os.makedirs("logs", exist_ok=True)
        
        # Configuration du logger
        logger = logging.getLogger('PhotoTransfer')
        logger.setLevel(log_level)
        
        # Handler pour fichier
        file_handler = logging.FileHandler('logs/photo_transfer.log')
        file_handler.setLevel(log_level)
        
        # Handler pour console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        # Format des logs
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def test_camera_connection(self):
        """Teste la connexion avec l'appareil photo ou téléphone"""
        try:
            result = subprocess.run(['gphoto2', '--auto-detect'], 
                                   capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and 'usb:' in result.stdout:
                # Extraire les informations de l'appareil détecté
                lines = result.stdout.strip().split('\n')
                device_info = []
                
                for line in lines:
                    if 'usb:' in line:
                        device_info.append(line.strip())
                
                if device_info:
                    device_list = '\n'.join(device_info)
                    
                    # Détecter si c'est un téléphone
                    phone_indicators = ['Android', 'Samsung', 'Google', 'Huawei', 'OnePlus', 'Xiaomi']
                    is_phone = any(indicator in device_list for indicator in phone_indicators)
                    
                    if is_phone:
                        self.logger.info("Téléphone détecté en mode PTP")
                        return True, f"📱 Téléphone détecté:\n{device_list}\n💡 Mode PTP actif"
                    else:
                        self.logger.info("Appareil photo détecté")
                        return True, f"📸 Appareil photo détecté:\n{device_list}"
                else:
                    return False, "Aucun appareil détecté par gPhoto2"
            else:
                return False, "Aucun appareil photo/téléphone détecté. Vérifiez la connexion USB et le mode PTP pour les téléphones."
                
        except subprocess.TimeoutExpired:
            return False, "Timeout lors de la détection - vérifiez la connexion USB"
        except FileNotFoundError:
            return False, "gPhoto2 non installé. Installez avec: sudo apt install gphoto2"
        except Exception as e:
            return False, f"Erreur lors du test: {str(e)}"

    def test_ftp_connection(self):
        """Test la connexion FTP"""
        try:
            ftp = ftplib.FTP()
            ftp.connect(
                self.config["ftp"]["server"], 
                self.config["ftp"]["port"]
            )
            ftp.login(
                self.config["ftp"]["username"], 
                self.config["ftp"]["password"]
            )
            
            if self.config["ftp"]["passive_mode"]:
                ftp.set_pasv(True)
            
            # Test d'accès au dossier
            try:
                ftp.cwd(self.config["ftp"]["directory"])
            except ftplib.error_perm:
                # Le dossier n'existe pas, on essaie de le créer
                ftp.mkd(self.config["ftp"]["directory"])
                ftp.cwd(self.config["ftp"]["directory"])
            
            ftp.quit()
            self.logger.info("Connexion FTP réussie")
            return True, "Connexion FTP réussie"
            
        except Exception as e:
            self.logger.error(f"Erreur de connexion FTP: {e}")
            return False, str(e)
    
    def capture_new_photos(self):
        """Capture les nouvelles photos depuis l'appareil photo"""
        try:
            # Vérifier les nouvelles photos
            result = subprocess.run(
                ["gphoto2", "--get-all-files", "--skip-existing", 
                 f"--filename={self.config['camera']['download_path']}/IMG_%Y%m%d_%H%M%S.jpg"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Analyser la sortie pour identifier les nouvelles photos
                lines = result.stdout.split('\n')
                new_photos = []
                
                for line in lines:
                    if "Saving file as" in line:
                        # Extraire le nom du fichier
                        filename = line.split("Saving file as ")[-1].strip()
                        if filename:
                            new_photos.append(filename)
                            self.logger.info(f"Nouvelle photo capturée: {filename}")
                
                return new_photos
            else:
                self.logger.warning(f"Erreur gPhoto2: {result.stderr}")
                return []
                
        except subprocess.TimeoutExpired:
            self.logger.error("Timeout lors de la capture des photos")
            return []
        except Exception as e:
            self.logger.error(f"Erreur lors de la capture: {e}")
            return []
    
    def upload_photo_to_ftp(self, photo_path):
        """Upload une photo vers le serveur FTP"""
        try:
            filename = os.path.basename(photo_path)
            
            ftp = ftplib.FTP()
            ftp.connect(
                self.config["ftp"]["server"], 
                self.config["ftp"]["port"]
            )
            ftp.login(
                self.config["ftp"]["username"], 
                self.config["ftp"]["password"]
            )
            
            if self.config["ftp"]["passive_mode"]:
                ftp.set_pasv(True)
            
            # Aller dans le dossier de destination
            ftp.cwd(self.config["ftp"]["directory"])
            
            # Upload du fichier
            with open(photo_path, 'rb') as file:
                ftp.storbinary(f'STOR {filename}', file)
            
            ftp.quit()
            
            self.logger.info(f"Photo uploadée avec succès: {filename}")
            
            # Mettre à jour les statistiques
            self.stats["photos_transferred"] += 1
            self.stats["last_photo"] = filename
            self.stats["last_transfer_time"] = datetime.now().isoformat()
            
            # Supprimer le fichier local si configuré
            if self.config["camera"]["delete_after_upload"]:
                os.remove(photo_path)
                self.logger.info(f"Fichier local supprimé: {photo_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur upload FTP pour {photo_path}: {e}")
            self.stats["errors"] += 1
            return False
    
    def process_photo_queue(self):
        """Traite la queue des photos à uploader"""
        while self.running:
            try:
                photo_path = self.photo_queue.get(timeout=1)
                
                # Tentatives d'upload avec retry
                for attempt in range(self.config["system"]["max_retries"]):
                    if self.upload_photo_to_ftp(photo_path):
                        break
                    else:
                        if attempt < self.config["system"]["max_retries"] - 1:
                            self.logger.warning(f"Tentative {attempt + 1} échouée, retry dans 5s")
                            time.sleep(5)
                        else:
                            self.logger.error(f"Upload définitivement échoué pour {photo_path}")
                
                self.photo_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Erreur dans le traitement de la queue: {e}")
    
    def monitor_camera(self):
        """Surveille l'appareil photo en continu"""
        self.logger.info("Démarrage de la surveillance de l'appareil photo")
        
        while self.running:
            try:
                # Vérifier la connexion de l'appareil photo
                camera_ok, _ = self.test_camera_connection()
                
                if camera_ok:
                    # Capturer les nouvelles photos
                    new_photos = self.capture_new_photos()
                    
                    # Ajouter les nouvelles photos à la queue
                    for photo in new_photos:
                        if os.path.exists(photo):
                            self.photo_queue.put(photo)
                            self.logger.info(f"Photo ajoutée à la queue: {photo}")
                
                # Attendre avant la prochaine vérification
                time.sleep(self.config["system"]["check_interval"])
                
            except Exception as e:
                self.logger.error(f"Erreur dans la surveillance: {e}")
                time.sleep(10)
    
    def start(self):
        """Démarre le service"""
        self.logger.info("Démarrage du service de transfert de photos")
        self.running = True
        self.stats["status"] = "Running"
        
        # Vérifications initiales
        camera_ok, camera_msg = self.test_camera_connection()
        ftp_ok, ftp_msg = self.test_ftp_connection()
        
        if not camera_ok:
            self.logger.warning(f"Appareil photo non détecté: {camera_msg}")
        
        if not ftp_ok:
            self.logger.error(f"Connexion FTP échouée: {ftp_msg}")
            self.stats["status"] = "FTP Error"
            return False
        
        # Démarrer les threads
        upload_thread = threading.Thread(target=self.process_photo_queue, daemon=True)
        monitor_thread = threading.Thread(target=self.monitor_camera, daemon=True)
        
        upload_thread.start()
        monitor_thread.start()
        
        self.logger.info("Service démarré avec succès")
        return True
    
    def stop(self):
        """Arrête le service"""
        self.logger.info("Arrêt du service")
        self.running = False
        self.stats["status"] = "Stopped"
        
        # Attendre que la queue soit vide
        self.photo_queue.join()
    
    def get_status(self):
        """Retourne le statut actuel du service"""
        return {
            **self.stats,
            "config": self.config,
            "queue_size": self.photo_queue.qsize()
        }

def signal_handler(signum, frame):
    """Gestionnaire de signaux pour l'arrêt propre"""
    global service
    if service:
        service.stop()
    sys.exit(0)

if __name__ == "__main__":
    # Configuration des signaux
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Créer et démarrer le service
    service = PhotoTransferService()
    
    if service.start():
        try:
            # Maintenir le service en vie
            while service.running:
                time.sleep(1)
        except KeyboardInterrupt:
            service.stop()
    else:
        print("Échec du démarrage du service")
        sys.exit(1)
