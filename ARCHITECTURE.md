# Architecture de GeneWeb - Analyse pour refactorisation Python

## Vue d'ensemble

GeneWeb est un logiciel de généalogie open source écrit en OCaml qui fournit une interface web pour gérer des bases de données généalogiques. Il peut fonctionner hors ligne ou comme service web.

## Structure du projet

### 1. **Organisation générale**

```
geneweb/
├── bin/           # Exécutables principaux
├── lib/           # Bibliothèques centrales
├── plugins/       # Extensions modulaires
├── hd/            # Ressources web (HTML, CSS, JS)
├── rpc/           # Service RPC JSON
├── test/          # Tests unitaires et d'intégration
└── docker/        # Configuration Docker
```

## Composants principaux

### 2. **Exécutables (bin/)**

#### **2.1 Serveur principal - gwd**
- **Rôle** : Serveur HTTP principal qui gère les requêtes web
- **Fonctionnalités** :
  - Authentification (Basic, Digest, Token)
  - Gestion des sessions et timeouts
  - Pool de workers pour traitement parallèle
  - Support des plugins dynamiques
  - Gestion du cache

#### **2.2 Outils de manipulation de base**
- **gwb2ged** : Conversion base GeneWeb → GEDCOM
- **ged2gwb** : Conversion GEDCOM → base GeneWeb
- **gwc** : Compilateur de bases
- **gwu** : Utilitaire de mise à jour
- **consang** : Calcul de consanguinité
- **connex** : Vérification de connexité
- **gwfixbase** : Réparation de bases

#### **2.3 Interface de configuration**
- **gwsetup** : Interface web de configuration des bases
- **setup** : Module de configuration initial

### 3. **Bibliothèques centrales (lib/)**

#### **3.1 Modèles de données (def/)**
- **def.ml** : Types de base (personnes, familles, événements)
- **adef.ml** : Types avancés et encodages

#### **3.2 Base de données (db/)**
- **database.ml** : Interface abstraite de base de données
- **dbdisk.ml** : Implémentation sur disque
- **driver.ml** : Système de pilotes pour différents backends
- **collection.ml** : Collections et index
- **avl.ml** : Arbres AVL pour indexation
- **iovalue.ml** : Sérialisation/désérialisation

#### **3.3 Utilitaires (util/)**
- **calendar.ml** : Gestion des calendriers (Grégorien, Julien, Hébreu, etc.)
- **date.ml** : Manipulation des dates
- **name.ml** : Gestion des noms et particules
- **utf8.ml** : Support Unicode
- **secure.ml** : Fonctions de sécurité
- **lock.ml** : Verrous pour accès concurrent

