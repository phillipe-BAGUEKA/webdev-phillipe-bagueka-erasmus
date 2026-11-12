# Slice 2 — finalisation de la tranche réservation

Date de vérification : 12 novembre 2026. Point de départ propre :
64bc12a1f0c0ee8b6a5af44111fceaa6afe74e07, huit commits locaux depuis origin/main.
Cette livraison ne constitue pas une déclaration de clôture du TP3.

## Périmètre et preuves

Slice 2 regroupe **AC-11 et AC-13 à AC-28**, sans réécriture ni renumérotation.
Les aspects applicables d'AC-40 à AC-45 et les sessions AC-46/47/49 sont
transversaux. AC-1 à AC-10, AC-12, AC-29 à AC-39 restent hors de cette tranche.
Un test portant un identifiant peut n'en prouver qu'une partie : voir SPEC.

| Domaine | Preuve réellement disponible | Limite |
| --- | --- | --- |
| Modèles et migrations | Guides 1A/1B ; nouvelle base PostgreSQL vide, contraintes réelles | Pas de migration de la base SQLite conservée |
| Disponibilités, création, quota, annulation/historique | Tests directs PostgreSQL et horloge contrôlée, guides 2A/2B/2D | Une lecture n'autorise pas une création ultérieure |
| Concurrence AC-22/23/24 | Connexions distinctes, attente réelle des verrous observée, guide 2C ; mutation temporaire du quota détectée puis restaurée | Seulement les entrelacements décrits, pas tous les scénarios possibles |
| HTTP | Intégration sessions/CSRF, refus et absence de mutation, guide 3 | Les statuts automatisés ne sont pas des observations manuelles |
| UI | DOM/réseau simulé ; parcours Edge ci-dessous | Pas de preuve de toute l'accessibilité ou de tous les états |

## Observations Edge supplémentaires de Codex

L'utilisateur a laissé sa session de démonstration disponible. L'accès natif à
Edge a été utilisé ; aucune valeur de mot de passe, cookie ou profil n'a été lue.
Le navigateur a signalé une intervention utilisateur : les entrées ont été
suspendues puis reprises après sa confirmation « DISPONIBLE ».

- Lien « Aller au contenu » révélé par Tab avec contour visible. Navigation
  vers le laboratoire avec Tab/Entrée ; ouverture des disponibilités et focus
  visible sur le champ de date. La saisie native est segmentée : la séquence
  de chiffres 13112026, sans flèches supplémentaires, a donné 13/11/2026.
- À partir du champ de date : Tab, Tab, Entrée charge 20 créneaux ; Tab, Entrée
  sélectionne le premier poste A, 08:00–09:00 Europe/Sofia. Le focus passe au
  bouton de confirmation, avec contour visible. Entrée confirme : succès,
  18 créneaux et deux entrées d'historique, dont la nouvelle « À venir ».
- Depuis la date après le succès, Tab traverse calendrier, recherche, les
  18 créneaux et le bouton d'actualisation jusqu'à l'annulation. Son contour
  est visible ; Entrée annule. Succès et retour à 20 créneaux. L'ancienne entrée
  annulée du premier essai est conservée ; la nouvelle est aussi annulée.
  Aucune suppression ni modification d'un compte ou laboratoire existant.
- Ce parcours prouve la partie réservation/annulation au clavier. Il ne constitue
  pas un nouvel essai complet connexion → action → déconnexion dans une seule
  session : connexion/déconnexion clavier étaient rapportées par l'utilisateur
  au TP2. Le mot de passe n'a pas été ressaisi par Codex.
- DevTools Network : simulation **Offline**, puis « Afficher les créneaux ».
  La requête fetch échoue, sans réponse HTTP ; message visible : « Erreur réseau.
  Vérifie ta connexion puis réessaie la consultation. ». Retour à **No throttling**,
  réessai explicite : HTTP **200**, puis 20 créneaux. Simulation désactivée et
  DevTools fermé à la fin. Ce n'est pas un arrêt réel du backend.
- Pas de défaut applicatif démontré ; pas de correction de production nécessaire.
  Le refus HTTP métier, la session expirée, le CSRF et le résultat de mutation
  incertain restent couverts automatiquement, pas tous rejoués dans Edge.
  Aucun statut de création/annulation n'a été relevé dans le réseau pendant
  l'essai clavier. Captures affichées par l'outil, non archivées au dépôt.

