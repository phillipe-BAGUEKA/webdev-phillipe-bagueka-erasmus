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
| TP3 Check status codes by hand | Complément du 12 novembre ci-dessous : requêtes sur le serveur réel, 201 création, 409 conflit, 401 consultation anonyme, 403 autre propriétaire ; aussi POST création/annulation anonymes401 avec CSRF valide. Comptages et champs PostgreSQL comparés avant/après. Aucun secret partagé. |
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

## Complément HTTP réel — observations du 12 novembre 2026

Point de départ propre : 8910a6c454e91d321d9d0e9ddc8236f8908974b0. L'utilisateur
reporte explicitement l'accompagnement, la rédaction et la revue personnelles.
Architecture reste une exigence en attente ; aucun texte personnel ni validation
de compréhension n'est produit par Codex.

Le processus à l'écoute sur 127.0.0.1:8000 utilise la commande de ce dépôt,
sa .venv et --settings=src.config.postgres --insecure --noreload. Lecture réelle
PostgreSQL : lab_booking_1a, rôle lab_booking_1a_dev, port 5433. Aucun redémarrage,
provisionnement, transfert SQLite ou accès à l'instance 5432.

L'unique compte dédié existant pour ce parcours était student-ui@demo.example.
Sur autorisation explicite, Codex a créé student-http@demo.example (id 2), actif,
role=student, is_staff=False, is_superuser=False, initialement sans mot de passe
utilisable. Aucun compte ou mot de passe existant modifié. Laboratoire DEMO UI,
postes A/B et deux réservations historiques conservés. L'utilisateur a confirmé
avoir défini le mot de passe neuf dans l'invite masquée et s'être connecté dans
Edge InPrivate. Commande fournie pour cette préparation initiale uniquement,
**à ne pas répéter pour modifier un mot de passe existant** :

```powershell
.\.venv\Scripts\python.exe manage.py changepassword student-http@demo.example --settings=src.config.postgres
```

Connexion dans cette fenêtre : http://127.0.0.1:8000/login. La session régulière
student-ui est conservée séparément. Codex a observé les deux identités affichées
sur /labs dans leurs fenêtres distinctes. La saisie du mot de passe reste un fait
rapporté par l'utilisateur ; aucune valeur n'a été lue, affichée ou enregistrée.

| Méthode et route | Attendu | Réellement observé | Effet vérifié |
| --- | --- | --- | --- |
| POST /api/bookings, student-http connecté en InPrivate | 201, réservation créée pour la session | **201**, JSON booking id 3, poste 1, début 2026-11-13T06:00:00Z, fin 07:00:00Z, cancelled_at=null | **2 → 3 lignes**, une seule nouvelle réservation, propriétaire id2 ; les deux lignes antérieures identiques sur tous leurs champs |
| POST /api/bookings, même poste/créneau et même session | 409, refus métier | **409**, {"error":"Ce poste est déjà réservé sur ce créneau."} | **3 → 3 lignes**, comparaison de tous les champs de toutes les lignes : identiques |
| GET /api/bookings, aucun cookie fourni | 401, aucune donnée personnelle | **401**, application/json, {"error": "Connexion requise."} | **2 → 2 réservations**, comparaison de tous les champs de toutes les lignes : identiques |
| POST /api/bookings/3/cancel, student-ui connecté en fenêtre normale | 403 métier avec CSRF valide | **403**, {"error":"Tu ne peux annuler que tes propres réservations."} | **3 → 3 lignes**, tous les champs identiques ; réservation 3 encore non annulée et toujours propriété de student-http |

Le 401 provient d'une requête réseau volontaire contre le serveur réel, envoyée
par urllib (code standard Python) hors pytest, sans Django Client, mock ou base
de test. Comparaison en lecture seule PostgreSQL avant/après : id, propriétaire,
poste, début, fin, création et annulation. Le corps d'erreur est le seul contenu
reçu ; aucune liste ni identité. Relevé non sensible local ignoré :
.local/http-manual-401-20261112.json. Les tests automatisés antérieurs ne sont
pas utilisés comme preuve de ces observations.

### Méthode des mutations et distinction CSRF/propriété

