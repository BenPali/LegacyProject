# Makefile pour le déploiement du système GeneWeb restauré
# Respecte les exigences du projet avec les règles re, clean, fclean

.PHONY: help install test clean fclean re deploy security-check demo

# Cible par défaut
help:
	@echo "Commandes disponibles pour le système GeneWeb restauré :"
	@echo "  install        - Installer les dépendances"
	@echo "  test           - Exécuter les tests de validation"
	@echo "  clean          - Nettoyer les fichiers temporaires"
	@echo "  fclean         - Nettoyer complètement le projet"
	@echo "  re             - Nettoyer et reconstruire"
	@echo "  deploy         - Déployer le système"
	@echo "  security-check - Vérifier la sécurité"
	@echo "  demo           - Démonstration du système"

# Installation des dépendances
install:
	pip install pytest cryptography

# Exécution des tests de validation
test:
	python -m pytest ../tests/ -v

# Nettoyage des fichiers temporaires
clean:
	find .. -type f -name "*.pyc" -delete
	find .. -type d -name "__pycache__" -delete
	find .. -type f -name "*.log" -delete
	rm -rf ../.pytest_cache/
	rm -rf ../htmlcov/
	rm -rf ../.coverage

# Nettoyage complet (fclean)
fclean: clean
	rm -rf ../build/
	rm -rf ../dist/
	rm -rf ../*.egg-info/
	rm -rf ../data/
	rm -rf ../logs/

# Reconstruction complète (re)
re: fclean install test

# Déploiement du système
deploy:
	@echo "Déploiement du système GeneWeb restauré..."
	mkdir -p ../data ../logs
	python -c "import sys; sys.path.append('../python_restored'); from python_restored import Gwdb; print('Système GeneWeb restauré prêt')"

# Vérification de sécurité
security-check:
	python -c "import sys; sys.path.append('../security'); from security import DataProtection; dp = DataProtection(); print('Sécurité active:', dp.get_security_info())"

# Démonstration du système
demo:
	@echo "=== Démonstration du système GeneWeb restauré ==="
	python ../main.py
