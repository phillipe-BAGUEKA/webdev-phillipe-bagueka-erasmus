# Préparation de clôture Lab 03 — aucun quitus

17 novembre 2026, départ publié `c96aa2ecebcc5821c11d61928fc2d194102f0592`.
Arbre Git initial propre. Documentation préparée par Codex ; décisions de
l'utilisateur conservées, compréhension et revue personnelles non validées.
Aucun code, test, vérificateur, CI, critère approuvé ou fonctionnalité modifié.
Aucun commit/push, fournisseur, clé réelle, installation, facturation ou Lab 04.

Le 19 novembre, Codex a repris le contrôle UI reporté. Connexion et réservation
ont été observées dans Edge à 380, 768 et 1280 px CSS sur données synthétiques.
La correction stabilise les trois listes asynchrones. Le tableau de mesures
et les limites figurent dans [UI.md](UI.md). AC-42 reste partiel. Les résultats
de préparation du 17 novembre ci-dessous sont conservés comme historique.

## Lecture des consignes actuelles

Lecture Web en échec ; les deux pages officielles ont été récupérées par curl
et lues le 17 novembre. Copies ignorées sous `.local/*-current-closure.html` et
`.txt`. Les constats suivants se fondent sur ces pages, pas uniquement sur les
anciens bilans. Les commandes destructrices données en exemple dans le cours
ne sont pas exécutées ; les changements et données locaux restent préservés.
Le projet impose SPEC et AGENTS ; ce guide et les autres guides de jalons sont
des aides documentaires/pédagogiques, pas des livrables supplémentaires imposés.

