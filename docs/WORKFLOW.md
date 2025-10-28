# Guide d’organisation et de flux de travail

Ce document résume notre manière de travailler, les bonnes pratiques adoptées et le pipeline qui sécurise nos livraisons.

## Principes clés

- Gestion du projet via GitHub Project (tasks, priorisation, assignations).
- Flux de contribution: issue → branche → PR → review (≥1 approbation) → merge.
- Push direct sur `main` bloqué (sauf exception admin pour urgences contrôlées).
- CI/CD systématique sur chaque PR et sur `main`.
- Couverture mesurée et publiée via Codecov, avec gate de merge si le seuil n’est pas atteint.
- Dependabot surveille les dépendances et ouvre des PR de mise à jour automatiquement.

## Cycle de développement

1. Création de l’issue dans GitHub Project, description claire (objectif, critères d’acceptation, risques).
2. Assignation de l’issue et création d’une branche dédiée.
3. Développement et commits réguliers, petits et cohérents.
4. Ouverture de la Pull Request, lien vers l’issue, description, checklist et captures/logs si pertinent.
5. Revue par au moins une personne (lecture attentive, commentaires constructifs, suggestions).
6. CI/CD exécute les tests, mesure la couverture, et bloque si le seuil minimal n’est pas respecté.
7. Merge sur `main` quand les checks passent et la revue est validée.

## Règles de branchement et commits

- Nommage des branches: `feature/<issue-id>-court-intitulé`, `fix/<issue-id>-court-intitulé`, `chore/...`.
- Messages de commit: clairs et orientés résultat (ex: “fix(database): corrige lecture des patches invalides”).
- Une PR reste de taille raisonnable; découper quand nécessaire pour faciliter la revue.

## CI/CD et couverture

- Tests unitaires et d’intégration exécutés sur chaque PR.
- Publication de la couverture via Codecov; seuil configurable côté dépôt.
- Les merges sont bloqués si la couverture chute en dessous du seuil défini.
- La pipeline doit rester rapide et fiable; un test flaky est soit stabilisé, soit temporairement isolé.

## Sécurité des dépendances

- Dependabot surveille les versions et ouvre des PR automatiquement.
- Les PR de mises à jour suivent le même cycle (tests, revue, merge).
- En cas d’alerte de sécurité, prioriser la mise à jour et documenter l’impact.

## Déploiement

- Cible: VPS
- Déploiement orchestré depuis `main` après validation CI/CD.

## Bonnes pratiques de revue

- Vérifier lisibilité, modularité, tests associés et impact sur la couverture.
- Exiger au moins une validation; encourager les suggestions plutôt que les injonctions.
- Documenter les décisions (dans la PR) pour tracer le pourquoi du changement.

## En bref

Un flux clair, une CI/CD stricte et des règles simples nous permettent de livrer vite et en confiance. Les outils (GitHub Project, Codecov, Dependabot) automatisent le suivi, la qualité et la sécurité, tandis que la revue par les pairs garantit la robustesse du code avant chaque merge.
