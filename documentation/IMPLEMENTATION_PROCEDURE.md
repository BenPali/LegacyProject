# Procédure d'Implémentation

## Préparation
1. Cloner le dépôt et créer un venv
2. `pip install -r requirements.txt -r requirements-dev.txt`

## Mise en place
1. Lancer les tests pour baseline
   ```bash
   python -m pytest tests/ -v
   ```
2. Exécuter la démo
   ```bash
   python main.py
   ```
3. Déploiement démo via Makefile
   ```bash
   make -C deployment demo
   ```

## Contrôles qualité
- Lint/format: outils du `requirements-dev.txt`
- Sécurité: `bandit`, `safety`
- Couverture: `coverage`/codecov

## Traçabilité
- Documenter dans `CHANGELOG.md`
- Lier décisions dans `documentation/DECISIONS.md`