| Source et passage | Conséquence pour cette clôture |
| --- | --- |
| [Lab 03 — Goal, What you build, What the assistant checks](https://webdev-course.tu-sofia.workers.dev/en/resources/exercises/3/) : « Every criterion this feature implements » et conditions sur modèle/MCP. | Le Lab porte sur une fonctionnalité complète et les critères qu'elle réalise ; migration, règles/service, API, autorisation, UI, refus et preuves sont à examiner ensemble. |
| [Lab 03 — Steps, Run the self-check](https://webdev-course.tu-sofia.workers.dev/en/resources/exercises/3/) : « Every check must pass ». | Le même énoncé demande ex3 vert ; le script inspecte tous les AC de SPEC. Tension à soumettre au professeur, pas une dispense décidée par Codex. |
| [Lab 03 — Steps, Working with the agent](https://webdev-course.tu-sofia.workers.dev/en/resources/exercises/3/) : « Write the architecture note yourself ». | Note, choix des critères, lecture du diff et commits sont attribués à l'étudiant. Les adaptations assistées/déléguées restent à faire confirmer. |
| [Projet — The requirements, exactly ; 3 ; 4 ; 5 ; 7 ; When you build which part](https://webdev-course.tu-sofia.workers.dev/en/guides/project/) : « built where they fit », « the UI is finished for Exercise 4 ». | Le projet final exige deux connexions, modèle, MCP, UI complète et traçabilité. Le calendrier répartit leur réalisation ; il n'impose pas tous ces écrans au seul Lab 03. |

Le Lab 03 demande explicitement des tests modèle avec faux client. Aucun passage
consulté n'impose explicitement un appel Google réel pendant ce Lab. Cela ne
prouve ni accès effectif ni conformité d'usage : la fonctionnalité doit réellement
fonctionner pour l'acceptation finale. Le rôle exact d'un essai client MCP final
dans la réception du Lab reste à confirmer ; les services/session ordinaires et
la parité automatisée sont établis, pas la remise réelle à Gemini.

## 1 — Commande npm : condition et preuves

Dans `checks/ex3.mjs`, package.json déclare scripts.test : le chemin réellement
choisi appelle `run('npm', ['test'])`, puis exige `code === 0`.
`checks/lib.mjs::run` utilise `execFileSync`, `shell:false`, timeout 180 000 ms.
Il ne choisit pas npm.cmd et n'utilise pas le shell PowerShell.

Observation locale actuelle : `node checks/ex3.mjs` sort 1, affiche 15/18 et
`spawnSync npm ENOENT`. Node est Windows ; la commande interactive npm est
fournie par npm.ps1/npm.cmd. Le shell sait la lancer, pas ce chemin du vérificateur.
L'échec précède les tests : il ne constitue pas un test applicatif échoué.

Environnement compatible réellement vérifié : [job test Ubuntu du SHA c96aa2e](https://github.com/phillipe-BAGUEKA/webdev-phillipe-bagueka-erasmus/actions/runs/44138794766/job/134235547443).
Logs relus : système Ubuntu, étape « Run npm test », puis
`node tools/run_tests.mjs`, 545 PostgreSQL réussis/1 désélection, garde SQLite
réussie séparément, 9 TP1 et 42 Node. PostgreSQL prend 82,97 s ; cette étape
complète dure environ 85 s. C'est une **suite npm réussie sous Linux**, pas
une exécution d'ex3 Linux ni un résultat 18/18.

Inventaire WSL local en lecture seule : seule distribution docker-desktop
listée ; aucune distribution de travail du cours préparée. Elle n'est pas
utilisée pour des essais improvisés. Aucun environnement installé ou lancé.
On réutilise la preuve CI sur le code publié inchangé, sans nouvelle CI.

Reste : utiliser le vérificateur officiel dans l'environnement de remise et
faire reconnaître l'incompatibilité Windows. Le timeout 180 s demeure : les
tests PG Windows avaient pris 206,01 s lors de la finalisation antérieure.
Ni wrapper remplaçant npm, ni copie du vérificateur, ni contrôle affaibli.

## 2 — Traçabilité : condition et corrections documentaires

Condition exacte : `ids.length > 0 && untested.length === 0`. `ids` vient des
AC présents sous Acceptance criteria de SPEC, y compris ses références groupées.
`testFiles('.')` parcourt les noms usuels de tests jusqu'à la profondeur 5.
Le script concatène leurs **sources**, puis calcule pour chaque identifiant
`!testText.includes(id)`. Il ne collecte pas pytest et ne vérifie pas d'assertion.

Échec actuel : AC-45, AC-5/6/7/8/9/10/12, AC-43/44. AC-1 peut être masqué par
AC-11, AC-2 par AC-20, AC-3 par AC-33, AC-4 par AC-40. Ce sont des correspondances
textuelles, pas des tests Google. Le script reste inchangé.

Méthode plus précise employée ici : collecte pytest réelle sans exécution,
extraction des identifiants avec borne après le nombre ; lecture des tests,
titres Node réellement exécutés et bilans des observations existantes. Résultat :
546 cas Python collectés ; aucun titre Python AC-1 à AC-10, AC-12 ou AC-43 à
AC-45 ; ces IDs n'apparaissent pas non plus dans les 42 titres Node exécutés.
AC-11, AC-13 à AC-42 et AC-46 à AC-49 ont au moins un titre Python exact.

`SPEC.md::Traceability` contient désormais une ligne par AC-1 à AC-49, avec noms
réels, assertions visées et portée. Les formulations approuvées restent intactes.
Les tests directs, HTTP Django, stdio réel, DOM simulé et navigateur sont distingués.
Les raccourcis antérieurs sont remplacés, sans créer de test ni greffer un ID.

Restes réels :

- AC-1 à AC-4 : Google/liaison absents. AC-5 à AC-10 et AC-12 : gestion du personnel
  absente ; un seed ou un poste mis hors service dans une fixture ne la prouve pas.
- AC-40 : navigation actuelle seulement partielle, espaces compte/personnel absents.
- AC-42 : le titre Python vérifie le template. Les parcours étudiant et connexion
  ont été observés dans Edge à 380, 768 et 1 280 px CSS, avec le refus de
  connexion vérifié à 380 px. Les autres états et écrans finaux gardent le
  critère partiel. Voir [UI.md](UI.md) pour les mesures effectuées par Codex.
- AC-43/44 : clavier/palette/titres partiellement observés, pas le parcours/audit
  entier. AC-45 : jetons inspectés, pas de titre automatisé ni audit exhaustif.
- AC-29 à AC-39 : preuves hors fournisseur et sessions synthétiques fortes mais
  aucune qualité/connexion Google ou validation du client MCP final déduite.

Le déficit documentaire est corrigé ; les déficits fonctionnels/visuels ne sont
pas résolus par la table. Ex3 reste rouge. Faire préciser au professeur comment
traiter les critères finaux conservés dans SPEC pour la réception de cette tranche.

## 3 — Note personnelle : condition exacte, préparation seulement

Condition du code : `answered(section(spec, 'Architecture')).length >= 3`
**ou** `findFile('docs', name => /feature/i.test(name))`. La première voie compte
des lignes de réponse hors commentaire/étiquette ; la seconde se contente d'un
nom de fichier. Ni l'une ni l'autre ne juge la qualité ou l'auteur du texte.
Actuellement la section ne contient qu'un commentaire et aucun fichier ne remplit
l'autre voie. Le cours demande une note personnelle d'environ une demi-page.

**Ne rien copier de ce guide comme note.** SPEC/Architecture est laissée vide.
Ce guide n'est pas nommé feature-3.md pour ne pas faire passer artificiellement
le contrôle. La rédaction et la revue approfondie restent reportées par l'utilisateur.

Préparation pour le parcours « Confirmer une réservation » :

| Fichiers exacts à ouvrir | Questions à traiter avec tes mots, plus tard |
| --- | --- |
| `src/templates/labs.html` ; `src/static/js/labs.mjs` ; `src/static/js/booking.mjs` | Quel bouton déclenche quoi ? Où résident laboratory, selected, selectedSource, busy et uncertain ? Où sont séparées suggestion et réservation ? |
| `src/static/js/booking.mjs::mutate`, `request` et gestionnaire de booking-confirm | Quelle méthode, URL, forme JSON et protection CSRF partent après le clic ? Pourquoi l'appel n'est-il pas relancé automatiquement ? |
| `src/config/urls.py` ; `src/config/base.py` ; `src/routes/session.py::current_actor` | Quelle route reçoit la requête ? D'où vient request.user ? Pourquoi l'acteur ne provient-il jamais du JSON ? Quels middleware assurent session, authentification et CSRF ? |
| `src/routes/bookings.py::bookings_api` ; `src/routes/booking_http.py::api_methods`, `timestamp`, `booking_json` | Quelle validation est une validation de forme ? Où le succès devient-il 201 et chaque refus un 4xx ? Quelle structure repart vers le client ? |
| `src/services/access.py` ; `src/services/booking_creation.py::create_booking` | Quels contrôles portent sur acteur, rôle, poste, temps, quota et chevauchement ? Quelles erreurs sont indépendantes du protocole ? |
| `src/data/booking_creation.py::creation_transaction`, `lock_actor`, `lock_workstation`, `insert_booking` ; `src/data/booking_reads.py` | Qui exécute l'ORM ? Dans quel ordre sont les verrous ? Quand l'heure et les données sont-elles relues ? Pourquoi le quota est-il recalculé dans la transaction ? |
| `src/data/models.py` ; `src/data/migrations/0002_btree_gist.py` ; `src/data/migrations/0003_workstation_booking.py` | Que protègent les contraintes, et que ne protègent-elles pas seules ? Comment les intervalles consécutifs restent-ils possibles ? |
| `src/static/js/booking.mjs::loadHistory`, `loadSlots`, `message` | Après réponse, quel état change, quels éléments sont reconstruits et comment une réponse perdue diffère-t-elle d'un refus certain ? |
| `mcp-server/project_tools.py` ; `mcp-server/project_runtime.py` ; `src/data/session_auth.py` | À quel niveau entre book_slot ? Comment l'acteur est-il revérifié sans appeler une route HTTP ni choisir un owner_id ? |
| Les fichiers ci-dessus, puis `tests/test_booking_creation.py`, `tests/test_booking_api.py`, `tests/test_booking_concurrency.py` | Quel écart **réel** entre ton schéma d'architecture et le code peux-tu démontrer ? Le corriges-tu, ou quelle raison justifie son maintien ? Quelle preuve le confirme ? Ne pas inventer d'écart pour remplir une rubrique. |

La revue personnelle devra nommer fichiers, fonctions, données traversant chaque
frontière et un écart justifié. Aucun paragraphe final ni validation de compréhension
n'est rédigé ici. L'aide de Codex doit rester attribuée dans le texte que tu produiras.

## Ce qui reste, selon l'échéance

**Réception Lab 03 explicite** : note personnelle, lecture personnelle du diff et
bilan personnel des écarts ; trace exacte des critères réalisés ; test de refus
qui détecte un défaut, migrations à vide, statuts manuels et CI (preuves existantes
conservées) ; condition de contrôle entièrement vert encore non satisfaite.

**Projet final / calendrier à préciser avec le professeur** : Google et gestion
du personnel absents ; autres états et écrans de l'UI ; intégration réelle de la
session au client MCP et utilisation des outils ; fonctionnement réel du modèle
et conditions d'usage autorisées. Les pages demandent les tests IA hors fournisseur,
elles ne justifient pas d'activer Google ou de déployer pendant ce travail.

**Intervention de l'étudiant, quand il reprendra** : écrire la note puis relire le
diff ; faire préciser réception par tranche contre tous les AC de SPEC, preuve
réelle attendue pour modèle/client MCP et adaptations Codespaces/Gemini/commits
délégués. Garder aussi la question du refus nommant 409/422 et de la relation
plusieurs-à-plusieurs matérialisée par Booking. Aucune réponse personnelle inventée.

## Vérifications de la préparation du 17 novembre

- `node checks/ex3.mjs` : 15/18, sortie 1, mêmes trois échecs après les changements.
- `node checks/ex2.mjs` : 32/32, sortie 0 ; `git diff --check` réussi.
- Pytest collect-only PostgreSQL : 546 cas, sans exécution ni écriture métier.
- Node : 42 réussis, zéro échec ; aucun titre ou assertion modifié.
- Contrôle documentaire : 49 lignes uniques, 46 références de fonctions Python
  réellement existantes, texte des critères Acceptance criteria identique à HEAD.
- Architecture : zéro ligne de réponse, aucun document dont le nom contient
  feature ; le guide n'a pas transformé son absence en succès structurel.
- Ex3 et son helper inchangés ; aucun code/CI/seuil modifié, pas de relance Python
  complète pour ces seules modifications documentaires. Preuve Linux existante
  explicitement datée et rattachée au SHA publié, pas une exécution nouvelle.
- Six documents modifiés/créés, non indexés ; HEAD reste c96aa2e. Aucun commit/push.
  Empreinte SQLite identique ; profils, autres données et instances préservés.

## Finalisation du correctif UI

Les trois ancres suivies restent à la même position après les réponses mesurées
du catalogue, des créneaux et de l'historique. Les 0 px du relevé portent sur
ces trois déplacements. Lors d'un essai supplémentaire, Codex a observé le
refus 401 à 380 px, a relu le message dans Edge et a corrigé les deux champs au
clavier avant de retrouver le bouton avec un focus visible. L'essai a utilisé
le serveur local isolé et des identifiants fictifs. Les preuves de l'étudiant
sont conservées séparément. [Relevés Edge et périmètre d'AC-42](UI.md)

### MIME et isolation

Commande qui a reproduit le problème sous Windows :

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_booking_page.py tests/test_access.py tests/test_auth.py --ds=tests.settings_sqlite_legacy -q --tb=short
```

Avant correction, 42 cas réussissaient. Les cas
`test_root_and_imported_module_are_served_as_javascript[AC-48-root]` (`labs.mjs`)
et `[AC-40-import]` (`booking.mjs`) passaient les assertions HTTP 200,
`text/javascript` et contenu non vide, puis échouaient dans `response.close()`.
Ce dernier émet `request_finished`. Le rappel Django de nettoyage tentait de
consulter une connexion SQLite en mémoire conservée après le test précédent,
alors que pytest interdit l'accès à la base pour ces deux cas. Isolés sous
`tests.settings`, les deux réussissaient sans connexion préexistante.

Le test suspend le rappel de nettoyage pendant la seule fermeture de la
réponse et le rétablit ensuite, selon le principe utilisé par le client de
test Django. Assertions et code de service statique inchangés. La même
commande groupée donne 44 réussites après correction. Cette combinaison sert
à reproduire l'état partagé. Le lanceur officiel garde PostgreSQL pour
l'application et réserve les réglages SQLite historiques à son test de garde.

### Périmètre JavaScript

Les trois fichiers `tests/labs_ui.test.mjs`, `tests/booking_ui.test.mjs` et
`tests/ai_suggestion_ui.test.mjs` exécutent 41 tests. Cette sélection correspond
au job de couverture JavaScript. `npm test`, utilisé aussi par le job `test`,
découvre tous les `tests/*.test.mjs` et exécute 42 tests Node. Le cas
supplémentaire, `test launcher includes PostgreSQL application, TP1 and every UI test`
dans `tests/test_runner.test.mjs`, vérifie le lanceur avec un faux appel de
sous-processus. Les deux sélections ont été exécutées localement.

### Contrôles avant publication

- `npm.cmd test` sous Windows, hors du bac à sable : 545 cas PostgreSQL
  réussis en 295,13 s, un garde SQLite désélectionné puis réussi séparément,
  9 tests Python TP1 et 42 tests Node réussis. L'essai initial dans le bac à
  sable avait bloqué 37 préparations de cas sur le dossier temporaire de pytest.
- `node checks/ex2.mjs` : 32/32. Contrôle MCP TP1 : 12/12. Django `check` avec
  `tests.settings` et `git diff --check` réussis. Les 41 tests de la commande de
  couverture JavaScript passent, avec 97,71 % des lignes et 95,59 % des branches
  sur les modules mesurés. Les résultats de CI précédents restent liés à leur SHA.
- Revue indépendante : le test du template contrôle désormais les trois régions
  réservées et leurs listes. `tests/test_booking_page.py` rejoué sous les réglages
  PostgreSQL officiels : 3 réussites. Les mesures Edge, les essais de l'étudiant,
  les tests locaux et les résultats de CI restent des preuves distinctes.

## Réexamen AC-43 à AC-45 — 23 novembre 2026

Le réexamen précédent avait commencé sur le commit publié `464cbeb`, alors
sans changements locaux. La reprise actuelle a préservé les modifications
déjà présentes d'AGENT_LOG, SPEC, ce guide, app.css et le test de jetons.
Les pages actuelles [Lab 03](https://webdev-course.tu-sofia.workers.dev/en/resources/exercises/3/)
et [guide projet](https://webdev-course.tu-sofia.workers.dev/en/guides/project/)
ont répondu HTTP 200 via curl. Le Lab demande une note personnelle et un
autocontrôle intégral. Le guide du projet situe la finition UI au Lab 04.

Le parcours clavier d'AC-43 dispose de preuves partielles dans `docs/UI.md` et
les guides des jalons. Il manque un parcours étudiant unique, du début à la
fin, au clavier seul, avec vérification des libellés et des effets métier.
Pour AC-44, `base.html` fournit titre et langue, `app.css` définit les cibles
et les couleurs, et `docs/UI.md` consigne des mesures partielles. Il manque un
audit des écrans et états préparés, avec un outil de contraste nommé et la
mesure de toutes les cibles tactiles pertinentes. Aucune de ces deux exigences
n'est déclarée complète par les seuls tests DOM ou recherches textuelles.

Pour AC-45, le nouveau test `tests/style_tokens.test.mjs` a d'abord échoué sur
la taille littérale du titre `h2`. `src/static/css/app.css` utilise désormais
`--text-section`. Le test passe après correction et protège les jetons, leurs
références et l'absence de valeurs dispersées pour les familles contrôlées.
L'inspection complète des éventuels autres styles et le rendu restent à faire.

Sur cette machine, WSL ne liste que `docker-desktop` et le moteur Docker ne
répond pas. Aucun environnement Linux de travail n'est disponible pour lancer
`ex3` intégralement. Le job Ubuntu `test` du SHA publié prouve `npm test`, pas
`node checks/ex3.mjs`. Le vérificateur officiel reste inchangé. Sa recherche
des identifiants est une recherche de sous-chaînes dans les sources des tests ;
elle ne démontre ni la réussite ni l'absence d'un comportement.

Après correction, `node --test tests/*.test.mjs` réussit avec 65 cas. `ex3`
sur Windows donne encore 15/18, sortie 1 : lancement `npm` en `ENOENT`, absence
de titres AC-43/44 et note personnelle absente. AC-45 n'est plus signalé.
`ex2` passe 32/32 et `git diff --check` réussit.

La note d'architecture dans `SPEC.md` reste à rédiger personnellement. Pour le
parcours « Confirmer une réservation », relire `src/static/js/booking.mjs`,
`src/config/urls.py`, `src/routes/bookings.py`, `src/services/booking_creation.py`
et `src/data/booking_creation.py`, puis répondre aux questions de la section 3 ci-dessus
avec ses propres mots. La revue personnelle du diff et la question au professeur
sur le périmètre des critères finaux dans `ex3` restent nécessaires.

### Vérifications complémentaires AC-43 à AC-45 — 23 novembre 2026

Le relevé précédent décrivait les lacunes avant les essais complémentaires.
Codex a depuis effectué dans Edge un parcours étudiant **continu au clavier**
sur une instance Django isolée (port 8015, PostgreSQL de test sur 5433,
fournisseur IA désactivé). Connexion, laboratoire, date, créneau, confirmation,
historique, annulation et déconnexion ont fonctionné. Le focus visible, les
libellés et les états « À venir » puis « Annulée » ont été observés ; le nombre
de créneaux est passé de 10 à 9 puis à 10. La ligne annulée reste dans
l'historique. Les données de démonstration sont restées intactes. Le test de
template porte maintenant AC-43 et vérifie les éléments sémantiques utiles ;
il ne remplace pas l'observation navigateur. Détails dans [UI.md](UI.md).

La connexion a été mesurée à 380, 768 et 1280 px CSS via Edge DevTools :
`innerWidth/clientWidth/scrollWidth` sont respectivement 380/380/380,
768/768/768 et 1280/1280/1280. Titre, langue et hauteurs de quatre éléments
interactifs (lien d'évitement, deux champs, bouton) ont été vérifiés. Edge
« Aperçu du CSS » a relevé la palette ; le test
Node applique le calcul de contraste WCAG aux principales associations
texte/fond, toutes au-dessus de 4,5:1. Les essais antérieurs des écrans étudiant
et personnel aux trois largeurs restent cités avec leurs limites. Le zoom,
les cibles de tous les écrans et tous les états d'erreur ne sont pas entièrement
audités : **AC-44 reste partiel**.

`src/static/css/app.css` est le seul CSS applicatif. Son inspection, le test de
jetons et le rendu Edge après correction confirment AC-45 dans le périmètre
construit. Le test contrôle désormais explicitement `--text-section` et les
contrastes/minimums CSS. Aucune refonte ni nouvelle fonctionnalité. La note
personnelle reste absente. `node checks/ex3.mjs` officiel, inchangé, donne
**16/18 sous Windows** : traçabilité AC-43/44/45 acceptée ; `spawnSync npm
ENOENT` persiste et la note personnelle manque. Ce résultat n'est pas un
contrôle Lab 03 entièrement réussi. Le relevé 15/18 précédent reste daté.

### Complément d'audit AC-44 — 23 novembre 2026

Codex a utilisé Edge sur un serveur local ignoré par Git, relié exclusivement
à la base PostgreSQL de test sur 5433. La connexion et les écrans étudiant,
réservations du personnel et catalogue du personnel ont été inspectés avec le
zoom **navigateur** de 200 % (émulation Responsive désactivée). Sur la fenêtre
physique de 768 px, la Console a mesuré `innerWidth/clientWidth/scrollWidth =
379/372/372` CSS. Les quatre écrans ont replié leur contenu sans perte visible
ni défilement horizontal. Les contrôles `a`, `button`, `input`, `textarea`
visibles et mesurés n'ont pas de rectangle inférieur à 44 CSS px ; les
sous-commandes natives ne sont pas couvertes. Le personnel, réservations, a
également été remesuré en Responsive à 380/768/1280 CSS px, sans débordement.

Les états chargement, vide et erreur des trois vues de données ont été observés
dans Edge via un middleware **local de simulation** des réponses GET ; les
états succès utilisent les vrais services et données de la base de test. Le
refus de connexion à 380 px et les autres parcours aux trois largeurs déjà
documentés ont été réutilisés sans les revendiquer comme nouveaux essais.
Les résultats et limites écran par écran sont dans [UI.md](UI.md). Aucun appel
fournisseur, donnée de démonstration ou changement métier. Aucune nouvelle
correction de production n'a été nécessaire pendant ce complément ; la
correction `--text-section` d'AC-45 reste à publier avec ses tests.

Le premier `npm test` après l'audit a échoué sur des assertions de base vide :
les lignes synthétiques du banc avaient persisté dans la base de test réutilisée.
Le rôle Django de test ne peut pas recréer la base (`--create-db` refuse
`CREATE DATABASE`, conformément à ses permissions limitées). Codex a donc
exécuté `flush` **uniquement** sur `test_lab_booking_1a` après vérification
explicite du nom et du port 5433, en conservant les migrations. La base de
développement et les données de démonstration n'ont pas été touchées.

AC-44 reste **partiel** : contrôles internes natifs, commandes désactivées de
mutation et certains états transitoires non revus, et écrans Google/compte
non livrés. Les rapports de contrastes automatisés sur la palette ne sont pas
une inspection de chaque pixel rendu. La note et la revue personnelles restent
à faire par l'étudiant.

Vérifications locales après nettoyage de la base de test : `npm test` a réussi
avec **573 tests PostgreSQL**, **1 garde SQLite**, **9 tests TP1** et **66 tests
Node**. La couverture JavaScript du job `coverage` a réussi : 63 tests, 97,97 %
des lignes et 94,69 % des branches des modules mesurés. Le lanceur `npm test`
inclut automatiquement `tests/style_tokens.test.mjs` parmi les `*.test.mjs` ;
le job de couverture exécute les cinq fichiers UI qui instrumentent les modules
de production, sans ajouter de nouvelle exclusion. `node checks/ex2.mjs` :
32/32. `node checks/ex3.mjs` officiel, exécuté sous Windows/Node 22.12.0 :
16/18, sortie 1 ; `spawnSync npm ENOENT` dans ce vérificateur et note personnelle
absente. `npm test` réussi ne vaut pas réussite d'ex3. `git diff --check` :
réussi. La CI du futur SHA publié reste à observer séparément.
