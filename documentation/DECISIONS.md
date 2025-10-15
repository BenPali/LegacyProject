# Décisions et Justifications (ADR léger)

## D-001: Restauration fidèle vs réécriture
- Choix: restauration 1:1 du core OCaml en Python.
- Alternatives: réécriture moderne.
- Justification: contrainte d'énoncé « ne pas altérer le core », traçabilité des comportements, réduction du risque de régression.

## D-002: Pytest comme framework
- Alternatives: unittest, nose.
- Justification: écosystème riche, facilité de fixtures/paramétrage, intégration coverage/CI.

## D-003: Sécurité par wrapper
- Alternatives: modification du core.
- Justification: non-intrusif, respecte la contrainte; isolation claire des préoccupations.

## D-004: CI basée sur GitHub Actions + codecov
- Justification: visibilité continue, badges, gate qualité.

## D-005: Golden master pour régression
- Justification: comparer les sorties déterministes pour garantir l'identité fonctionnelle.


