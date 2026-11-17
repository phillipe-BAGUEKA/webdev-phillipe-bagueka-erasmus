# MCP — finalisation et état de la validation client

## Périmètre et état initial

Départ `524370db1f0b4e7b89d6c291d3ecda2fcc37851a`, arbre propre ; trois commits
MCP locaux, sans divergence après fetch d'origin/main. Aucune sous-étape métier
reconstruite, aucune rotation répétée. Publication normale autorisée après
contrôles/revue. SQLite, démonstration et instance 5432 restent hors des mutations.

## Client réellement disponible : Gemini CLI 0.65.0

Version relevée dans le package installé `@google/gemini-cli/package.json`.
Code local inspecté : `bundle/gemini-GLQ4MVLB.js`, commande CLI `mcp list` ;
documentation embarquée `bundle/docs/tools/mcp-server.md`, sections configuration,
`cwd`, `env` et sanitization. Le client retire les variables sensibles héritées
sauf celles explicitement déclarées dans le bloc `env` : le placeholder
`LAB_BOOKING_MCP_SESSION` est donc nécessaire, sans jamais stocker sa valeur.

`.gemini/settings.json` conserve la lecture d'AGENTS.md et configure :

- commande Windows `.venv/Scripts/python.exe` ; arguments
  `mcp-server/server.py --project` ; répertoire `.` depuis la racine du dépôt ;
- `DJANGO_SETTINGS_MODULE=src.config.postgres`, explicite ;
- `LAB_BOOKING_MCP_SESSION=$LAB_BOOKING_MCP_SESSION`, placeholder uniquement ;
- aucune approbation automatique ni option qui saute les confirmations.

Pour un autre système, adapter le chemin de la venv (`.venv/bin/python`). Cette
configuration Windows n'est pas le lanceur TP1 de package.json, laissé inchangé.

## Observation réelle, sans fournisseur ni session personnelle

Le vrai point d'entrée installé de Gemini CLI a exécuté `mcp list` dans un
domicile et une configuration de diagnostic isolés sous `.local/mcp-client-probe/`.
Une copie de la configuration du projet utilise le répertoire absolu du dépôt,
équivalent au `.` de la configuration normale lancée depuis cette racine.
Fichiers `.env` de diagnostic vides, domiciles/configurations personnelles non
chargés, variable de session **factice** créée uniquement dans l'environnement
enfant. Le serveur démarre le vrai profil de développement PostgreSQL mais aucun
outil métier n'est appelé ; aucune donnée de démonstration n'est modifiée.

Un garde Node bloque HTTP(S), sockets et fetch externe ; seules les URL `data:`
embarquées en mémoire restent permises. Reçu final sans valeur sensible :
`.local/mcp-client-probe/summary.json`. Résultats réellement observés :

- retour CLI **0**, `my-project … (stdio) - Connected` ;
- processus Python de la venv, bon répertoire, réglage `src.config.postgres` ;
- transfert du jeton factice confirmé par comparaison en mémoire, sans valeur
  dans les arguments, sorties ou fichiers ;
- serveur stdout exclusivement JSON-RPC, stderr vide ;
- méthodes relevées : `initialize`, `notifications/initialized`, `ping` ;
- **0 tentative réseau externe**, **0 lecture de .env personnel**, **0 fuite du
  jeton factice** dans les sorties.

Échecs de diagnostic conservés honnêtement : chemin Windows du garde à corriger,
premier dossier isolé non approuvé puis approuvé dans son seul domicile de test,
blocage initial d'une ressource `data:` locale par le garde trop strict. Un
prototype de wrapper Python a expiré avec remplacement de processus, puis avec
un relais enfant. La commande directe de la venv s'est connectée. Ce prototype
et ses tests sont conservés comme textes ignorés sous `.local`, hors livraison ;
aucun wrapper n'est ajouté à l'application. Les sources métier restent inchangées.

## Ce que cette preuve ne valide pas

`gemini mcp list` vérifie la connexion ; son implémentation n'envoie pas
`tools/list` ou `tools/call`. Les sous-commandes CLI disponibles gèrent les
serveurs, sans commande d'invocation directe d'un outil identifiée. Les commandes
interactives `/mcp list/desc/schema` existent mais leur parcours agent n'a pas été
initialisé ici. L'utilisation d'un outil par un prompt demanderait un parcours
modèle ; cet essai est arrêté conformément à l'interdiction de fournisseur.

Aucune disponibilité/historique réel n'a donc été consulté via Gemini, aucune
création/annulation démo effectuée, aucune confirmation de poste/créneau demandée.
Pas de clé personnelle récupérée ni de cookie lu. Un lanceur client à saisie
masquée n'est pas nécessaire au simple healthcheck : il reste à préparer et
valider avant une future remise réelle, lorsqu'un parcours d'appel est autorisé.
Ne pas confondre le diagnostic réel Gemini avec les clients stdio des tests.

## AC-37, AC-38, AC-39 : preuves et limites

- **AC-37** : les tests stdio réels découvrent les six outils et leurs schémas,
  avec descriptions ≥20 caractères. Gemini healthcheck n'est pas une preuve de
  découverte des outils dans le client final.
- **AC-38** : tests paramétrés des quatre outils, sessions absentes/inconnues,
  expiration/activité/hash et révocation dans un même processus ; refus sans
  données/mutation. Vraie session personnelle dans Gemini non testée.
