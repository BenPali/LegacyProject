# Test Policy (Politique de Test)

## Objectif
Assurer que la migration GeneWeb OCaml → Python préserve 100% des comportements fonctionnels, l'intégrité des données et des performances acceptables, avec une approche d'assurance qualité mesurable et traçable.

## Portée
- Code Python restauré dans `python_restored/`
- Scripts de démo `main.py` et déploiement `deployment/`
- Données d'exemple `data/`
- Couches de sécurité `security/`

## Références
- Stratégie détaillée: `TESTING_STRATEGY.md`
- Procédure d'exécution: `documentation/TEST_PROTOCOL.md`
- Couverture scénarios: `documentation/SCENARIO_COVERAGE.md`

## Niveaux de test et critères d'acceptation
- Unitaires (≥55% de l'effort)
  - Cible: logique métier, parsers, validateurs
  - DoD: couverture ≥90% sur nouveau code, invariants validés (property-based lorsque pertinent)
- Intégration (≈25%)
  - Cible: DB/IO, cohérence transactions, schémas
  - DoD: contraintes d'intégrité vérifiées, rollback OK
- API/Contrats (≈15%)
  - Cible: schémas, authz/authn, pagination
  - DoD: schémas validés, codes HTTP et erreurs stables
- E2E (≈5%)
  - Cible: parcours critiques (import GEDCOM, création famille, recherche, arbre, export)
  - DoD: taux de réussite 100% en CI sur les happy paths

## Tests non-fonctionnels (objectifs)
- Performance: import 10k pers <30s, recherche 100k <500ms
- Sécurité: aucune vulnérabilité critique (OWASP Top 10), dépendances saines
- Compatibilité: navigateurs/OS listés dans `TESTING_STRATEGY.md`
- Accessibilité: WCAG 2.1 AA (voir `documentation/ACCESSIBILITY.md`)

## Gouvernance et responsabilités
- QA Lead: garde la politique, suit les KPIs, arbitre les risques
- Dev: écrivent et maintiennent les tests unitaires/integ
- Test Engineers: automatisation E2E/perf/sécu
- Experts métier: valident cas de test et critères d'acceptation

## Processus
- TDD pour modules critiques; PR bloquée si tests manquants
- CI requise verte (tests, lint, sécurité)
- Revue de code incluant revue de tests
- Release: smoke + régression + perf minimales

## Mesure et reporting
- KPIs: couverture globale >80%, nouveau code >90%, stabilité tests >95%
- Tableaux de bord: CI + codecov + rapports d'exécution E2E

## Gestion des risques et régression
- Golden master vs version OCaml (sur résultats deterministes)
- Base de données de référence et checksums
- Feature flags et rollback planifiés

## Clause d'évolution
Document vivant: révision à chaque jalon majeur et REX de sprint.


