# Preuves d'Exécution de la Stratégie

## Preuves automatiques
- Badges CI et codecov visibles dans `README.md`
- Rapport `pytest` vert (voir section Démonstration)

## Exemples de mesures
- Durées top 10 tests (`--durations=10`)
- Couverture par fichier (rapport coverage)

## Micro-benchmarks (exemple)
Exécuter:
```bash
python - <<'PY'
import time
from python_restored.gwdb import Gwdb
from python_restored.definitions import Person

db = Gwdb.load('data/persons.json', 'data/families.json')
start = time.time()
for _ in range(1000):
    _ = db.find_person_by_id('P1')
print('lookup_1k_ms=', (time.time()-start)*1000)
PY
```

## Traçabilité documentaire
- Décisions: `documentation/DECISIONS.md`
- Changelog: `CHANGELOG.md`
- Scénarios: `documentation/SCENARIO_COVERAGE.md`


