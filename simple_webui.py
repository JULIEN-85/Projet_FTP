#!/usr/bin/env python3
"""
Interface web simplifiée pour le transfert de photos
"""

import os
import sys
import json
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from simple_main import SimpleFTPService

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/webui.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('WebUI')

# Créer l'application Flask
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Instance globale du service
photo_service = None

def get_photo_service():
    """Récupère ou crée l'instance du service photo"""
    global photo_service
    
    if not photo_service:
        try:
            photo_service = SimpleFTPService()
        except Exception as e:
            logger.error(f"Erreur initialisation service: {e}")
            # Créer un service basique si échec
            photo_service = SimpleFTPService(config_path='config.json')
    
    return photo_service

@app.route('/')
def index():
    """Page d'accueil"""
    global photo_service
    
    photo_service = get_photo_service()
    
    # Obtenir la configuration
    config = photo_service.config
    
    # Tester la connexion
    is_connected, connection_message = photo_service.test_connection()
    connection_status = 'success' if is_connected else 'error'
    
    # Vérifier le statut du dossier local
    local_path = config.get('camera', {}).get('download_path', '/tmp/photos')
    local_status = 'success' if os.path.exists(local_path) else 'warning'
    
    # Compter les photos en attente (si le dossier existe)
    photos_count = 0
    if os.path.exists(local_path):
        try:
            photo_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.raw']
            photos_count = len([f for f in os.listdir(local_path) 
                              if any(f.lower().endswith(ext) for ext in photo_extensions)])
        except (PermissionError, OSError):
            photos_count = 0
    
    # Statistiques basiques
    stats = {
        'total_photos': 0,  # Pourrait être lu depuis un fichier de statistiques
        'success_rate': '100%'  # Placeholder
    }
    
    # Statut du service
    service_status = photo_service.running if photo_service else False
    
    # Logs récents (optionnel)
    recent_logs = []
    log_file = os.path.join('logs', 'photo_transfer.log')
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                recent_logs = f.readlines()[-5:]  # 5 dernières lignes
        except (PermissionError, UnicodeDecodeError):
            recent_logs = []
    
    return render_template(
        'index.html',
        config=config,
        stats=stats,
        service_status=service_status,
        connection_status=connection_status,
        local_status=local_status,
        photos_count=photos_count,
        recent_logs=recent_logs
    )

@app.route('/status')
def status():
    """Affiche l'état du service"""
    global photo_service
    
    photo_service = get_photo_service()
    
    # Tester la connexion FTP
    is_connected, message = photo_service.test_connection()
    
    # Obtenir la configuration
    config = photo_service.config
    
    return render_template(
        'status.html', 
        connected=is_connected,
        message=message,
        config=config,
        running=photo_service.running
    )

@app.route('/config', methods=['GET', 'POST'])
def config():
    """Affiche et modifie la configuration"""
    global photo_service
    
    photo_service = get_photo_service()
    
    if request.method == 'POST':
        # Récupérer les données du formulaire
        ftp_config = {
            'server': request.form.get('server'),
            'port': int(request.form.get('port', 21)),
            'username': request.form.get('username'),
            'directory': request.form.get('directory', 'photos')
        }
        
        # Ajouter le protocole s'il est spécifié
        protocol = request.form.get('protocol')
        if protocol and protocol != 'auto':
            ftp_config['protocol'] = protocol
        
        # Ne mettre à jour le mot de passe que s'il a été modifié
        if request.form.get('password'):
            ftp_config['password'] = request.form.get('password')
        else:
            ftp_config['password'] = photo_service.config['ftp']['password']
        
        # Passive mode
        ftp_config['passive_mode'] = 'passive_mode' in request.form
        
        # FTPS support
        ftp_config['use_ftps'] = 'use_ftps' in request.form
        
        # Mise à jour de la configuration
        photo_service.config['ftp'] = ftp_config
        
        # Mettre à jour les paramètres de la caméra
        photo_service.config['camera'] = {
            'auto_detect': 'auto_detect' in request.form,
            'download_path': request.form.get('download_path', '/tmp/photos'),
            'delete_after_upload': 'delete_after_upload' in request.form
        }
        
        # Mettre à jour les paramètres système
        photo_service.config['system'] = {
            'log_level': request.form.get('log_level', 'INFO'),
            'check_interval': int(request.form.get('check_interval', 5)),
            'max_retries': int(request.form.get('max_retries', 3)),
            'web_port': int(request.form.get('web_port', 8080)),
            'web_host': request.form.get('web_host', '0.0.0.0')
        }
        
        # Sauvegarder la configuration
        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(photo_service.config, f, indent=4)
            
            flash("Configuration sauvegardée avec succès", "success")
            
            # Recharger le module de transfert avec la nouvelle configuration
            photo_service.reload_transfer()
            
            # Tester la connexion
            is_connected, message = photo_service.test_connection()
            if is_connected:
                flash(f"Test de connexion réussi: {message}", "success")
            else:
                flash(f"Test de connexion échoué: {message}", "warning")
                
        except Exception as e:
            flash(f"Erreur lors de la sauvegarde: {e}", "danger")
        
        return redirect(url_for('config'))
    else:
        return render_template('config.html', config=photo_service.config)

