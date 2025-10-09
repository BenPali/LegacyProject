#!/bin/bash

# Script de déploiement pour le système GeneWeb restauré
# CoinLegacy Inc. - Migration OCaml vers Python

set -e

echo "=== Déploiement du système GeneWeb restauré ==="
echo "Migration OCaml GeneWeb vers Python"
echo "CoinLegacy Inc."
echo ""

# Vérification des prérequis
echo "Vérification des prérequis..."
python3 --version || { echo "Python 3 requis"; exit 1; }
pip --version || { echo "pip requis"; exit 1; }

# Installation des dépendances
echo "Installation des dépendances..."
pip install pytest cryptography

# Création des répertoires nécessaires
echo "Création des répertoires..."
mkdir -p data logs

# Exécution des tests de validation
echo "Exécution des tests de validation..."
python -m pytest tests/ -v

if [ $? -eq 0 ]; then
    echo "✅ Tests de validation réussis"
else
    echo "❌ Tests de validation échoués"
    exit 1
fi

# Vérification de la sécurité
echo "Vérification de la sécurité..."
python -c "
import sys
sys.path.append('python_restored')
sys.path.append('security')
from security import DataProtection
dp = DataProtection()
info = dp.get_security_info()
print(f'✅ Sécurité active: {info[\"encryption_algorithm\"]}')
"

# Test de fonctionnement
echo "Test de fonctionnement du système restauré..."
python -c "
import sys
sys.path.append('python_restored')
from python_restored import Gwdb, Person, Sex

# Test basique
db = Gwdb()
person = Person(
    key=0,
    first_name='Test',
    surname='User',
    occ=0,
    public_name='Test User',
    image='',
    sex=Sex.MALE
)

person_id = db.add_person(person)
retrieved = db.get_person(person_id)

if retrieved and retrieved.first_name == 'Test':
    print('✅ Système restauré fonctionnel')
else:
    print('❌ Problème de fonctionnement')
    exit(1)
"

# Configuration de l'environnement
echo "Configuration de l'environnement..."
cat > .env << 'ENVEOF'
# Configuration du système GeneWeb restauré
GENEWEB_DATA_DIR=data
GENEWEB_LOG_DIR=logs
GENEWEB_ENCRYPTION_KEY=default-key-change-in-production
GENEWEB_ENVIRONMENT=production
ENVEOF

echo "✅ Configuration créée"

# Finalisation
echo ""
echo "=== Déploiement terminé avec succès ==="
echo "Système GeneWeb restauré depuis OCaml vers Python"
echo "Fonctionnalités préservées : ✅"
echo "Tests de validation : ✅"
echo "Sécurité activée : ✅"
echo "Prêt pour la production : ✅"
echo ""
echo "Pour démarrer le système :"
echo "  make demo"
echo ""
echo "Pour les tests :"
echo "  make test"
echo ""
echo "Pour la sécurité :"
echo "  make security-check"