Codex a saisi volontairement des appels fetch dans la Console DevTools de chaque
fenêtre, sur l'origine http://127.0.0.1:8000, credentials=same-origin. En-têtes :
Content-Type application/json et X-CSRFToken alimenté en mémoire depuis
document.querySelector('#booking-csrf').value de **la même page/session**.
Seuls le statut HTTP et le JSON de réponse étaient affichés. Aucun cookie,
jeton, en-tête sensible ou profil n'a été copié dans les échanges ou relevés.

Le créneau vient du GET réel /api/labs/1/availability?date=2026-11-13 : HTTP 200,
20 créneaux, premier poste DEMO UI - Poste A. Corps exact des deux demandes :
{"workstation_id":1,"starts_at":"2026-11-13T06:00:00Z","ends_at":"2026-11-13T07:00:00Z"}.
Cela correspond à 08:00–09:00 Europe/Sofia le 13 novembre, strictement futur
au moment de l'essai. La création a renvoyé created_at=2026-11-12T17:39:04.082188Z.
L'annulation interdite depuis l'autre session envoyait le JSON vide {}.

Le message reçu en 403 est celui de NotBookingOwner, traduit par l'adaptateur
HTTP. Il diffère du corps que produirait csrf_failure : « La vérification de
sécurité a échoué. Recharge la page puis réessaie. ». Le middleware CSRF a donc
laissé atteindre la règle de propriété ; il n'a pas été désactivé ou contourné.
Le 201 dans la session de création confirme aussi un POST réellement accepté.

Ces requêtes réseau réelles ne passent ni par Django Client, ni par une fixture,
ni par une invocation directe du service. La vérification des effets est une
lecture indépendante de la base de développement 5433, avant/après chaque
étape. Relevés non sensibles ignorés : .local/http-manual-before-create.json,
after-create.json, after-conflict.json, after-forbidden.json et after-owner-cancel.json
(ces quatre derniers noms ont aussi le préfixe http-manual-).

### Refus anonymes complémentaires et état final

Pour couvrir aussi les mutations sans session, Codex a utilisé un CookieJar
urllib **neuf**, uniquement en mémoire, obtenu le CSRF d'un GET réel /login,
vérifié l'absence de session authentifiée, puis envoyé les deux POST avec ce
CSRF valide : /api/bookings et /api/bookings/3/cancel ont chacun répondu **401**,
{"error":"Connexion requise."}. Trois lignes avant/après, tous les champs
identiques. Le jeton et les cookies n'ont été ni imprimés ni sauvegardés.
Relevé expurgé : .local/http-manual-anonymous-posts.json. Il s'agit de sondes
HTTP ponctuelles contre l'application en marche, hors suite de tests automatisés.

Après le refus 403, le propriétaire student-http a envoyé le même POST
/api/bookings/3/cancel avec sa propre session/CSRF : **HTTP 200**, id 3 conservé,
cancelled_at=2026-11-12T17:44:39.439591Z. La comparaison confirme que seul ce champ
a changé sur la nouvelle ligne ; propriétaire, poste, créneau et date de création
restent identiques, les deux réservations anciennes aussi. **Trois réservations
conservées au total, toutes annulées ; aucune suppression.** Dans Edge InPrivate,
après rechargement explicite, Codex a observé « 1 réservation(s), historique
compris. » et le poste A « Annulée · Poste en service ». Les requêtes Console
n'utilisaient pas le contrôleur de l'écran : aucune actualisation automatique
de celui-ci n'est revendiquée. Les clics natifs tentés n'ont pas donné de changement
observable dans l'outil ; le résultat a été vérifié après rechargement, sans
attribuer ce comportement à un défaut applicatif non démontré. DevTools refermés,
sessions conservées. Captures affichées par l'outil, non archivées au dépôt.

380 pixels, limites UI, IA/MCP absents et ambiguïtés professorales restent ouverts.
Pas de défaut de l'API démontré, ni changement applicatif ou de CI ; pas de
relance locale complète des tests pour cette documentation seule. Contrôles et
publication de ce complément consignés après leur exécution réelle.

Contrôles locaux de ce complément : ex2 **32/32**, git diff --check réussi,
aucun changement applicatif ou de configuration. Revue indépendante en lecture
seule : aucun problème bloquant ou important ; amélioration de lisibilité
routes/statuts retenue, aucun constat écarté. Cette revue de preuves ne remplace
pas la revue personnelle reportée. La CI sera vérifiée sur le SHA publié ; aucun
résultat distant nouveau n'est présumé à partir du commit précédent.
