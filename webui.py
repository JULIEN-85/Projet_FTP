#!/usr/bin/env python3
"""
Interface web optimisée pour Raspberry Pi - Économie d'énergie
"""

import os
import json
import logging
import gc
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from main import PhotoTransferService
import subprocess

# Configuration Flask optimisée
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Clé aléatoire plus sûre
app.config.update(
    SECRET_KEY=os.urandom(24),
    PERMANENT_SESSION_LIFETIME=1800,  # 30 minutes
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max
    JSON_SORT_KEYS=False,  # Désactiver le tri JSON pour économiser CPU
    JSONIFY_PRETTYPRINT_REGULAR=False  # Pas de formatage JSON inutile
)

# Instance globale du service
photo_service = None

def load_config():
    """Charge la configuration"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        return None

def save_config(config):
    """Sauvegarde la configuration"""
    try:
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        return False

def get_logs(max_lines=50):  # Réduire le nombre de lignes par défaut
    """Récupère les dernières lignes des logs - version optimisée"""
    try:
        log_file = 'logs/photo_transfer.log'
        if os.path.exists(log_file):
            # Lecture optimisée - seulement les dernières lignes
            with open(log_file, 'rb') as f:
                # Aller à la fin du fichier
                f.seek(0, 2)
                file_size = f.tell()
                
                # Lire les derniers blocs pour trouver les dernières lignes
                lines = []
                buffer_size = min(8192, file_size)  # 8KB max
                f.seek(max(0, file_size - buffer_size))
                lines = f.read().decode('utf-8', errors='ignore').splitlines()
                
                return lines[-max_lines:] if len(lines) > max_lines else lines
                lines = f.readlines()
                return lines[-max_lines:]
        return []
    except Exception:
        return []

@app.route('/')
def index():
    """Page d'accueil avec le statut du système"""
    global photo_service
    
    config = load_config()
    if not config:
        flash('Erreur de chargement de la configuration', 'error')
        return redirect(url_for('config_page'))
    
    # Statut du service
    status = {
        'running': False,
        'photos_transferred': 0,
        'last_photo': None,
        'last_transfer_time': None,
        'errors': 0,
        'queue_size': 0
    }
    
    if photo_service:
        status = photo_service.get_status()
    
    # Tests de connexion
    test_service = PhotoTransferService()
    camera_status, camera_msg = test_service.test_camera_connection()
    ftp_status, ftp_msg = test_service.test_ftp_connection()
    
    return render_template('index.html', 
                         config=config, 
                         status=status,
                         camera_status=camera_status,
                         camera_msg=camera_msg,
                         ftp_status=ftp_status,
                         ftp_msg=ftp_msg)

@app.route('/config')
def config_page():
    """Page de configuration"""
    config = load_config()
    if not config:
        # Configuration par défaut si le fichier n'existe pas
        config = {
            "ftp": {
                "server": "",
                "port": 21,
                "username": "",
                "password": "",
                "directory": "/uploads",
                "passive_mode": True
            },
            "camera": {
                "auto_detect": True,
                "download_path": "/tmp/photos",
                "delete_after_upload": True
            },
            "system": {
                "log_level": "INFO",
                "check_interval": 5,
                "max_retries": 3,
                "web_port": 8080,
                "web_host": "0.0.0.0"
            }
        }
    
    return render_template('config.html', config=config)

@app.route('/save_config', methods=['POST'])
def save_config_route():
    """Sauvegarde la configuration"""
    try:
        config = {
            "ftp": {
                "server": request.form.get('ftp_server', ''),
                "port": int(request.form.get('ftp_port', 21)),
                "username": request.form.get('ftp_username', ''),
                "password": request.form.get('ftp_password', ''),
                "directory": request.form.get('ftp_directory', '/uploads'),
                "passive_mode": request.form.get('ftp_passive') == 'on'
            },
            "camera": {
                "auto_detect": request.form.get('camera_auto_detect') == 'on',
                "download_path": request.form.get('camera_download_path', '/tmp/photos'),
                "delete_after_upload": request.form.get('camera_delete_after') == 'on'
            },
            "system": {
                "log_level": request.form.get('system_log_level', 'INFO'),
                "check_interval": int(request.form.get('system_check_interval', 5)),
                "max_retries": int(request.form.get('system_max_retries', 3)),
                "web_port": int(request.form.get('system_web_port', 8080)),
                "web_host": request.form.get('system_web_host', '0.0.0.0')
            }
        }
        
        if save_config(config):
            flash('Configuration sauvegardée avec succès', 'success')
            
            # Redémarrer le service si il est en cours
            global photo_service
            if photo_service and photo_service.running:
                photo_service.stop()
                photo_service = PhotoTransferService()
                photo_service.start()
                flash('Service redémarré avec la nouvelle configuration', 'info')
        else:
            flash('Erreur lors de la sauvegarde', 'error')
            
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'error')
    
    return redirect(url_for('config_page'))

