#!/usr/bin/env python3
"""
Script de diagnostic pour les transferts FTP qui arrivent vides (0 octet)
"""

import os
import sys
import json
import subprocess
import tempfile
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('FTPZeroByteTest')

def load_config():
    """Charge la configuration"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erreur chargement config: {e}")
        return None

def create_test_file():
    """Crée un fichier de test"""
    test_content = b"Test file content - " + datetime.now().strftime("%Y-%m-%d %H:%M:%S").encode() + b"\n"
    test_content += b"This is a test to verify FTP transfer integrity.\n" * 100  # ~5KB
    
    test_file = "/tmp/ftp_test.txt"
    with open(test_file, 'wb') as f:
        f.write(test_content)
    
    logger.info(f"Fichier test créé: {test_file} ({len(test_content)} octets)")
    return test_file, len(test_content)

def test_lftp_transfer(config, test_file, original_size):
    """Test le transfert avec lftp"""
    logger.info("🔍 Test avec lftp...")
    
    ftp_config = config['ftp']
    use_ftps = ftp_config.get('use_ftps', True)
    
    # Configuration lftp
    commands = []
    
    if use_ftps:
        commands.extend([
            'set ftp:ssl-force true',
            'set ftp:ssl-protect-data true',
            'set ssl:verify-certificate false'
        ])
    
    # Ajouter debug pour voir ce qui se passe
    commands.extend([
        'set cmd:trace true',  # Debug des commandes
        'set net:timeout 30',
        'set net:max-retries 3',
        f'open -u {ftp_config["username"]},{ftp_config["password"]} {ftp_config["server"]}',
        f'cd {ftp_config["directory"]}',
        f'put "{test_file}" -o "test_lftp.txt"',
        'ls -l test_lftp.txt',  # Vérifier la taille sur le serveur
        'quit'
    ])
    
    lftp_script = '\n'.join(commands)
    
    try:
        result = subprocess.run(
            ['lftp'], 
            input=lftp_script.encode(), 
            capture_output=True,
            text=True,
            timeout=60
        )
        
        logger.info(f"Code retour lftp: {result.returncode}")
        logger.info(f"Sortie lftp:\n{result.stdout}")
        
        if result.stderr:
            logger.warning(f"Erreurs lftp:\n{result.stderr}")
        
        return result.returncode == 0
        
    except Exception as e:
        logger.error(f"Erreur lftp: {e}")
        return False

def test_curl_transfer(config, test_file, original_size):
    """Test le transfert avec curl"""
    logger.info("🔍 Test avec curl...")
    
    ftp_config = config['ftp']
    use_ftps = ftp_config.get('use_ftps', True)
    
    # URL FTP
    protocol = "ftps" if use_ftps else "ftp"
    url = f"{protocol}://{ftp_config['username']}:{ftp_config['password']}@{ftp_config['server']}{ftp_config['directory']}/test_curl.txt"
    
    # Options curl
    cmd = ['curl', '-v', '--upload-file', test_file]
    
    if use_ftps:
        cmd.extend(['-k', '--ftp-ssl'])  # -k ignore les certificats SSL
    
    cmd.append(url)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        logger.info(f"Code retour curl: {result.returncode}")
        logger.info(f"Sortie curl:\n{result.stdout}")
        
        if result.stderr:
            logger.info(f"Debug curl:\n{result.stderr}")
        
        return result.returncode == 0
        
    except Exception as e:
        logger.error(f"Erreur curl: {e}")
        return False

def test_python_ftplib(config, test_file, original_size):
    """Test le transfert avec Python ftplib"""
    logger.info("🔍 Test avec Python ftplib...")
    
    try:
        import ftplib
        import ssl
        
        ftp_config = config['ftp']
        use_ftps = ftp_config.get('use_ftps', True)
        
        if use_ftps:
            # Contexte SSL permissif
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            ftp = ftplib.FTP_TLS(context=context)
        else:
            ftp = ftplib.FTP()
        
        # Connexion
        ftp.connect(ftp_config['server'], ftp_config['port'])
        ftp.login(ftp_config['username'], ftp_config['password'])
        
        if use_ftps:
            ftp.prot_p()  # Protection des données
        
        # Changer de répertoire
        ftp.cwd(ftp_config['directory'])
        
        # Différentes méthodes de transfert
        methods = [
            ("STOR normal", lambda: ftp.storbinary('STOR test_python_normal.txt', open(test_file, 'rb'))),
            ("STOR petit buffer", lambda: ftp.storbinary('STOR test_python_small.txt', open(test_file, 'rb'), blocksize=1024)),
            ("STOR très petit buffer", lambda: ftp.storbinary('STOR test_python_tiny.txt', open(test_file, 'rb'), blocksize=512))
        ]
        
        success_count = 0
        for method_name, method_func in methods:
            try:
                logger.info(f"Tentative: {method_name}")
                method_func()
                logger.info(f"✅ {method_name} réussi")
                success_count += 1
            except Exception as e:
                logger.error(f"❌ {method_name} échoué: {e}")
        
        ftp.quit()
        return success_count > 0
        
    except Exception as e:
        logger.error(f"Erreur Python ftplib: {e}")
        return False

def test_binary_mode_issues(config, test_file, original_size):
    """Test spécifique pour les problèmes de mode binaire"""
    logger.info("🔍 Test des problèmes de mode binaire...")
    
    try:
        import ftplib
        import ssl
        
        ftp_config = config['ftp']
        use_ftps = ftp_config.get('use_ftps', True)
        
        if use_ftps:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            ftp = ftplib.FTP_TLS(context=context)
        else:
            ftp = ftplib.FTP()
        
        ftp.connect(ftp_config['server'], ftp_config['port'])
        ftp.login(ftp_config['username'], ftp_config['password'])
        
        if use_ftps:
            ftp.prot_p()
        
        ftp.cwd(ftp_config['directory'])
        
        # Test du mode passif vs actif
        logger.info("Test mode passif...")
        ftp.set_pasv(True)
        try:
            with open(test_file, 'rb') as f:
                ftp.storbinary('STOR test_passive.txt', f)
            logger.info("✅ Mode passif OK")
        except Exception as e:
            logger.error(f"❌ Mode passif échoué: {e}")
        
        logger.info("Test mode actif...")
        ftp.set_pasv(False)
        try:
            with open(test_file, 'rb') as f:
                ftp.storbinary('STOR test_active.txt', f)
            logger.info("✅ Mode actif OK")
        except Exception as e:
            logger.error(f"❌ Mode actif échoué: {e}")
        
        ftp.quit()
        return True
        
    except Exception as e:
        logger.error(f"Erreur test binaire: {e}")
        return False

def main():
    """Fonction principale"""
    logger.info("🚀 Diagnostic des transferts FTP avec fichiers vides")
    
    # Charger la config
    config = load_config()
    if not config:
        sys.exit(1)
    
    # Créer un fichier de test
    test_file, original_size = create_test_file()
    
    logger.info(f"📋 Configuration FTP:")
    logger.info(f"  Serveur: {config['ftp']['server']}:{config['ftp']['port']}")
    logger.info(f"  Utilisateur: {config['ftp']['username']}")
    logger.info(f"  Répertoire: {config['ftp']['directory']}")
    logger.info(f"  FTPS: {config['ftp'].get('use_ftps', False)}")
    
    # Tests successifs
    tests = [
        ("lftp", test_lftp_transfer),
        ("curl", test_curl_transfer),
        ("Python ftplib", test_python_ftplib),
        ("Modes binaires", test_binary_mode_issues)
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Test: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            results[test_name] = test_func(config, test_file, original_size)
        except Exception as e:
            logger.error(f"Erreur durant le test {test_name}: {e}")
            results[test_name] = False
    
    # Résumé
    logger.info(f"\n{'='*50}")
    logger.info("RÉSUMÉ DES TESTS")
    logger.info(f"{'='*50}")
    
    for test_name, success in results.items():
        status = "✅ RÉUSSI" if success else "❌ ÉCHEC"
        logger.info(f"{test_name:20} : {status}")
    
    # Nettoyage
    try:
        os.unlink(test_file)
    except:
        pass
    
    logger.info(f"\n📝 Vérifiez manuellement les fichiers sur le serveur pour confirmer les tailles:")
    logger.info(f"   - test_lftp.txt")
    logger.info(f"   - test_curl.txt") 
    logger.info(f"   - test_python_*.txt")
    logger.info(f"   - test_passive.txt")
    logger.info(f"   - test_active.txt")

if __name__ == "__main__":
    main()
