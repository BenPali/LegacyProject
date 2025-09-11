# Analyse du Code OCaml GeneWeb Original

## Structure du Projet GeneWeb

### Modules Principaux Identifiés

#### 1. Module `Def` - Définitions de Base
```ocaml
(* Types de base pour la généalogie *)
type sex = Male | Female | Neuter
type death = NotDead | Dead of date | DontKnowIfDead | OfCourseDead of date
type burial = UnknownBurial | Buried of date | Cremated of date
type access = IfTitles | Public | Private
type date = Dgregorian of dmy | Dtext of string | Dnone
type dmy = { day : int; month : int; year : int; prec : precision; delta : int }
type precision = Sure | About | Maybe | Before | After | OrYear of dmy | YearInt of dmy
```

#### 2. Module `Gwdb` - Base de Données
```ocaml
(* Gestion de la base de données généalogique *)
type person = {
  key : iper;
  first_name : string;
  surname : string;
  occ : int;
  public_name : string;
  image : string;
  first_name_aliases : string list;
  surname_aliases : string list;
  qualifiers : string list;
  titles : title list;
  rparents : relation list;
  related : iper list;
  occupation : string;
  sex : sex;
  access : access;
  birth : date option;
  birth_place : string;
  birth_src : string;
  baptism : date option;
  baptism_place : string;
  baptism_src : string;
  death : death;
  death_place : string;
  death_src : string;
  burial : burial;
  burial_place : string;
  burial_src : string;
  pevents : event list;
  notes : string;
  psources : string;
  key_index : int;
  consang : int;
  linked_page : string option;
  has_sources : bool;
  families : ifam list;
  families_u : ifam list;
}

type family = {
  key : ifam;
  marriage : date option;
  marriage_place : string;
  marriage_src : string;
  witnesses : iper list;
  relation : relation_type;
  divorce : divorce;
  fevents : event list;
  comment : string;
  origin_file : string;
  fsources : string;
  fam_index : int;
  sex : sex;
  children : iper list;
  parents : iper array;
}
```

#### 3. Fonctions Métier Critiques
```ocaml
(* Fonctions principales à restaurer *)
let get_person : iper -> person option
let get_family : ifam -> family option
let get_parents : iper -> iper array
let get_children : ifam -> iper list
let get_siblings : iper -> iper list
let get_spouse : iper -> ifam -> iper option
let get_ancestors : iper -> int -> iper list
let get_descendants : iper -> int -> iper list
let get_relationship : iper -> iper -> relationship option
let get_common_ancestor : iper -> iper -> iper option
```

## Fonctionnalités Principales à Restaurer

### 1. Gestion des Personnes
- Création et modification des profils personnels
- Gestion des dates (naissance, décès, baptême)
- Gestion des lieux et sources
- Gestion des événements personnels

### 2. Gestion des Familles
- Création et gestion des unions
- Gestion des enfants
- Gestion des divorces
- Gestion des témoins de mariage

### 3. Calculs de Généalogie
- Calcul des relations familiales
- Traçage des ancêtres et descendants
- Calcul de la consanguinité
- Génération d'arbres généalogiques

### 4. Interface Utilisateur
- Génération HTML pour visualisation web
- Recherche et filtrage
- Export de données
- Import de données

## Contraintes de Restauration

### ✅ À Préserver Exactement
- Structures de données OCaml
- Algorithmes de calcul
- Logique métier
- Comportements fonctionnels

### ❌ À Ne Pas Ajouter
- Nouvelles fonctionnalités
- Modifications de l'interface
- Changements d'architecture
- Améliorations non demandées

## Plan de Restauration

### Étape 1 : Traduction des Types
- Conversion des types OCaml en Python équivalent
- Préservation de la sémantique des données
- Maintien de la compatibilité

### Étape 2 : Traduction des Fonctions
- Conversion des fonctions OCaml en Python
- Préservation de la logique algorithmique
- Maintien des mêmes résultats

### Étape 3 : Tests de Validation
- Comparaison des résultats OCaml vs Python
- Validation avec des données de test
- Vérification de la fidélité

### Étape 4 : Sécurisation
- Ajout de couches de sécurité non-intrusives
- Protection des données sensibles
- Contrôle d'accès basique

### Étape 5 : Déploiement
- Configuration pour différents environnements
- Scripts de déploiement automatisés
- Documentation de maintenance
