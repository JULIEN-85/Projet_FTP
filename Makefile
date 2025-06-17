# Makefile pour le système de transfert automatique de photos
# Utilisation: make <target>

.PHONY: help install uninstall test backup update clean status start stop restart logs

# Configuration
PROJECT_DIR = /home/pi/photo-ftp
PYTHON = python3
VENV_DIR = $(PROJECT_DIR)/venv
PIP = $(VENV_DIR)/bin/pip
PYTHON_VENV = $(VENV_DIR)/bin/python

# Couleurs pour l'affichage
BLUE = \033[0;34m
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## Affiche cette aide
	@echo "$(BLUE)Système de Transfert Automatique de Photos$(NC)"
	@echo "============================================="
	@echo ""
	@echo "$(YELLOW)Commandes disponibles:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""

install: ## Installation complète du système
	@echo "$(BLUE)Installation du système...$(NC)"
	chmod +x install.sh
	./install.sh

uninstall: ## Désinstallation complète du système
	@echo "$(YELLOW)Désinstallation du système...$(NC)"
	chmod +x uninstall.sh
	./uninstall.sh

test: ## Lance les tests du système
	@echo "$(BLUE)Lancement des tests...$(NC)"
	$(PYTHON) test_system.py

test-quick: ## Test rapide des composants essentiels
	@echo "$(BLUE)Test rapide des composants...$(NC)"
	@echo "📁 Vérification des fichiers..."
	@test -f main.py && echo "✅ main.py" || echo "❌ main.py manquant"
	@test -f webui.py && echo "✅ webui.py" || echo "❌ webui.py manquant"
	@test -f config.json && echo "✅ config.json" || echo "❌ config.json manquant"
	@echo "🐍 Test Python..."
	@$(PYTHON) -c "import json; print('✅ Python JSON OK')" 2>/dev/null || echo "❌ Python problème"
	@echo "🌐 Test Flask..."
	@$(PYTHON) -c "import flask; print('✅ Flask disponible')" 2>/dev/null || echo "❌ Flask non installé"

test-web: ## Test de l'interface web uniquement
	@echo "$(BLUE)Démarrage test interface web...$(NC)"
	@echo "🌐 Interface accessible sur: http://localhost:8080"
	@echo "🛑 Appuyez Ctrl+C pour arrêter"
	$(PYTHON) webui.py

backup: ## Crée une sauvegarde complète
	@echo "$(BLUE)Création d'une sauvegarde...$(NC)"
	chmod +x backup.sh
	./backup.sh

update: ## Met à jour le système
	@echo "$(BLUE)Mise à jour du système...$(NC)"
	chmod +x update.sh
	./update.sh

clean: ## Nettoie les fichiers temporaires
	@echo "$(YELLOW)Nettoyage des fichiers temporaires...$(NC)"
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache 2>/dev/null || true
	rm -f *.log 2>/dev/null || true
	sudo rm -rf /tmp/photos/* 2>/dev/null || true
	@echo "$(GREEN)✓ Nettoyage terminé$(NC)"

# Gestion des services
start: ## Démarre les services
	@echo "$(BLUE)Démarrage des services...$(NC)"
	sudo systemctl start photo-ftp-web.service
	sudo systemctl start photo-ftp.service
	@echo "$(GREEN)✓ Services démarrés$(NC)"

stop: ## Arrête les services
	@echo "$(YELLOW)Arrêt des services...$(NC)"
	sudo systemctl stop photo-ftp.service || true
	sudo systemctl stop photo-ftp-web.service || true
	@echo "$(GREEN)✓ Services arrêtés$(NC)"

restart: stop start ## Redémarre les services

status: ## Affiche le statut des services
	@echo "$(BLUE)Statut des services:$(NC)"
	@echo ""
	@echo "$(YELLOW)Service principal (photo-ftp):$(NC)"
	sudo systemctl status photo-ftp.service --no-pager -l || echo "Service non actif"
	@echo ""
	@echo "$(YELLOW)Interface web (photo-ftp-web):$(NC)"
	sudo systemctl status photo-ftp-web.service --no-pager -l || echo "Service non actif"
	@echo ""
	@echo "$(YELLOW)Connectivité réseau:$(NC)"
	@ip addr show | grep "inet " | grep -v "127.0.0.1" | awk '{print "  Interface disponible:", $$NF, "-", $$2}'

logs: ## Affiche les logs en temps réel
	@echo "$(BLUE)Logs en temps réel (Ctrl+C pour arrêter):$(NC)"
	sudo journalctl -u photo-ftp.service -u photo-ftp-web.service -f

logs-main: ## Affiche les logs du service principal
	@echo "$(BLUE)Logs du service principal:$(NC)"
	sudo journalctl -u photo-ftp.service -n 50 --no-pager

logs-web: ## Affiche les logs de l'interface web
	@echo "$(BLUE)Logs de l'interface web:$(NC)"
	sudo journalctl -u photo-ftp-web.service -n 50 --no-pager

logs-file: ## Affiche les logs du fichier
	@echo "$(BLUE)Logs du fichier photo_transfer.log:$(NC)"
	tail -50 $(PROJECT_DIR)/logs/photo_transfer.log 2>/dev/null || echo "Fichier de log non trouvé"

# Tests spécifiques
test-camera: ## Test de l'appareil photo uniquement
	@echo "$(BLUE)Test de l'appareil photo...$(NC)"
	gphoto2 --auto-detect || echo "$(YELLOW)Aucun appareil détecté$(NC)"
	@echo "$(CYAN)💡 Pour les téléphones: make setup-phone$(NC)"

setup-phone: ## Configuration pour téléphones Android
	@echo "$(BLUE)Configuration téléphone Android...$(NC)"
	chmod +x setup_phone.sh
	./setup_phone.sh

test-ftp: ## Test de la configuration FTP
	@echo "$(BLUE)Test de la configuration FTP...$(NC)"
	$(PYTHON_VENV) -c "from main import PhotoTransferService; service = PhotoTransferService(); print('FTP:', service.test_ftp_connection())"

test-deps: ## Test des dépendances
	@echo "$(BLUE)Test des dépendances...$(NC)"
	@echo "Python: $$(python3 --version)"
	@echo "gPhoto2: $$(gphoto2 --version | head -1)"
	@echo "Flask: $$($(PIP) show flask | grep Version)"

# Développement
dev-setup: ## Configuration de l'environnement de développement
	@echo "$(BLUE)Configuration de l'environnement de développement...$(NC)"
	$(PYTHON) -m venv venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install flask-debugtoolbar pylint black
	@echo "$(GREEN)✓ Environnement de développement configuré$(NC)"

dev-run: ## Lance en mode développement
	@echo "$(BLUE)Lancement en mode développement...$(NC)"
	@echo "Interface web: http://localhost:8080"
	FLASK_ENV=development $(PYTHON_VENV) webui.py

# Monitoring
monitor: ## Surveille le système (CPU, mémoire, espace disque)
	@echo "$(BLUE)Monitoring du système:$(NC)"
	@echo ""
	@echo "$(YELLOW)CPU et mémoire:$(NC)"
	top -bn1 | grep "photo-ftp\|python" | head -5
	@echo ""
	@echo "$(YELLOW)Espace disque:$(NC)"
	df -h | grep -E "(Filesystem|/dev/root|/dev/mmcblk)"
	@echo ""
	@echo "$(YELLOW)Température:$(NC)"
	vcgencmd measure_temp 2>/dev/null || echo "Non disponible"
	@echo ""
	@echo "$(YELLOW)Connexions réseau:$(NC)"
	ss -tuln | grep ":8080\|:21"

# Maintenance
fix-permissions: ## Corrige les permissions
	@echo "$(YELLOW)Correction des permissions...$(NC)"
	sudo chown -R pi:pi $(PROJECT_DIR)
	chmod +x $(PROJECT_DIR)/*.py
	chmod +x $(PROJECT_DIR)/*.sh
	@echo "$(GREEN)✓ Permissions corrigées$(NC)"

# Configuration
config-edit: ## Édite la configuration
	@echo "$(BLUE)Édition de la configuration...$(NC)"
	nano $(PROJECT_DIR)/config.json

config-backup: ## Sauvegarde la configuration
	@echo "$(YELLOW)Sauvegarde de la configuration...$(NC)"
	cp $(PROJECT_DIR)/config.json $(PROJECT_DIR)/config.json.backup.$$(date +%Y%m%d_%H%M%S)
	@echo "$(GREEN)✓ Configuration sauvegardée$(NC)"

config-restore: ## Restaure la configuration par défaut
	@echo "$(YELLOW)Restauration de la configuration par défaut...$(NC)"
	cp $(PROJECT_DIR)/config.example.json $(PROJECT_DIR)/config.json
	@echo "$(GREEN)✓ Configuration par défaut restaurée$(NC)"

# Informations
info: ## Affiche les informations système
	@echo "$(BLUE)Informations système:$(NC)"
	@echo ""
	@echo "$(YELLOW)Système:$(NC)"
	@uname -a
	@echo ""
	@echo "$(YELLOW)Modèle Raspberry Pi:$(NC)"
	@cat /proc/device-tree/model 2>/dev/null || echo "Non détecté"
	@echo ""
	@echo "$(YELLOW)Distribution:$(NC)"
	@lsb_release -a 2>/dev/null || cat /etc/os-release | head -2
	@echo ""
	@echo "$(YELLOW)Python:$(NC)"
	@python3 --version
	@echo ""
	@echo "$(YELLOW)gPhoto2:$(NC)"
	@gphoto2 --version | head -1
	@echo ""
	@echo "$(YELLOW)Services:$(NC)"
	@systemctl is-active photo-ftp.service || echo "photo-ftp: inactif"
	@systemctl is-active photo-ftp-web.service || echo "photo-ftp-web: inactif"
	@echo ""
	@echo "$(YELLOW)Réseau:$(NC)"
	@hostname -I | awk '{print "IP:", $$1}'
	@echo "Interface web: http://$$(hostname -I | awk '{print $$1}'):8080"
	@echo ""
	@echo "$(YELLOW)Température (si Pi):$(NC)"
	@vcgencmd measure_temp 2>/dev/null || echo "Non disponible"

optimize-pi5: ## Optimise le système pour Raspberry Pi 5
	@echo "$(BLUE)Optimisation pour Raspberry Pi 5...$(NC)"
	chmod +x optimize-pi5.sh
	./optimize-pi5.sh

monitor-pi5: ## Monitoring spécifique Pi 5
	@echo "$(BLUE)Monitoring Raspberry Pi 5:$(NC)"
	@if [ -f "monitor-pi5.sh" ]; then \
		./monitor-pi5.sh; \
	else \
		echo "$(RED)Script monitor-pi5.sh non trouvé. Exécutez 'make optimize-pi5' d'abord.$(NC)"; \
	fi

# Aide contextuelle
install-help: ## Aide pour l'installation
	@echo "$(BLUE)Aide à l'installation:$(NC)"
	@echo ""
	@echo "1. Exécutez: make install"
	@echo "2. Redémarrez: sudo reboot"
	@echo "3. Connectez votre appareil photo"
	@echo "4. Configurez via: http://[IP]:8080"
	@echo ""

troubleshoot: ## Guide de dépannage
	@echo "$(BLUE)Guide de dépannage:$(NC)"
	@echo ""
	@echo "$(YELLOW)Problèmes courants:$(NC)"
	@echo "• Appareil photo non détecté: make test-camera"
	@echo "• Erreur FTP: make test-ftp"
	@echo "• Service ne démarre pas: make logs-main"
	@echo "• Interface web inaccessible: make logs-web"
	@echo ""
	@echo "$(YELLOW)Commandes utiles:$(NC)"
	@echo "• État général: make status"
	@echo "• Tests complets: make test"
	@echo "• Logs en temps réel: make logs"
	@echo "• Redémarrage: make restart"
	@echo ""
