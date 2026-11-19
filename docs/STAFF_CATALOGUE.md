# Espace du personnel — Catalogue

## Essayer le parcours

Lancer Django avec les réglages PostgreSQL depuis la racine puis ouvrir
<http://127.0.0.1:8000/staff/catalogue>. Utiliser un compte actif `personnel`.
Le lien **Catalogue du personnel** figure aussi dans l'en-tête de l'espace.
Pour préparer un compte dédié, suivre la procédure du [guide Réservations](STAFF_BOOKINGS.md#ouvrir-lécran).

```powershell
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --settings=src.config.postgres --insecure --noreload
```

1. Saisir un nom de laboratoire, puis choisir **Créer le laboratoire**.
2. Dans la fiche créée, saisir un nom de poste, puis choisir **Ajouter le poste**.
3. Modifier les deux champs de nom et activer chaque bouton **Renommer**.
4. Recharger avec F5. La fiche et le poste affichent leurs nouveaux noms.

Les écritures utilisent la base du serveur démarré. La commande suivante documente
le banc Edge de la machine d'essai, sur une base en mémoire. Son fichier sous
`.local/` est ignoré par Git et absent d'un clone propre. Depuis un clone, la
[suite PostgreSQL ci-dessous](#cycle-et-concurrence-sur-postgresql-isolé) vérifie
la création et le renommage, avec relecture des identifiants et des rattachements.

```powershell
.\.venv\Scripts\python.exe .local/ui-staff-catalogue-audit.fixture .local/ui-staff-catalogue-manuel.stop
```

Ouvrir <http://127.0.0.1:8013/__catalogue_test__/enter> pour obtenir la session
synthétique, puis arrêter le processus avec Ctrl+C après l'essai.

## Changer l'état d'un poste

Le [catalogue](http://127.0.0.1:8000/staff/catalogue) affiche « En service »
ou « Hors service » et propose l'action correspondante. La commande suivante
correspond au banc Edge en mémoire de la machine d'essai. Ce second fichier
sous `.local/` est également absent d'un clone propre. Pour rejouer la règle
métier sans utiliser la base de démonstration, lancer la suite PostgreSQL.

```powershell
.\.venv\Scripts\python.exe .local/ui-workstation-state-audit.fixture .local/ui-workstation-state-manuel.stop
```

1. Ouvrir [la session personnel](http://127.0.0.1:8014/__state_test__/staff). Avec Tab et Entrée, activer **Mettre hors service** pour le poste synthétique.
2. Ouvrir [la session étudiant](http://127.0.0.1:8014/__state_test__/student). Lire **Mes réservations**, puis afficher les créneaux de la date préremplie. La réservation de 9 h à 10 h signale que le poste est hors service. La liste des créneaux est vide.
3. Revenir à la session personnel et activer **Remettre en service**. Retourner à la session étudiant. Le créneau de 10 h à 11 h réapparaît et celui de 9 h à 10 h reste occupé. Arrêter le banc avec Ctrl+C.

## Contrat et preuves PostgreSQL

| Méthode et route sous `/api/staff/catalogue` | Effet |
| --- | --- |
| `GET` sur la racine | Laboratoires avec leurs postes, triés par identifiant. |
| `POST` sur la racine | Crée un laboratoire. Réponse 201. |
| `PATCH /laboratories/{lab}` | Renomme le laboratoire. Réponse 200. |
| `POST /laboratories/{lab}/workstations` | Crée le poste dans ce laboratoire. Réponse 201. |
| `PATCH /laboratories/{lab}/workstations/{poste}` | Renomme le poste sous ce parent. Réponse 200. |
| `PATCH /laboratories/{lab}/workstations/{poste}/state` | Applique `{"is_operational": true}` ou `false`. Réponse 200 avec l'état enregistré. |

La création et le renommage reçoivent un objet JSON avec `name`. Toutes les
écritures exigent le jeton CSRF. Le service
vérifie le rôle actif `personnel` et valide le nom après retrait des espaces
aux extrémités. La couche de données utilise les tables existantes. Le renommage
met à jour uniquement le nom. La contrainte PostgreSQL du poste refuse un nom
identique dans le même laboratoire avec un 409 et permet le même nom ailleurs.
Le nom du laboratoire conserve les règles du modèle existant.

Le changement d'état verrouille la ligne `Workstation` dans la transaction,
comme `create_booking`. Il écrit uniquement `is_operational` quand la valeur
diffère. Répéter la même demande conserve le résultat. Le renommage écrit
uniquement le nom. Les historiques du personnel et de l'étudiant lisent l'état
courant du poste tout en gardant le statut de la réservation.

### Cycle et concurrence sur PostgreSQL isolé

Préparer la base de test selon le [guide PostgreSQL](POSTGRES_1A.md), puis
lancer ces tests versionnés depuis la racine du dépôt.

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_staff_catalogue.py tests/test_staff_bookings.py tests/test_workstation_state_concurrency.py --ds=tests.settings_postgres --reuse-db -q
```

- Une réservation de 9 h à 10 h et un créneau autrement valide de 10 h à 11 h
  sont préparés pour le même poste et le même étudiant. Chaque état est demandé
  deux fois. La réservation est comparée champ par champ. Hors service, elle
  reste à venir dans les deux historiques, les disponibilités sont vides et le
  POST direct pour 10 h reçoit 409. Après remise en service, la liste initiale
  revient et 9 h reste occupé.
- Une session étudiante avec CSRF valide reçoit 403 pour le changement d'état.
  Une session personnel sans CSRF reçoit un 403 distinct. Sans session ou avec
  un compte personnel désactivé, l'API renvoie 401. Les données restent identiques.
- Deux connexions éprouvent les deux ordres. Si le changement d'état verrouille
  le poste en premier, la création attend puis est refusée. Si la création
  détient le verrou en premier, elle aboutit avant la désactivation et demeure
  conservée. Le blocage est constaté dans PostgreSQL avec `pg_blocking_pids`.

`tests/test_staff_catalogue.py` vérifie la création d'une seule ligne par action,
les identifiants stables et le rattachement après rechargement. Une session
étudiante avec jeton valide reçoit 403 sur les quatre opérations de création
et de renommage, y compris si `is_staff` est actif. Les lignes et le rôle sont comparés avant et
après. Les essais vérifient également les écritures sans jeton, les noms invalides,
les doublons à la création et au renommage, le parent incorrect et la préservation
de l'état d'un poste déjà hors service. Les tests DOM vérifient les quatre actions,
les retours de focus et la relecture après une écriture incertaine.

## Observations Edge

Le 20 novembre 2026, Codex a réalisé les quatre opérations au clavier à chaque
largeur, après mise au focus de la page. Edge DevTools a mesuré `innerWidth`,
`clientWidth` et `scrollWidth`. Le serveur Django local a utilisé une session
de personnel synthétique et SQLite en mémoire sur `127.0.0.1:8013`. La preuve
du comportement d'unicité vient des tests PostgreSQL séparés.

| Largeur CSS | Viewport / client / défilement | Résultats après création, renommage et F5 |
| --- | --- | --- |
| 380 px | 380 / 380 / 380 | Laboratoire nº 1 et poste nº 1. Le nom long du laboratoire revient à la ligne dans le titre. |
| 768 px | 768 / 768 / 768 | Laboratoire nº 2 et poste nº 2. Le titre du poste renommé reçoit le focus visible. |
| 1 280 px | 1280 / 1280 / 1280 | Laboratoire nº 3 et poste nº 3. Les trois fiches conservent leurs postes après F5. |

Le serveur a répondu 201 aux deux créations puis 200 aux deux renommages pour
chaque largeur. Les réponses GET après F5 ont confirmé les noms et les paires
d'identifiants 1/1, 2/2 et 3/3. Le focus est passé au champ d'ajout du poste,
puis aux titres après les enregistrements. Les captures restent dans la
conversation. Le banc a été arrêté et sa base en mémoire libérée. La base de
démonstration a été préservée.

### Relevé Edge du changement d'état

Le 20 novembre 2026, Codex a utilisé Edge à 380 × 424 px CSS avec le même poste
et deux sessions synthétiques sur le banc SQLite en mémoire, port 8014.
Les deux boutons ont été atteints avec Tab et activés avec Entrée. Le focus
visible est resté sur le bouton qui porte maintenant l'action inverse.
La console a mesuré 380 / 380 / 380 pour la largeur, le client et le défilement
horizontal du catalogue et de la vue étudiant.

| Moment | Catalogue et réservation | Vue étudiant le 23 novembre, Europe/Sofia |
| --- | --- | --- |
| Après désactivation, PATCH 200 | « Hors service ». Réservation nº 1 toujours à venir avec « Poste hors service » côté personnel. | Réservation de 9 h à 10 h visible avec le même signalement. 0 créneau disponible. |
| Après réactivation, PATCH 200 | « En service ». Même poste. | Même réservation à venir. 9 créneaux disponibles, dont 10 h à 11 h. 9 h à 10 h reste occupé. |

Le banc a comparé la réservation avant et après, puis a été arrêté. L'essai
navigateur a utilisé les pages et l'API, et le verrou ainsi que le POST refusé
ont été vérifiés séparément sur PostgreSQL. La base de démonstration est restée
en dehors de ces essais.

## Vérifications locales du cycle d'état

La couverture complète a exécuté 573 cas PostgreSQL et 9 tests Python TP1.
Le garde SQLite a réussi séparément. Les services couvrent 404/404 lignes et
124/124 branches. La mesure globale atteint 1 995/2 243 lignes (88,94 %) et
478/544 branches (87,87 %), serveur TP1 et anciens bancs Python ignorés inclus.
Deux bancs Python ignorés ajoutent 148 lignes non exécutées à cette mesure
Windows. L'ancienne CI de `2919829` mesurait 1 766/1 865 lignes depuis un clone
sans ces fichiers et avant les ajouts du personnel. Les inventaires diffèrent.

Les 28 cas PostgreSQL ciblés couvrent le catalogue, les réservations du personnel
et les deux ordres concurrents. Les 64 tests Node passent, dont les nouveaux
cas de libellé, de focus, d'état explicite et de renommage hors service. La
commande de couverture étendue aux deux écrans du personnel exécute 63 cas UI
et mesure 97,97 % des lignes et 94,69 % des branches. Le seuil de 80 % est conservé.
Le job de couverture JavaScript est configuré pour ces mêmes cinq suites UI.
Le rapport local inclut `labs.mjs`, `booking.mjs` (suggestion IA comprise),
`staff_bookings.mjs` et `staff_catalogue.mjs`. Le cas de
`tests/test_runner.test.mjs` vérifie le lanceur de `npm test` et fait partie
de ses 64 cas Node. La mesure UI compte 63 cas.

Le contrôle Django, `git diff --check`, ex2 (32/32) et MCP TP1 (12/12) passent.
Les 28 cas ciblés repassent après la revue et couvrent les deux nouveaux
refus 401. Ex3 reconnaît AC-10 à AC-12 et affiche 15/18. Le lancement de npm
sous Windows, AC-43 à AC-45 et la note d'architecture personnelle restent
signalés par le vérificateur.

## Vérifications locales du lot AC-6 à AC-8

La couverture PostgreSQL a exécuté 568 cas et 9 tests Python TP1. Le garde
SQLite a été exécuté séparément. Les services atteignent 394/394 lignes et
120/120 branches. La mesure globale compte 1 963/2 211 lignes (88,78 %) et
470/536 branches (87,69 %), avec le serveur TP1 et les deux anciens bancs
Python ignorés dans `.local/` détectés par la configuration existante.

Le contrôle Django, `git diff --check`, ex2 (32/32), le garde SQLite isolé et
le contrôle MCP TP1 (12/12) passent. La suite Node compte 60 réussites, dont
9 pour le catalogue. La mesure locale des modules UI, avec les deux écrans du
personnel, atteint 97,80 % des lignes et 94,65 % des branches (59 cas, seuil de
80 % des lignes). Le module du catalogue atteint 97,89 % des lignes.

La revue indépendante a demandé une preuve du tri sur plusieurs laboratoires
et postes. L'assertion vérifie désormais leur ordre par identifiant. Les 23 cas
PostgreSQL du catalogue et des réservations ont repassé après cet ajout. À ce stade,
seule la mesure locale incluait le catalogue. La publication de l'espace du
personnel étend le job de couverture aux deux écrans.

Ex3 reconnaît AC-6 à AC-8 et affiche encore 15/18. La commande automatique
`npm` rencontre `spawnSync npm ENOENT` sous Windows. Le vérificateur relève
encore AC-10, AC-12, AC-43 à AC-45 et l'absence de note personnelle.

## Repères dans le code

- `base.html` relie les écrans du personnel. `staff_catalogue.html` fournit les formulaires et le jeton CSRF. `staff_catalogue.mjs` appelle l'API et met les fiches à jour. `app.css` définit leur présentation et leur focus.
- `urls.py` associe les URL à `routes/staff_catalogue.py`. `session.py` garde une destination de retour interne, `pages.py` contrôle les écrans et `booking_http.py` traduit les erreurs d'API.
- `services/access.py` partage le contrôle du rôle entre les écrans et les services. `staff_bookings.py` réutilise cette règle côté route et côté service. `services/staff_catalogue.py` valide chaque nom avant d'appeler `data/staff_catalogue.py`, qui lit ou modifie les lignes par l'ORM.
- `test_staff_catalogue.py` vérifie les réponses et les lignes PostgreSQL. `test_workstation_state_concurrency.py` observe les deux ordres de verrouillage. Les tests DOM vérifient les actions et les historiques. `SPEC.md`, `UI.md`, `AGENTS.md` et `AGENT_LOG.md` conservent la portée, les commandes et les preuves.

## Questions pour relire le code

- Quelle valeur la requête envoie-t-elle pour que sa répétition conserve le même état ?
- Pourquoi le changement d'état verrouille-t-il la même ligne que `create_booking` ?
- Comment les historiques affichent-ils l'état actuel du poste tout en conservant le statut de la réservation ?
