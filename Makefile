# Makefile simplifié pour Raspberry Pi
.PHONY: help install start stop status logs test clean

# Couleurs
BLUE=\033[0;34m
GREEN=\033[0;32m
YELLOW=\033[0;33m
RED=\033[0;31m
NC=\033[0m

# Variables
PYTHON=python3
SERVICE_MAIN=photo-ftp
SERVICE_WEB=photo-ftp-web

help: ## Affiche cette aide
	@echo "$(BLUE)Photo Transfer System - Commandes disponibles:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'

install: ## Installation complète
	@echo "$(BLUE)Installation...$(NC)"
	chmod +x install_minimal.sh
	./install_minimal.sh

start: ## Démarre les services
	@echo "$(BLUE)Démarrage des services...$(NC)"
	sudo systemctl start $(SERVICE_MAIN) $(SERVICE_WEB)
	@echo "$(GREEN)Services démarrés$(NC)"

stop: ## Arrête les services
	@echo "$(BLUE)Arrêt des services...$(NC)"
	sudo systemctl stop $(SERVICE_MAIN) $(SERVICE_WEB)
	@echo "$(YELLOW)Services arrêtés$(NC)"

restart: ## Redémarre les services
	@echo "$(BLUE)Redémarrage...$(NC)"
	sudo systemctl restart $(SERVICE_MAIN) $(SERVICE_WEB)

status: ## État des services
	@echo "$(BLUE)État des services:$(NC)"
	@systemctl is-active $(SERVICE_MAIN) && echo "$(GREEN)✅ photo-ftp: actif$(NC)" || echo "$(RED)❌ photo-ftp: inactif$(NC)"
	@systemctl is-active $(SERVICE_WEB) && echo "$(GREEN)✅ web interface: active$(NC)" || echo "$(RED)❌ web interface: inactive$(NC)"

logs: ## Affiche les logs
	@echo "$(BLUE)Logs du service principal:$(NC)"
	sudo journalctl -u $(SERVICE_MAIN) -n 20 --no-pager

test: ## Tests rapides
	@echo "$(BLUE)Tests du système...$(NC)"
	@echo "📸 Test gPhoto2:"
	@gphoto2 --auto-detect || echo "Aucun appareil détecté"
	@echo "🌐 Test interface web:"
	@curl -s http://localhost:8080 > /dev/null && echo "✅ Interface accessible" || echo "❌ Interface inaccessible"

clean: ## Nettoyage logs
	@echo "$(BLUE)Nettoyage...$(NC)"
	sudo journalctl --vacuum-time=7d
	find logs/ -name "*.log" -mtime +7 -delete 2>/dev/null || true

info: ## Informations système
	@echo "$(BLUE)Informations système:$(NC)"
	@echo "OS: $(shell cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2 | tr -d '\"')"
	@echo "Pi: $(shell cat /proc/device-tree/model 2>/dev/null || echo 'Non détecté')"
	@echo "CPU: $(shell cat /proc/cpuinfo | grep 'model name' | head -1 | cut -d: -f2 | xargs || echo 'Non détecté')"
	@echo "Température: $(shell vcgencmd measure_temp 2>/dev/null || echo 'Non disponible')"
	@echo "Mémoire: $(shell free -h | grep Mem | awk '{print $$3 "/" $$2}')"
	@echo "IP: $(shell hostname -I | awk '{print $$1}')"
	@echo "Interface: http://$(shell hostname -I | awk '{print $$1}'):8080"
