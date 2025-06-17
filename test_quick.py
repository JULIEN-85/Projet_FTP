#!/usr/bin/env python3
"""
Tests rapides et économiques pour le système
"""

import os
import sys
import subprocess
import json

def test_gphoto2():
    """Test rapide gPhoto2"""
    try:
        result = subprocess.run(['gphoto2', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ gPhoto2 installé")
            
            # Test détection
            detect = subprocess.run(['gphoto2', '--auto-detect'], 
                                  capture_output=True, text=True, timeout=10)
            if 'usb:' in detect.stdout:
                print("📸 Appareil détecté")
            else:
                print("⚠️  Aucun appareil détecté")
            return True
        else:
            print("❌ gPhoto2 non fonctionnel")
            return False
    except Exception as e:
        print(f"❌ Erreur gPhoto2: {e}")
        return False

def test_config():
    """Test configuration"""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        if config.get('ftp', {}).get('server'):
            print("✅ Configuration FTP présente")
        else:
            print("⚠️  Configuration FTP à compléter")
        
        return True
    except Exception as e:
        print(f"❌ Erreur config: {e}")
        return False

def test_permissions():
    """Test permissions"""
    import grp
    try:
        groups = [g.gr_name for g in grp.getgrall() if os.getlogin() in g.gr_mem]
        if 'plugdev' in groups:
            print("✅ Permissions USB OK")
            return True
        else:
            print("❌ Manque permissions plugdev")
            return False
    except Exception:
        print("⚠️  Impossible de vérifier les permissions")
        return False

def test_services():
    """Test services"""
    try:
        result = subprocess.run(['systemctl', 'is-active', 'photo-ftp'], 
                              capture_output=True, text=True)
        if result.stdout.strip() == 'active':
            print("✅ Service principal actif")
        else:
            print("⚠️  Service principal inactif")
        
        result = subprocess.run(['systemctl', 'is-active', 'photo-ftp-web'], 
                              capture_output=True, text=True)
        if result.stdout.strip() == 'active':
            print("✅ Interface web active")
        else:
            print("⚠️  Interface web inactive")
        
        return True
    except Exception as e:
        print(f"❌ Erreur services: {e}")
        return False

def main():
    print("🧪 Tests rapides du système")
    print("=" * 30)
    
    tests = [
        ("Configuration", test_config),
        ("gPhoto2", test_gphoto2),
        ("Permissions", test_permissions),
        ("Services", test_services)
    ]
    
    passed = 0
    for name, test_func in tests:
        print(f"\n📋 Test {name}:")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 30)
    print(f"📊 Résultats: {passed}/{len(tests)} tests réussis")
    
    if passed == len(tests):
        print("🎉 Système opérationnel!")
    else:
        print("⚠️  Système partiellement fonctionnel")
    
    return passed == len(tests)

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