@app.route('/test_camera')
def test_camera():
    """Test de la connexion appareil photo"""
    test_service = PhotoTransferService()
    status, message = test_service.test_camera_connection()
    
    return jsonify({
        'status': status,
        'message': message
    })

@app.route('/test_ftp')
def test_ftp():
    """Test de la connexion FTP"""
    test_service = PhotoTransferService()
    status, message = test_service.test_ftp_connection()
    
    return jsonify({
        'status': status,
        'message': message
    })

@app.route('/start_service')
def start_service():
    """Démarre le service de transfert"""
    global photo_service
    
    try:
        if photo_service and photo_service.running:
            return jsonify({
                'status': False,
                'message': 'Le service est déjà en cours d\'exécution'
            })
        
        photo_service = PhotoTransferService()
        if photo_service.start():
            return jsonify({
                'status': True,
                'message': 'Service démarré avec succès'
            })
        else:
            return jsonify({
                'status': False,
                'message': 'Échec du démarrage du service'
            })
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Erreur: {str(e)}'
        })

@app.route('/stop_service')
def stop_service():
    """Arrête le service de transfert"""
    global photo_service
    
    try:
        if photo_service and photo_service.running:
            photo_service.stop()
            return jsonify({
                'status': True,
                'message': 'Service arrêté'
            })
        else:
            return jsonify({
                'status': False,
                'message': 'Le service n\'est pas en cours d\'exécution'
            })
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Erreur: {str(e)}'
        })

@app.route('/status')
def status_api():
    """API pour récupérer le statut en temps réel"""
    global photo_service
    
    if photo_service:
        return jsonify(photo_service.get_status())
    else:
        return jsonify({
            'status': 'Stopped',
            'photos_transferred': 0,
            'last_photo': None,
            'last_transfer_time': None,
            'errors': 0,
            'queue_size': 0
        })

@app.route('/logs')
def logs_page():
    """Page d'affichage des logs"""
    logs = get_logs(200)
    return render_template('logs.html', logs=logs)

@app.route('/logs_api')
def logs_api():
    """API pour récupérer les logs"""
    max_lines = request.args.get('max_lines', 100, type=int)
    logs = get_logs(max_lines)
    return jsonify({'logs': logs})

@app.route('/power_status')
def power_status():
    """API pour statut énergétique"""
    try:
        # Température CPU
        temp = subprocess.run(['vcgencmd', 'measure_temp'], 
                            capture_output=True, text=True)
        temperature = temp.stdout.strip() if temp.returncode == 0 else "N/A"
        
        # Fréquence CPU
        freq = subprocess.run(['vcgencmd', 'measure_clock', 'arm'], 
                            capture_output=True, text=True)
        frequency = freq.stdout.strip() if freq.returncode == 0 else "N/A"
        
        # Mémoire
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()
        
        mem_total = 0
        mem_available = 0
        for line in meminfo.split('\n'):
            if line.startswith('MemTotal:'):
                mem_total = int(line.split()[1])
            elif line.startswith('MemAvailable:'):
                mem_available = int(line.split()[1])
        
        mem_usage = round((mem_total - mem_available) / mem_total * 100, 1)
        
        return jsonify({
            'temperature': temperature,
            'frequency': frequency,
            'memory_usage': f"{mem_usage}%",
            'power_mode': 'eco' if photo_service and hasattr(photo_service, 'sleep_mode') and photo_service.sleep_mode else 'normal'
        })
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    config = load_config()
    if config:
        host = config.get('system', {}).get('web_host', '0.0.0.0')
        port = config.get('system', {}).get('web_port', 8080)
    else:
        host = '0.0.0.0'
        port = 8080
    
    app.run(host=host, port=port, debug=False)
