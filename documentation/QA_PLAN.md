# Quality Assurance Plan

## But
Garantir la qualité logicielle pendant la migration et après, via prévention (process) et détection (tests outillés).

## Piliers
- Prévention: TDD, revues, normes de code, lint
- Détection: tests multi-niveaux, analyse statique, scans sécurité
- Amélioration: métriques, REX, actions correctives

## Processus
- DoD: tests, doc à jour, scan sécu OK, couverture seuil atteinte
- CI/CD: build → tests → qualité → artefacts → déploiement démo
- Gate qualité: PR bloquées si seuils non atteints

## Rôles
- QA Lead: définit standards, suit KPIs
- Devs: tests unitaires/integ + doc
- Test Eng: E2E, perf, sécu

## KPIs
- Couverture >80% global, flaky <5%, MTTR <3j, défauts/sprint <5

## Outils
- pytest/coverage, hypothesis, playwright/selenium (optionnel), bandit/safety, codecov, GitHub Actions

## Gestion des risques
- Régression: suite automatisée + golden master
- Données: checksums, anonymisation
- Performance: budgets et tests réguliers

## Traçabilité
- Matrice scénario-tests: `SCENARIO_COVERAGE.md`
- Changelog: `CHANGELOG.md`


