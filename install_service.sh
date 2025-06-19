#!/bin/bash
echo "Installation du service..."
sudo cp photo-ftp-web.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable photo-ftp-web.service
echo "Service installé. Démarrer avec: sudo systemctl start photo-ftp-web.service"
