# Couverture des Scénarios

Ce document relie les scénarios utilisateurs critiques aux tests présents.

## Matrice Scénario ↔ Tests

| Scénario | Description | Tests associés |
|---|---|---|
| Import de données | Charger données `data/` et valider structures | `tests/test_restoration.py::test_data_integrity`, `::test_structures_presence` |
| Création d'une famille | Validation relations parent-enfant, unions | `tests/test_restoration.py::test_family_relations` |
| Recherche d'une personne | Accès par identifiant/attributs | `tests/test_restoration.py::test_person_lookup` |
| Calcul de parenté | Relations généalogiques complexes | `tests/test_restoration.py::test_genealogical_computations` |
| Export/Itérations | Parcours et sérialisation stable | `tests/test_restoration.py::test_iteration_stability` |
| Démonstration E2E | Exécution `main.py` sans erreur | Voir `DEMONSTRATION.md` |

## Couverture et écarts
- Couverture actuelle: voir badge codecov et rapport local `coverage`.
- Écarts identifiés: E2E UI (hors scope), perf large dataset (prévu jalon Q3).


