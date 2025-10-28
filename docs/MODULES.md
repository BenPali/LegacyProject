# Modules Python — Vue d’ensemble et fonctionnement

Ce document présente brièvement les modules Python implémentés, leur rôle et les grandes lignes de leur fonctionnement. Les descriptions ci‑dessous s’appuient sur le code des fichiers concernés.

## Cœur et types

- `gwdef.py` — Définitions des structures généalogiques (personnes, familles, événements, titres, avertissements). Fournit les énumérations (`Sex`, `Access`, `GenPersEventName`, `GenFamEventName`, etc.) et les dataclasses génériques `GenPerson`, `GenFamily`, `GenPersEvent`, `GenFamEvent`, ainsi que `BaseNotes`.
- `adef.py` — Types et auxiliaires génériques (dates, calendriers, couples, constantes). Sert de base aux conversions et à la représentation des dates.
- `date.py` — Conversions et comparaisons de dates. Implémente la compression/décompression des `Dmy`, la conversion entre `Date` et `Cdate`, et des aides pour comparer des dates (strict ou non).
- `calendar.py` — Conversion entre formats de calendrier et enveloppes `Dmy`/`Dmy2`.
- `name.py` — Normalisation des noms: abréviations, suppression d’accents, transformation en minuscules, concaténation et vérification des caractères interdits.
- `utf8.py` — Aides sur UTF‑8 (parcours, longueur) utilisées par la normalisation des noms.

## Base de données

- `dbdisk.py` — Contrats et interfaces de la couche disque: `RecordAccess`, `StringPersonIndex`, `BaseData`, `BaseFunc`, `BaseVersion`, `DskBase`, et `Perm`. Définit la forme des données et des fonctions manipulées par la base.
- `database.py` — Ouverture et lecture d’une base GeneWeb. `with_database` vérifie les « magic numbers » pour déterminer `BaseVersion`, construit les accès immuables aux tableaux, applique les patches (`input_patches`/`commit_patches`), charge la synchro (`input_synchro`) et les `particles.txt`. Fournit les fonctions d’index (personnes par nom/prénom) selon la version et encapsule l’exécution d’un callback sur `DskBase`.
- `driver.py` — Accès haut niveau aux personnes/familles. Charge paresseusement les structures `GenPerson`, `GenFamily`, `GenAscend`, `GenUnion` à partir des accès disque et expose des helpers pour naviguer dans la base (ex: `gen_person_of_person`, `no_person`).
- `dutil.py` — Helpers de conversion entre structures disque et structures génériques (ex: `person_to_gen_person`, `ascend_to_gen_ascend`, etc.) et utilitaires d’index/tri.
- `outbase.py` — Écriture d’une base et de ses index. Produit `base`, `base.acc`, les index `names.inx/acc`, les tables `snames.dat/inx` et `fnames.dat/inx`, le fichier `nb_persons`, les notes et `particles.txt`. Utilise `secure`/`iovalue` et renomme des fichiers temporaires en atomique.
- `filesystem.py` — Opérations de fichiers sécurisées: création de dossiers avec permissions, copie, suppression, vérification de type/permission.
- `secure.py` — Garde‑fou pour l’accès aux fichiers: vérifie les chemins autorisés, fournit des wrappers d’ouverture (`open_in_bin`, `open_out_bin`, etc.).

## Entrées/sorties

- `iovalue.py` — Sérialisation binaire des valeurs: lecture (`input_value`) et écriture (`output`) d’entiers, chaînes, blocs, listes/dicts selon un protocole binaire. Fournit `SIZEOF_LONG` et `output_array_access` pour les tables indexées.
- `output.py` — Pont vers la sortie configurée: écrit en‑têtes et corps via `conf.output_conf`.
- `json_converter.py` — Conversions JSON pour l’échange et le débogage.

## Événements et données

- `event.py` — Comparaison/tri d’événements. Détermine l’ordre logique (naissance avant décès, etc.) et trie selon date puis type via `sort_events`.
- `futil.py` — Fonctions de mapping d’événements/personnes/familles: remap de champs et transformation des noms (génériques) avec éventuelle conversion de dates.
- `hasher.py` — Construction d’empreintes (SHA256) à partir des structures `gwdef`: feeders dédiés pour événements et champs.
- `notes_links.py` — Gestion des notes et liens (association et nettoyage).

## Utilitaires généraux

- `util.py` — Fonctions variées pour UI et logique (traductions `transl`, helpers HTML, chemins `etc`, opérations sur listes/chaînes, formats pour événements). Sert de couche utilitaire transversale.
- `mutil.py` — Utilitaires de chaînes; support de normalisation.
- `loc.py` — Références de provenance pour messages/erreurs.
- `lock.py` — Verrouillage basique de fichiers.
- `collection.py`, `buff.py`, `pqueue.py`, `gutil.py` — Structures et utilitaires complémentaires (buffers, files de priorité, parcours/tri).

## Différences, compatibilité et compression

- `difference.py` — Diff de séquences (type Myers) pour comparer tableaux/structures.
- `compat.py`, `geneweb_compat.py` — Aides de compatibilité avec formats GeneWeb et vieux schémas.
- `my_gzip.py` — Lecture/écriture Gzip.
- `my_unix.py` — Aides Unix (spécifiques plateforme).

## Couche web et daemon

- `wserver.py` — Squelette de serveur web et handlers génériques.
- `wserver_util.py` — Utilitaires de réponse/rendu.
- `modernProject/bin` — Scripts de démarrage et de routage (si présents dans le dépôt).

## Affichage et UI

- `templ.py` — Moteur de templates.
- `ast.py` — AST de templates (nœuds et validations).
- `progr_bar.py` — Affichage de progression.

## Notes de fonctionnement

- Ouverture de base: passer par `with_database(bname, k)` qui vérifie la version via les magic numbers et construit les accès disque.
- Patches: chargés via `input_patches` (avec vérification du magic `MAGIC_PATCH`) et engagés par `commit_patches` en écrivant `patches` de manière atomique.
- Synchro: `input_synchro` lit `synchro_patches` et renvoie une structure `SynchroPath` (vide en cas d’erreur).
- Index nom/prénom: produits dans `outbase.py` (création des inx/dat) et consommés par `database.py` via `persons_of_surname`/`persons_of_first_name` selon la `BaseVersion`.
- Fichiers: `secure` garantit les chemins, `filesystem` gère permissions/mouvements.
- Sérialisation: `iovalue` encode/décode les structures selon un protocole binaire dédié.