- **AC-39** : consultations et 14 cas de création/8 d'annulation comparés à HTTP
  depuis des états métier équivalents, CSRF réel, services partagés et assertions
  en base. Couverture de ces scénarios, pas de tout comportement possible ni de
  nouveaux ordonnancements concurrents MCP. Concurrence des services conservée.

## Contrôles et CI

Les commandes existantes `npm test`, `tools/check_coverage.py --postgresql`,
le contrôle MCP TP1 et ex2 sont conservées. La CI existante prépare déjà
PostgreSQL éphémère avec rôle limité et migrations depuis zéro. `npm test`
exécute tous les tests Python, donc les vrais tests stdio/projet et de parité,
puis le guard SQLite isolé, TP1 et Node. Aucun job n'est désactivé.

Seule adaptation CI : `PYTEST_ADDOPTS=-rA` dans le job test rend les noms AC et
tests réellement exécutés visibles dans ses logs. Le `--tb=short` du fichier
pytest.ini reste actif. Couverture : services 100 % lignes/branches, global
Python ≥80 %, TP1 et tout l'inventaire conservés, aucune exclusion modifiée.
Le job mcp reste le contrôle du mode TP1 autonome, pas une preuve du mode projet.

Le premier contrôle local, pendant le prototype non livré, a réussi ses 415 tests
et TP1, mais comptait aussi des artefacts de diagnostic : il ne sert pas de mesure
du périmètre publié. Les résultats locaux finaux et distants sont ajoutés après
leur exécution effective, sur le SHA réellement publié.

Contrôle local final sur le périmètre retenu : **411 tests PostgreSQL réussis,
1 guard SQLite désélectionné**, puis **9 tests TP1 réussis**. Services
**227/227 lignes et 76/76 branches (100 %)** ; global **1438/1524 lignes
(94,36 %)** et **342/378 branches (90,48 %)** ; adaptateur projet **90/90 lignes,
30/30 branches**. Rapport ignoré :
`.local/coverage/03682cbfb4df40b4a35085dc211c8d00/coverage.json`.
**23 tests Node**, MCP **12/12**, ex2 **32/32** réussis. Le guard SQLite est aussi
exécuté séparément avant publication, sans toucher la base de démonstration.
L'avertissement coverage du test TP1 `-S` sans site-packages reste attendu ; le
serveur TP1 est réellement couvert par les autres sous-processus.

Revue indépendante avant publication : aucun problème significatif, aucun
constat retenu ou écarté, aucune correction demandée. Guard SQLite séparé :
**1 réussi** ; contrôle Django sans problème, diff propre. La revue ne remplace
ni la note/revue personnelles reportées, ni les essais du client final.

## Publication réellement vérifiée

Les trois commits MCP et la finalisation ont été publiés normalement, sans
force-push, au SHA `365b52b4ff12aad7a725e84b025ae763707a3d57`.
[Exécution CI de ce SHA](https://github.com/phillipe-BAGUEKA/webdev-phillipe-bagueka-erasmus/actions/runs/44080856587) :

| Job | Résultat observé |
| --- | --- |
| [test](https://github.com/phillipe-BAGUEKA/webdev-phillipe-bagueka-erasmus/actions/runs/44080856587/job/134030755944) | Réussi : 411 tests PG, 1 désélection SQLite rejouée séparément (1 réussi), 9 TP1 et 23 Node. Titres AC-37, quota AC-20/39, propriétaire AC-27/39 et révocation AC-38 présents dans les logs des tests stdio réels. |
| [coverage](https://github.com/phillipe-BAGUEKA/webdev-phillipe-bagueka-erasmus/actions/runs/44080856587/job/134030755170) | Réussi : services 227/227 lignes, 76/76 branches ; global Python 1439/1524 lignes (94,42 %), 343/378 branches (90,74 %), TP1 et inventaire inclus. JS chargé par les tests : 98,18 % lignes, 90,91 % branches, pas une couverture visuelle complète. |
| [mcp](https://github.com/phillipe-BAGUEKA/webdev-phillipe-bagueka-erasmus/actions/runs/44080856587/job/134030758257) | Réussi : contrôle TP1 autonome 12/12. Le mode projet est testé dans test/coverage, pas dans ce job autonome. |
| [spec](https://github.com/phillipe-BAGUEKA/webdev-phillipe-bagueka-erasmus/actions/runs/44080856587/job/134030755621) | Réussi : ex2 32/32, pas une acceptation professorale ni un ex3 vert. |

Les jobs test/coverage montrent zéro table publique avant les migrations,
application de 0001/0002/0003, base/rôle dédiés sur 5433 et flags superuser,
createdb, createrole faux. Aucun job ignoré ; seule l'étape Docker est ignorée
par sa condition existante (pas de Dockerfile). Aucun correctif de CI nécessaire.
Ces preuves concernent **ce SHA précis**. Le commit documentaire qui consigne
ce tableau doit aussi recevoir une vérification CI indépendante ; son résultat
n'est pas présumé à partir de celui-ci.

## Points ouverts après publication

Validation client des outils et remise masquée réelle ; note/revue personnelles
du professeur ; vérifications UI reportées (380 pixels explicitement non validé) ;
fonctionnalité IA absente et son futur plan, Google/personnel/déploiement selon le
calendrier projet. L'ambiguïté entre exigences conditionnelles du TP3 et heuristiques
du contrôle ex3 reste à confirmer avec le professeur ; aucun ex3 vert n'est
déduit de la présence des outils. La publication MCP ne clôt pas le Lab 03.
