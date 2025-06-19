#!/usr/bin/env python3
"""
Module de gestion de configuration simplifié
"""

import os
import json
import logging

logger = logging.getLogger('ConfigUtil')

def load_config(config_path="config.json"):
    """
    Charge la configuration depuis un fichier JSON
    Gère automatiquement différents encodages
    """
    # Essayer différents encodages
    encodings = ['utf-8', 'latin-1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(config_path, 'r', encoding=encoding) as f:
                config = json.load(f)
                return config
        except UnicodeDecodeError:
            continue
        except json.JSONDecodeError:
            continue
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la config avec {encoding}: {e}")
            continue
    
    # Si on arrive ici, on n'a pas réussi à charger la config
    logger.error(f"Impossible de charger la configuration {config_path}")
    
    # Créer une configuration par défaut
    return create_default_config(config_path)

def save_config(config, config_path="config.json"):
    """
    Sauvegarde la configuration dans un fichier JSON
    """
    try:
        # Créer le répertoire parent si nécessaire
        os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
        
        # Enregistrer la configuration
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        
        logger.info(f"Configuration sauvegardée: {config_path}")
        return True
    except Exception as e:
        logger.error(f"Erreur sauvegarde configuration: {e}")
        return False

def create_default_config(config_path="config.json"):
    """
    Crée une configuration par défaut si aucune n'existe
    """
    default_config = {
        "ftp": {
            "server": "localhost",
            "port": 21,
            "username": "user",
            "password": "password",
            "directory": "photos",
            "passive_mode": True
        },
        "camera": {
            "auto_detect": True,
            "download_path": "/tmp/photos",
            "delete_after_upload": False
        },
        "system": {
            "log_level": "INFO",
            "check_interval": 5,
            "max_retries": 3,
            "web_port": 8080,
            "web_host": "0.0.0.0"
        }
    }
    
    # Essayer de sauvegarder la configuration par défaut
    if save_config(default_config, config_path):
        logger.info(f"Configuration par défaut créée: {config_path}")
    
    return default_config

def validate_config(config):
    """
    Vérifie que la configuration contient les champs requis
    """
    required_sections = ['ftp', 'camera', 'system']
    
    for section in required_sections:
        if section not in config:
            logger.error(f"Section manquante dans la config: {section}")
            return False
    
    # Vérifier les champs obligatoires dans la section FTP
    required_ftp_fields = ['server', 'port', 'username', 'password', 'directory']
    for field in required_ftp_fields:
        if field not in config['ftp']:
            logger.error(f"Champ manquant dans la section FTP: {field}")
            return False
    
    return True

def update_config(config, updates):
    """
    Met à jour la configuration avec de nouvelles valeurs
    """
    for section, values in updates.items():
        if section not in config:
            config[section] = {}
            
        for key, value in values.items():
            config[section][key] = value
    
    return config
