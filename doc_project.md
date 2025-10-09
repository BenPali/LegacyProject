texte Q/A généré par chatgpt sur la base des attentes de l'ancien projet Legacy Cobol:
🔹 1. Contexte & enjeux
Q1. Pourquoi le code legacy est-il un défi majeur pour les entreprises ?
 👉 Parce qu’il est souvent en production depuis longtemps, critique pour le business, mais difficile à maintenir (manque de documentation, technologies obsolètes, dépendance aux rares experts). Le moindre bug peut causer une panne coûteuse.
Q2. Quels étaient les risques du projet si la migration n’était pas bien faite ?
 👉 Risque de rupture de service, perte de données, indisponibilité de l’application, insécurité (failles non corrigées), incapacité à répondre à de nouveaux besoins métiers.

🔹 2. Approche méthodologique
Q3. Comment avez-vous abordé la migration du COBOL vers Python ?
 👉 D’abord comprendre le fonctionnement du code (lecture, documentation, tests existants), puis recoder module par module en Python, tout en gardant des tests comparatifs avec la version COBOL pour vérifier l’équivalence des résultats.
Q4. Pourquoi avoir choisi Python pour moderniser le projet ?
 👉 Python est plus lisible, moderne, largement documenté, compatible avec de nombreux outils (tests, CI/CD, sécurité). C’est un langage accessible qui facilite la maintenance et l’évolutivité.
Q5. Comment avez-vous géré la continuité du service pendant la migration ?
 👉 En travaillant sur une version parallèle (sandbox), sans toucher à la prod. On a comparé les résultats COBOL vs Python. Une fois validé, on a prévu un déploiement progressif et contrôlé.

🔹 3. Qualité & fiabilité
Q6. Quelles difficultés avez-vous rencontrées en traduisant du COBOL en Python ?
 👉 Syntaxe très différente, paradigme procédural vs objet, gestion des types stricts en COBOL vs dynamiques en Python. La principale difficulté : comprendre la logique métier derrière le code.
Q7. Comment avez-vous garanti que le nouveau code fonctionnait comme l’ancien ?
 👉 Mise en place de tests unitaires et de tests d’intégration. Comparaison systématique des outputs COBOL et Python avec les mêmes jeux de données. Automatisation avec pytest.
Q8. Quelle était votre stratégie de tests ?
 👉 Stratégie en 3 niveaux :
Tests unitaires pour chaque fonction.


Tests d’intégration pour vérifier la cohérence entre modules.


Tests de régression pour comparer les résultats COBOL/Python.



🔹 4. Documentation & collaboration
Q9. Comment avez-vous documenté votre travail ?
 👉 Documentation technique (comment le code fonctionne, choix faits), documentation utilisateur (comment lancer le programme, dépendances, exemples). Utilisation de docstrings Python + README + schémas de flux.
Q10. Quel rôle a joué GitHub Copilot dans votre projet ?
 👉 Copilot a aidé à accélérer la traduction et générer du squelette de code, mais nous avons toujours validé, corrigé et testé les propositions. L’IA est un outil d’aide, pas une garantie.
Q11. Comment avez-vous travaillé en équipe ?
 👉 Répartition des modules, usage de Git/GitHub (branches, pull requests, code reviews). On s’est synchronisés régulièrement pour harmoniser les choix techniques et éviter les divergences.

🔹 5. Mise en production
Q12. Quelles précautions avant de mettre le code en production ?
 👉 Vérifier que tous les tests passent, audit de sécurité (dépendances Python à jour), mise en place d’un environnement de staging pour tester la charge, prévoir un rollback possible en cas d’échec.
Q13. Comment assurer la maintenabilité du code dans le futur ?
 👉 Code clair, documenté, testé. Respect des standards (PEP8, conventions de nommage). Ajout de CI/CD pour tester automatiquement chaque changement futur.

🔹 6. Vision & recul
Q14. Que t’a appris ce projet sur la gestion du legacy ?
 👉 L’importance de la compréhension métier avant de toucher au code, la rigueur dans les tests, et le fait que moderniser ne veut pas dire tout réécrire, mais savoir conserver la valeur existante.
Q15. Si tu devais refaire le projet, que changerais-tu ?
 👉 Peut-être plus de temps sur la cartographie initiale du code COBOL (comprendre les flux métiers). Et dès le début, mettre en place une suite de tests automatisés pour gagner du temps ensuite.

✅ Astuce pour l’oral :
Ne jamais rentrer dans les détails techniques trop complexes (ils ne demandent pas ton code exact).