### Contraste

Outils : **Edge DevTools, CSS overview**, capture de la page réellement rendue,
puis calcul Python de la luminance relative sRGB et du rapport WCAG 2
`(L_clair + 0.05) / (L_sombre + 0.05)`. CSS overview a montré les couleurs de fond
#ffffff, #f2f5f8, #173e75 et de texte #182534, #173e75, #ffffff, #17613d,
#9c2020 et #000000. Les associations ont été contrôlées dans app.css.

| Texte / fond | Rapport mesuré |
| --- | --- |
| #182534 / #ffffff | 15,520:1 |
| #173e75 / #ffffff, ou blanc sur bouton bleu | 10,593:1 |
| #9c2020 / #ffffff (erreur) | 7,951:1 |
| #17613d / #ffffff (succès) | 7,463:1 |
| #173e75 / #f2f5f8 (en-tête) | 9,681:1 |

Les associations de texte applicatif mesurées dépassent 4,5:1. Le noir du
contrôle natif ne pose pas de contraste sur blanc. Ce relevé de palette n'est
pas un audit de lecteur d'écran ni de tous les contrôles natifs/états futurs.
380 pixels reste reporté ; 768/1280 et les déplacements au chargement ne sont
pas déclarés vérifiés. Aucun certificat global de conformité UI.

## Exigences actuelles, sources et écarts

