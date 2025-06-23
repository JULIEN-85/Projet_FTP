#!/usr/bin/env python3
"""
Script simple : détecte les fichiers dans /tmp/photos et les envoie sur le serveur FTP dans C:\FTP\photos
"""
import os
from ftplib import FTP

FTP_HOST = "192.168.1.22"
FTP_USER = "julien"
FTP_PASS = "2004"
FTP_DIR = "/photos"  # correspond à C:\FTP\photos côté serveur
LOCAL_DIR = "/tmp/photos"

# Connexion FTP
ftp = FTP()
ftp.connect(FTP_HOST, 21, timeout=15)
ftp.login(FTP_USER, FTP_PASS)

# Aller dans le bon dossier
try:
    ftp.cwd(FTP_DIR)
except Exception:
    ftp.mkd(FTP_DIR)
    ftp.cwd(FTP_DIR)

# Parcourir les fichiers locaux
for filename in os.listdir(LOCAL_DIR):
    local_path = os.path.join(LOCAL_DIR, filename)
    if os.path.isfile(local_path):
        with open(local_path, "rb") as f:
            print(f"Envoi de {filename}...")
            ftp.storbinary(f"STOR {filename}", f)

ftp.quit()
print("Transfert terminé.")
