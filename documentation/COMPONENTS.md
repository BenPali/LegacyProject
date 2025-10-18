# Composants du Système Restauré

## Vue d'ensemble
- `python_restored/definitions.py`: structures de données (Person, Family, etc.)
- `python_restored/gwdb.py`: logique d'accès et opérations sur la base généalogique
- `security/`: protections (chiffrement, validation, anonymisation)
- `deployment/`: scripts et Makefile pour installation/déploiement
- `main.py`: scénario de démonstration
- `tests/`: tests de validation de la restauration

## Interactions clés
1. `main.py` consomme `python_restored` pour charger données `data/`
2. `security/data_protection.py` offre des wrappers non-intrusifs
3. `deployment/deploy.sh` oriente l'exécution selon l'environnement

## Frontières et contraintes
- Préservation stricte du comportement OCaml dans `python_restored/`
- Couche sécurité ne modifie pas le core (wrapper)