Toujours ramener ta réponse à : continuité de service, qualité du code, tests, documentation, mise en prod sécurisée.




Nouveau project AWKWARD LEGACY:
AWKWARD LEGACY _ < CHANGE DE PAST, TEST THE PRESENT, SECURE THE FUTURE /> AWKWARD LEGACY language: Python compilation: via Makefile, including re, clean and fclean rules Legacy-OCaml: https://github.com/geneweb/geneweb ✓ The totality of your source files, except all useless files (binary, temp files, obj files,...), must be included in your delivery. The company CoinLegacy Inc., specialized in software reverse engineering, has just acquired code from an old software suite developed between 1995 and 2008. These tools, written in Ocaml language, should contain a program capable of revealing the origins of each individual. You are a team of the CoinLegacy Inc. Agency. A major client has entrusted you with this ancient code. It is a remnant that could be worth its weight in gold. With this program, we could uncover the rightful heirs of powerful lineages — and pocket a small fee for our efforts. Your mission: Your task is to make this code compliant with current standards. But be careful — this is a piece of history. You have to restore it, test it, deploy it in a secure manner, without altering its core, or risk the collapse of the entire infrastructure. Be vigilant and meticulous. Obviously, rewriting or destroying it is out of the question — doing so would get you fired. Good luck, and stay sharp! 1 Competencies needed ”Quality assurance – Project management” To do so, you will need to: Develop a documented testing policy Define standards and quality processes To make the code usable, you will need to provide us with: Your technical deployment expertise As well as create documentation to guide the deployment of the software solution 2 Render Your project defense will take place between October 20 and 24 Your final report must cover the following aspects Test policy: - Integration of the quality process throughout the project lifecycle - Definition of test protocols and scenarios (unit, functional, integration, performance) - Error detection and handling of malfunctions - Result analysis and test reporting - Security auditing and vulnerability management Standards and quality processes: ✓ Definition of documentation standards, coding conventions, and activity reporting ✓ Consideration of accessibility for people with disabilities ✓ Implementation of quality control activities Your technical deployment expertise: ✓ Provisioning of the necessary resources for project deployment (servers, cloud services, etc.) ✓ Compliance with system and network administration best practices (password management, network and machine configuration to prevent vulnerabilities, encryption keys, etc.) Create documentation to guide the deployment of the software solution: ✓ Awareness of security best practices ✓ Ensuring compliance with data protection regulations (GDPR) ✓ Delivery strategy ✓ Communication with various departments of the organization (sales, marketing, operations, etc.) ✓ Documentation of processes ✓ Clear and intelligible technical communication 3 v 1


Pour le projet Legacy, il s'agit plus d'une adaptation. On veut que vous apportiez de bonnes méthodes, que vous modernisiez le projet en langage Python. Nous ne souhaitons pas que vous altériez le projet. Cela signifie que vous devez conserver les features tout en adaptant au nouveau langage et aux bonnes pratiques. 
Est ce que le projet ou une partie est utilisée en externe ? Si oui, quel serait l'impact de vos modifications ? Est-ce-que c'est réellement voulu ?
 
Vous aurez pas mal de documentation à rédiger tout au long du projet.
 
Nous allons vous évaluer sur les points suivants :  
 
QA - Quality assurance : 
Doc de la stratégie QA
Présentation de la doc
Accessibilité
Préconisations 
Preuves d'implem (report, artifact, ticket etc...)
Mettre un point d'honneur sur la sécurité
Il faudra expliquer et justifier votre stratégie
Test
Protocoles 
Scenari
Implémentation
Documentation
Défendre vos choix
Explain the components
 
Projet :
Présenter le document concernant l'hébergement et le déploiement de la solution en fonction des besoins
Justifier vos choix en fonction des attentes et moyens du client
Procédure détaillant l'implémentation
Démonstration : du déploiement au fonctionnement
Démontrer que vous avez travaillé sur la sécurité du projet
Documentation technique (architecture, techno, implémentation) argumenté
Défendre vos choix techniques
Gestion de projet et preuve d'échanges réguliers
Chaque membre de l'équipe doit être en mesure de s'exprimer clairement et de défendre les choix liés au projet.
Les documents réalisés doivent également être professionnels et accessibles.
 
Quoi qu'il arrive, il s'agit ici d'une première évaluation. Nous sommes conscients que vous n'aurez pas tout, à vous de vous organiser de votre côté de la manière qui vous semble la plus adaptée. Le plus vous présentez d'éléments, le plus de retours on pourra vous faire.