#### **3.4 Affichage et templates**
- **templ/** : Moteur de templates
  - Parser et lexer pour langage de templates
  - AST et interpréteur
- **perso.ml** : Affichage des personnes
- **family.ml** : Affichage des familles
- **dateDisplay.ml** : Formatage des dates

#### **3.5 Fonctionnalités métier**

##### **Recherche et navigation**
- **searchName.ml** : Recherche par nom
- **advSearchOk.ml** : Recherche avancée
- **alln.ml** : Liste de tous les noms

##### **Généalogie**
- **relation.ml** : Calcul de relations
- **cousins.ml** : Recherche de cousins
- **dag.ml** : Graphes acycliques dirigés pour arbres
- **sosa/** : Numérotation Sosa-Stradonitz

##### **Statistiques et analyses**
- **birthDeath.ml** : Statistiques naissances/décès
- **birthday.ml** : Anniversaires
- **stats.ml** : Statistiques générales

##### **Édition et fusion**
- **updateInd.ml** : Mise à jour d'individus
- **updateFam.ml** : Mise à jour de familles
- **mergeInd.ml** : Fusion d'individus
- **mergeFam.ml** : Fusion de familles

##### **Import/Export**
- **wiki.ml** : Format Wiki
- **notes.ml** : Gestion des notes
- **image.ml** : Gestion des images

### 4. **Plugins (plugins/)**

#### **4.1 Système de plugins**
- Architecture modulaire permettant l'extension des fonctionnalités
- Chargement dynamique au démarrage
- API standardisée pour l'intégration

#### **4.2 Plugins disponibles**
- **export** : Export de données avancé
- **forum** : Forum de discussion intégré
- **fixbase** : Outils de réparation étendus
- **gwxjg** : Export JSON et API REST
- **jingoo** : Moteur de templates Jingoo
- **xhtml** : Génération XHTML strict
- **cgl** : Cousins German List
- **no_index** : Désactivation de l'indexation

### 5. **Interface web (hd/)**

#### **5.1 Assets statiques**
- **css/** : Bootstrap, DataTables, styles personnalisés
- **js/** : jQuery, visualisations (fanchart), interactions
- **images/** : Icônes et images du thème
- **webfonts/** : Polices personnalisées

#### **5.2 Templates**
- **etc/** : Templates HTML principaux
- **templm/** : Templates modulaires
- **modules/** : Composants réutilisables

### 6. **Service RPC (rpc/)**

#### **6.1 Architecture**
- **server/** : Serveur JSON-RPC
- **lib/** : Bibliothèque RPC partagée
  - Encodage/décodage JSON
  - Définition des services
  - Gestion des routes

#### **6.2 Fonctionnalités**
- API REST/JSON pour intégration externe
- Support WebSocket pour temps réel
- Authentification et autorisation

## Flux de données

### 7. **Pipeline de traitement**

```
Requête HTTP → gwd (serveur)
    ↓
Authentification
    ↓
Routing (plugin ou core)
    ↓
Base de données (lecture/écriture)
    ↓
Traitement métier
    ↓
Template rendering
    ↓
Réponse HTML/JSON
```

## Points clés pour la refactorisation Python

### 8. **Défis principaux**

#### **8.1 Typage statique**
- OCaml utilise un typage statique fort
- Python nécessitera des dataclasses et typing hints

#### **8.2 Performance**
- OCaml compile en code natif
- Python nécessitera :
  - Cython pour parties critiques
  - Cache agressif (Redis)
  - Optimisations algorithmiques

#### **8.3 Concurrence**
- OCaml utilise des processus légers
- Python : asyncio ou multiprocessing

#### **8.4 Templates**
- Système de templates custom
- Migration vers Jinja2 recommandée

### 9. **Architecture cible Python suggérée**

```
geneweb-python/
├── core/              # Modèles et logique métier
│   ├── models/        # Dataclasses (Person, Family, etc.)
│   ├── database/      # ORM ou interface DB
│   └── genealogy/     # Algorithmes généalogiques
├── web/               # Application web
│   ├── app.py         # FastAPI/Flask app
│   ├── auth/          # Authentification
│   ├── api/           # Endpoints REST
│   └── templates/     # Jinja2 templates
├── plugins/           # Système de plugins
│   └── base.py        # Interface de plugin
├── utils/             # Utilitaires
│   ├── calendar.py
│   ├── date.py
│   └── name.py
└── cli/               # Outils ligne de commande
    ├── import_export.py
    ├── database.py
    └── analysis.py
```

### 10. **Technologies Python recommandées**

#### **Backend**
- **Framework web** : FastAPI (async, moderne, typage)
- **ORM** : SQLAlchemy 2.0 ou Tortoise-ORM
- **Base de données** : PostgreSQL avec JSONB pour flexibilité
- **Cache** : Redis pour performances
- **Queue** : Celery pour tâches asynchrones

#### **Frontend**
- **Templates** : Jinja2
- **Assets** : Webpack ou Vite
- **API** : GraphQL avec Strawberry (optionnel)

#### **Outils**
- **Typage** : mypy, pydantic
- **Tests** : pytest, hypothesis
- **Documentation** : Sphinx, mkdocs

### 11. **Plan de migration suggéré**

#### **Phase 1 : Core**
1. Modèles de données (dataclasses)
2. Parseur GEDCOM
3. Interface base de données

#### **Phase 2 : API**
1. Endpoints REST basiques
2. Authentification
3. Recherche et navigation

#### **Phase 3 : Interface web**
1. Templates de base
2. Affichage personnes/familles
3. Navigation dans l'arbre

#### **Phase 4 : Fonctionnalités avancées**
1. Édition et fusion
2. Statistiques
3. Système de plugins

#### **Phase 5 : Optimisation**
1. Cache et performance
2. Scalabilité
3. Tests de charge

## Conclusion

GeneWeb est une application complexe avec une architecture modulaire bien pensée. La refactorisation en Python nécessitera une attention particulière aux performances et au typage, mais bénéficiera de l'écosystème Python moderne pour le web et l'analyse de données.

Les principaux avantages de la migration Python :
- Écosystème plus large
- Facilité de déploiement
- Intégration avec outils data science
- Communauté plus active

Les défis à anticiper :
- Performance (mitiger avec cache et optimisations)
- Typage (utiliser intensivement typing et pydantic)
- Compatibilité ascendante des données