@app.route('/start')
def start_service():
    """Démarre le service"""
    global photo_service
    
    photo_service = get_photo_service()
    
    if not photo_service.running:
        photo_service.start()
        flash("Service démarré", "success")
    else:
        flash("Le service est déjà en cours d'exécution", "warning")
    
    return redirect(url_for('status'))

@app.route('/stop')
def stop_service():
    """Arrête le service"""
    global photo_service
    
    photo_service = get_photo_service()
    
    if photo_service.running:
        photo_service.stop()
        flash("Service arrêté", "warning")
    else:
        flash("Le service n'est pas en cours d'exécution", "info")
    
    return redirect(url_for('status'))

@app.route('/test')
def test_connection():
    """Teste la connexion FTP/SFTP"""
    global photo_service
    
    photo_service = get_photo_service()
    
    is_connected, message = photo_service.test_connection()
    
    if is_connected:
        flash(f"Test de connexion réussi: {message}", "success")
    else:
        flash(f"Test de connexion échoué: {message}", "danger")
    
    return redirect(url_for('status'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Upload manuel d'un ou plusieurs fichiers"""
    try:
        photo_service = get_photo_service()
        
        if request.method == 'POST':
            # Vérifier s'il y a des fichiers
            if 'file' not in request.files:
                return jsonify({'error': 'Aucun fichier sélectionné'}), 400
            
            files = request.files.getlist('file')
            
            if not files or all(f.filename == '' for f in files):
                return jsonify({'error': 'Aucun fichier valide sélectionné'}), 400
            
            uploaded_count = 0
            failed_count = 0
            failed_files = []
            
            # Créer le répertoire temporaire
            temp_dir = '/tmp/photo_uploads'
            os.makedirs(temp_dir, exist_ok=True)
            
            # Traiter chaque fichier
            for file in files:
                if file.filename == '':
                    continue
                    
                try:
                    # Sauvegarder temporairement le fichier
                    temp_path = os.path.join(temp_dir, file.filename)
                    file.save(temp_path)
                    
                    # Uploader le fichier
                    if photo_service.upload_photo_to_ftp(temp_path):
                        uploaded_count += 1
                        logger.info(f"Fichier uploadé avec succès: {file.filename}")
                    else:
                        failed_count += 1
                        failed_files.append(file.filename)
                        logger.error(f"Échec upload: {file.filename}")
                    
                    # Supprimer le fichier temporaire
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                        
                except Exception as e:
                    failed_count += 1
                    failed_files.append(file.filename)
                    logger.error(f"Erreur traitement {file.filename}: {e}")
            
            # Retourner le résultat
            if uploaded_count > 0:
                message = f"{uploaded_count} fichier(s) uploadé(s) avec succès"
                if failed_count > 0:
                    message += f", {failed_count} échec(s)"
                return jsonify({'success': True, 'message': message}), 200
            else:
                return jsonify({'error': f'Tous les uploads ont échoué: {", ".join(failed_files)}'}), 500
        
        else:
            return render_template('upload.html', config=photo_service.config)
            
    except Exception as e:
        logger.error(f"Erreur dans la route upload: {e}")
        if request.method == 'POST':
            return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500
        else:
            flash(f"Erreur: {str(e)}", "danger")
            return render_template('upload.html', config=photo_service.config)

# Point d'entrée
if __name__ == '__main__':
    # Créer les répertoires nécessaires
    os.makedirs('logs', exist_ok=True)
    
    # Créer le service
    photo_service = SimpleFTPService()
    
    # Obtenir la configuration du port web
    port = photo_service.config['system'].get('web_port', 8080)
    host = photo_service.config['system'].get('web_host', '0.0.0.0')
    
    logger.info(f"Démarrage du serveur web sur {host}:{port}")
    
    # Démarrer Flask
    app.run(host=host, port=port, debug=False)
