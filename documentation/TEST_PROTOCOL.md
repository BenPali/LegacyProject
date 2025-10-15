# Test Protocol (Protocole d'Essais)

## Pré-requis
- Python 3.10+ installé
- Dépendances: `pip install -r requirements.txt`
- Environnement isolé (venv) recommandé

## Données de test
- Jeux fournis dans `data/` (personnes.json, families.json)
- Fixtures synthétiques générées par tests

## Exécution standard (CI locale)
```bash
python -m pytest tests/ -v --maxfail=1 --disable-warnings
```

## Étapes détaillées
1. Nettoyage
   ```bash
   make -C deployment clean || true
   ```
2. Installation
   ```bash
   pip install -r requirements.txt -r requirements-dev.txt
   ```
3. Tests unitaires & intégration
   ```bash
   python -m pytest tests/ -q --durations=10 --cov=python_restored --cov-report=term-missing
   ```
4. Tests E2E (démo fonctionnelle)
   ```bash
   python main.py
   ```
   Attendu: pas d'exception; sortie cohérente avec README.
5. Tests de sécurité (rapide)
   ```bash
   pip install safety bandit && safety check || true && bandit -r python_restored -q
   ```
6. Tests de performance (échantillon)
   - Lancer le micro-benchmark défini dans `STRATEGY_EVIDENCE.md`.

## Critères de réussite
- 100% des tests automatisés passent
- Couverture ≥80% global, ≥90% nouveau code
- Sortie `main.py` valide et déterministe

## Rapports
- `pytest` standard + `coverage`
- Export JUnit (CI): `--junitxml=reports/junit.xml`

## Traçabilité
- Lien scénario ↔ test dans `SCENARIO_COVERAGE.md`
- Changements notés dans `CHANGELOG.md`

## Procédure d'anomalie
1. Ouvrir un ticket (template bug)
2. Reproduire par test rouge
3. Corriger → tests verts
4. Ajouter au changelog