Sources officielles récupérées le 12 novembre 2026 :
[TP3, étapes et What you build](https://webdev-course.tu-sofia.workers.dev/en/resources/exercises/3/),
[projet, The requirements exactly et When you build which part](https://webdev-course.tu-sofia.workers.dev/en/guides/project/).
La lecture Web a échoué ; curl a réussi après relance réseau autorisée.
Copies de consultation dans .local, ignorées. Le site se présente comme un
brouillon susceptible d'évoluer ; ces constats sont datés.

| Exigence et section | État et preuve / action restante |
| --- | --- |
| TP3 Steps 1–5, autonomie, plan revu, petits commits | Huit jalons et commits conservés, décisions/autorisations dans AGENT_LOG. Codex/Windows et commits délégués sont des adaptations explicitement autorisées par l'étudiant ; l'énoncé réserve critères, revue et commits à l'étudiant : faire confirmer cette méthode au professeur. Aucune compréhension personnelle présumée. |
| TP3 What you build : migration, endpoints, règles en service, autorisation, UI | Construits ; guides 1B à 4 et tests PostgreSQL. 401/403 distincts, refus 409/422 ; données inchangées sur refus. |
| TP3 Prove the tests bite | Preuve conservée au jalon 2C : neutralisation temporaire du quota, test échoue, code restauré. Pas rejouée ici. |
| TP3 Check status codes by hand | Statuts testés automatiquement ; seul GET availability 200 relevé manuellement ici. Démonstration manuelle 201/409/401 et propriétaire 403/401 avec deux utilisateurs reste à effectuer sans partager les mots de passe. |
| TP3 Architecture note, whole diff, What the agent did that I did not ask for | Note personnelle encore vide ; chemins/questions ci-dessous. La lecture personnelle de tout le diff et le bilan personnel des écarts ne sont pas certifiés par une revue Codex. |
| TP3 critères/tests | Tous les identifiants de Slice 2 existent dans les titres collectés ; preuves partielles documentées. Les critères du projet futur restent non testés ; détails ci-dessous. |
| TP3 Step 1 : refus nommant son code | Les contrats HTTP approuvés nomment 409/422 dans la spécification et les tests. Les formulations originales AC-17/20 ne nomment pas elles-mêmes le statut : faire valider par l'étudiant/professeur si cette correspondance suffit, sans les réécrire silencieusement. |
| Projet Application and data | Backend/frontend/REST, quatre entités et migrations présents. Booking associe User et Workstation : relation plusieurs-à-plusieurs conceptuelle avec attributs temporels, sans champ Django ManyToManyField explicite. Confirmer si le professeur exige une représentation ORM explicite. Déploiement public non réalisé, hors phase. |
| Projet Sign-in and permissions | Local et propriétaire réalisés ; Google/liaison restent spécifiés mais non construits. Gestion du personnel future. |
| Projet Model feature | Choix et données sortantes spécifiés ; client, validation, timeout, repli et tests dédiés pas implémentés. Aucun appel fournisseur dans cette finalisation. |
| Projet MCP server | Deux outils de cours TP1 seulement. Les quatre outils projet restent prévus, aucun ne réutilise encore les services ni une session applicative. Minimum officiel : trois outils supplémentaires, descriptions ≥20 caractères. |
| Projet UI et tests | Palette/contraste et parcours partiel clavier observés ; quatre états testés en DOM, réseau réel testé ici. Largeurs et audit complet restent ouverts ; couverture Python réelle et seuils maintenus. |

L'énoncé TP3 rend IA/MCP conditionnels dans certains paragraphes (« If the feature
calls a model », « If ... reachable over MCP »), mais son auto-contrôle les exige
inconditionnellement et sa liste finale exige tous les contrôles verts. Le guide
projet exige IA/MCP au projet final et indique qu'ils se construisent où ils
s'insèrent. **Demander au professeur si la tranche réservation sans IA/MCP peut
être reçue séparément pour TP3.** Aucune de ces fonctions n'est ajoutée ici.

### Contrôle TP3 inchangé

`node checks/ex3.mjs` sous Windows : **11/18**, code de sortie 1.

- Échec « test suite passes » : `spawnSync npm ENOENT`, car le vérificateur
  appelle npm sans shell et Windows fournit npm.cmd. `npm test` exécuté directement
  fonctionne et lance réellement Django/PostgreSQL, TP1 et Node. Vérificateur intact.
- Échec de traçabilité : le contrôle liste AC-3, AC-5 à AC-10, AC-12,
  AC-29 à AC-39, AC-43 à AC-45. Il cherche des sous-chaînes dans les sources :
  ses succès apparents pour AC-1/2/4 peuvent provenir d'AC-11/20/40, pas de tests
  Google. Relevé plus strict des titres réellement collectés Python/Node :
  **AC-1 à AC-10, AC-12, AC-29 à AC-39, AC-43 à AC-45 absents**.
  AC-40/41/42 présents ne signifient pas validation complète de ces critères.
- Échecs réels : repli IA absent, MCP sans services ni acteur, zéro outil projet,
  note personnelle absente. IA « built », timeout et faux client signalés verts
  par recherche de mots dans mcp-server/server.py et mcp-server/test_server.py,
  sans fonction IA applicative livrée : ce sont des faux positifs structurels,
  pas des preuves fonctionnelles.
- Aucun identifiant factice, critère supprimé, test affaibli ou contrôle modifié.
  Ce diagnostic connu n'est pas ajouté comme faux contrôle vert dans la CI.

## Ta note d'architecture : fichiers à ouvrir et questions

Ce repérage est une aide de Codex, **pas le texte de ta note**. Écris toi-même
dans SPEC.md, section Architecture, après lecture des fichiers :

1. src/config/urls.py puis src/routes/bookings.py, bookings_api : quelle route
   reçoit POST /api/bookings, d'où provient l'acteur et où est choisi HTTP 201 ?
2. src/routes/booking_http.py : que valident json_object/timestamp, comment
   api_methods traduit-il chaque erreur et protège-t-il la confidentialité ?
3. src/services/access.py et src/services/booking_creation.py, create_booking :
   où vivent permission, créneau, quota et conflits ? Pourquoi relire l'heure ?
4. src/data/booking_creation.py, creation_transaction, lock_actor,
   lock_workstation, insert_booking ; src/data/booking_reads.py ;
   src/data/models.py et migrations/0002_btree_gist.py,
   migrations/0003_workstation_booking.py (sous src/data/) : qui touche l'ORM,
   dans quel ordre de verrous et quelles contraintes restent en dernier recours ?
5. src/templates/labs.html, src/static/js/labs.mjs, puis booking.mjs : quelle vue
   reçoit les données, où restent laboratory/selected/busy/uncertain/sessionLost,
   et comment request/mutate rendent-ils succès, refus et résultat incertain ?
6. src/services/booking_cancellation.py et src/data/booking_cancellation.py :
   comment l'acteur/propriétaire est-il contrôlé avant l'idempotence ?

Trouve aussi toi-même un écart réel ou une limite des couches, puis explique
ta décision : par exemple, src/services/labs.py est-il un simple passage ?
Qu'est-ce qui justifie son maintien ? Où entrera un futur outil MCP sans appeler
une route ni l'ORM ? Il n'existe pas encore. Ne prétends pas qu'il fonctionne.

## Commandes et CI

```powershell
npm test
.\.venv\Scripts\python.exe tools/check_coverage.py --postgresql
node --test --experimental-test-coverage --test-coverage-include='src/**' --test-coverage-exclude='tests/**' --test-coverage-lines=80 tests/labs_ui.test.mjs tests/booking_ui.test.mjs
node mcp-server/check.mjs -- .\.venv\Scripts\python.exe mcp-server/server.py
node checks/ex2.mjs
node checks/ex3.mjs
git diff --check
```

Le lanceur npm choisit la .venv locale si présente, sinon Python du PATH (CI).
Il échoue dès une commande échouée. Il exécute application/concurrence PostgreSQL,
puis **le test SQLite historique inchangé** avec tests.settings_sqlite_legacy
(base en mémoire, migration 0001 originale réutilisée par alias), puis TP1 et
tous les fichiers tests/*.test.mjs. Il ne migre jamais demo.sqlite3. Aucun modèle
de réservation n'est rendu compatible SQLite. La mesure Python PostgreSQL garde
sa seule désélection historique ; cette assertion est exécutée séparément par npm.

CI : chaque job test/coverage reçoit son propre service PostgreSQL 16 éphémère
sur le port de job 5433, sans contact avec les instances du PC. L'action locale
.github/actions/postgres-test crée uniquement le rôle lab_booking_1a_test
(sans SUPERUSER/CREATEDB/CREATEROLE) et sa base, vérifie zéro table publique,
puis applique toute la chaîne de migrations avec ce rôle. btree_gist est créée
par sa migration ; aucune migration existante n'est modifiée. Le profil CI neuf
est écrit exclusivement dans .local avec mode 0600. Les valeurs `ci-only-*`
sont des fixtures publiques limitées aux services éphémères, pas des identifiants
du PC. Aucun secret GitHub requis.

Le serveur du conteneur écoute lui-même sur 5433 (PGPORT, publication 5433:5433
et healthcheck -p5433), car les tests de concurrence contrôlent aussi
inet_server_port(), pas seulement le port client. La valeur par défaut serveur
PGPORT est documentée par [PostgreSQL 16, postgres -p](https://www.postgresql.org/docs/16/app-postgres.html).
Une simple redirection 5433:5432 ne respecterait pas cette preuve ; aucune
assertion d'identité n'a été modifiée.

Les jobs MCP et SPEC/ex2, la condition Docker existante et les seuils sont conservés.
Couverture : inventaire Python complet, TP1 compris ; 100 % lignes ET branches
des services, ≥80 % lignes globales. Exclusions inchangées : tests, .venv,
fichiers locaux/générés. La couverture JS séparée porte sur les modules chargés
src/**, pas sur tout le frontend ni le rendu. L'ex3 reste un diagnostic incomplet,
pas une preuve de clôture masquée par les quatre jobs de livraison.

## Résultats locaux de finalisation

- npm test final : **319 pytest PostgreSQL réussis, 1 désélectionné** (45,64 s),
  **1 garde SQLite réussi** (0,17 s), **9 TP1 réussis** (0,747 s), **23 Node réussis**.
- Couverture PostgreSQL : 319 réussis/1 désélectionné (62,09 s), 9 TP1 réussis
  (7,473 s) ; **services 220/220 lignes, 74/74 branches, 100 % chacune** ; global
  Python **1206/1283 lignes, 94,00 %**, branches **290/320, 90,625 %**. Inventaire
  inchangé, 49 fichiers Python de production. Pas de couverture SQLite globale
  mesurée ici. Rapport local ignoré :
  .local/coverage/af6059615acd4319bbe4eda12f280239/coverage.json.
- Couverture JavaScript des modules src chargés : **98,18 % lignes**,
  **90,91 % branches** ; booking100 % lignes, labs93,02 %. Seuil80 % conservé.
- MCP **12/12**, ex2 final **32/32**, contrôles Django, absence de dérive des
  migrations, pip check et git diff --check réussis. Le premier ex2 donnait31/32
  car les lignes d'un paragraphe de regroupement étaient prises pour des critères :
  seule sa mise en forme a changé, ni identifiants ni vérificateur.
- ex3 inchangé **11/18**, sortie1, raisons ci-dessus. L'appel npm interne Windows
  échoue avant d'exécuter les tests ; les résultats npm directs restent distincts.

Revue indépendante en lecture seule : aucun problème bloquant ou important.
Amélioration facultative retenue : assertion explicite de priorité du Python
Windows de la .venv dans le test synthétique du lanceur. Aucun constat écarté.
Les résultats de publication réellement observés sont consignés ci-dessous.

## Publication et preuves GitHub Actions

Push normal de l'historique local conservé, de b4c4cc6 à
[2011d95d6d711dd0ee84d60af7eb2135801ae9de](https://github.com/phillipe-BAGUEKA/webdev-phillipe-bagueka-erasmus/commit/2011d95d6d711dd0ee84d60af7eb2135801ae9de),
sans divergence distante ni force-push. Répertoire propre juste après ce push.
[Run CI 43262915943](https://github.com/phillipe-BAGUEKA/webdev-phillipe-bagueka-erasmus/actions/runs/43262915943) :

| Job | Résultat observé dans les logs |
| --- | --- |
| [test](https://github.com/phillipe-BAGUEKA/webdev-phillipe-bagueka-erasmus/actions/runs/43262915943/job/131338691716) | Réussi ; 319 pytest PostgreSQL, 1 désélectionné (23,15 s), garde SQLite séparé réussi (0,11 s), 9 TP1 (0,284 s), 23 Node, aucun ignoré. Étape Docker ignorée par la condition existante, aucun Dockerfile. |
| [coverage](https://github.com/phillipe-BAGUEKA/webdev-phillipe-bagueka-erasmus/actions/runs/43262915943/job/131338690884) | Réussi ; 319 pytest/1 désélectionné (21,70 s), 9 TP1 (1,033 s). Services 220/220 lignes et 74/74 branches (100 %). Global Python 1207/1283 lignes (94,0764 %, arrondi94,08 %), branches291/320 (90,9375 %). JS : 22 tests et 98,18 % lignes, 90,91 % branches des modules src chargés. |
| [mcp](https://github.com/phillipe-BAGUEKA/webdev-phillipe-bagueka-erasmus/actions/runs/43262915943/job/131338691900) | Réussi, contrôle de conformité TP1 conservé ; pas une preuve des outils MCP projet absents. |
| [spec](https://github.com/phillipe-BAGUEKA/webdev-phillipe-bagueka-erasmus/actions/runs/43262915943/job/131338691271) | Réussi, ex2 conservé ; pas une exécution de l'ex3 ni une validation professorale. |

Dans **chacun** des deux jobs PostgreSQL : `Public tables before migrations: 0`,
identité test_lab_booking_1a / lab_booking_1a_test, port serveur5433 ; flags
SUPERUSER/CREATEDB/CREATEROLE tous faux. Migrations data.0001_initial,
0002_btree_gist, 0003_workstation_booking et migrations Django réussies ; aucune
dérive de modèle. Version serveur réellement affichée : PostgreSQL16.15.
Les erreurs de contraintes présentes dans les logs PostgreSQL proviennent des
tests négatifs attendus, pas d'un job échoué. Aucun correctif CI après ce run.

La mesure Linux est distincte de la mesure Windows : une ligne et une branche
supplémentaires couvertes, mêmes1283 lignes/320 branches et mêmes seuils.
Les jobs s'exécutent sur des clusters séparés ; aucun profil ou donnée du PC
n'est utilisé. La condition Docker existante n'a pas été supprimée ou désactivée.

Ce relevé porte sur le SHA cité. Le commit documentaire qui l'enregistre est
vérifié séparément après publication ; son résultat final doit être rapporté
avec son propre SHA, sans déduire sa réussite de ce premier run.
