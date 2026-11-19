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

Les écritures utilisent la base du serveur démarré. Sur la machine d'essai, le
banc local ignoré permet de rejouer les mêmes étapes sur une base en mémoire.

```powershell
.\.venv\Scripts\python.exe .local/ui-staff-catalogue-audit.fixture .local/ui-staff-catalogue-manuel.stop
```

Ouvrir <http://127.0.0.1:8013/__catalogue_test__/enter> pour obtenir la session
synthétique, puis arrêter le processus avec Ctrl+C après l'essai.

## Contrat et preuves PostgreSQL

| Méthode et route sous `/api/staff/catalogue` | Effet |
| --- | --- |
| `GET` sur la racine | Laboratoires avec leurs postes, triés par identifiant. |
| `POST` sur la racine | Crée un laboratoire. Réponse 201. |
| `PATCH /laboratories/{lab}` | Renomme le laboratoire. Réponse 200. |
| `POST /laboratories/{lab}/workstations` | Crée le poste dans ce laboratoire. Réponse 201. |
| `PATCH /laboratories/{lab}/workstations/{poste}` | Renomme le poste sous ce parent. Réponse 200. |

Chaque écriture reçoit un objet JSON avec `name` et un jeton CSRF. Le service
vérifie le rôle actif `personnel` et valide le nom après retrait des espaces
aux extrémités. La couche de données utilise les tables existantes. Le renommage
met à jour uniquement le nom. La contrainte PostgreSQL du poste refuse un nom
identique dans le même laboratoire avec un 409 et permet le même nom ailleurs.
Le nom du laboratoire conserve les règles du modèle existant.

`tests/test_staff_catalogue.py` vérifie la création d'une seule ligne par action,
les identifiants stables et le rattachement après rechargement. Une session
étudiante avec jeton valide reçoit 403 sur chacune des quatre écritures, y
compris si `is_staff` est actif. Les lignes et le rôle sont comparés avant et
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
démonstration a été préservée. La mise en service et la mise hors service
relèvent d'une tranche suivante.

## Vérifications locales

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
PostgreSQL du catalogue et des réservations ont repassé après cet ajout. Le job de
couverture JavaScript de la CI devra inclure le catalogue avant une future
publication. La mesure locale couvre déjà ce périmètre.

Ex3 reconnaît AC-6 à AC-8 et affiche encore 15/18. La commande automatique
`npm` rencontre `spawnSync npm ENOENT` sous Windows. Le vérificateur relève
encore AC-10, AC-12, AC-43 à AC-45 et l'absence de note personnelle.

## Repères dans le code

- `base.html` relie les écrans du personnel. `staff_catalogue.html` fournit les formulaires et le jeton CSRF. `staff_catalogue.mjs` appelle l'API et met les fiches à jour. `app.css` définit leur présentation et leur focus.
- `urls.py` associe les URL à `routes/staff_catalogue.py`. `session.py` garde une destination de retour interne, `pages.py` contrôle les écrans et `booking_http.py` traduit les erreurs d'API.
- `services/access.py` partage le contrôle du rôle entre les écrans et les services. `staff_bookings.py` réutilise cette règle côté route et côté service. `services/staff_catalogue.py` valide chaque nom avant d'appeler `data/staff_catalogue.py`, qui lit ou modifie les lignes par l'ORM.
- `test_staff_catalogue.py` vérifie les réponses et les lignes PostgreSQL. `staff_catalogue_ui.test.mjs` vérifie les formulaires et les transitions DOM. `SPEC.md`, `UI.md`, `AGENTS.md` et `AGENT_LOG.md` conservent la portée, les commandes et les preuves.

## Questions pour relire le code

- Où le rôle du compte et le jeton CSRF sont-ils contrôlés ?
- Quelle opération de données permet de renommer un poste en gardant son laboratoire ?
- Comment le service distingue-t-il un nom en double d'une autre erreur de base ?
