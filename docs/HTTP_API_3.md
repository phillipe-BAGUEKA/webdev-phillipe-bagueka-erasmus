# Jalon 3 — API HTTP, sans interface

État initial propre : 39bb68f3255f75a2713b79b988873050798be4e7.
Contrats consignés avant implémentation. Services 2A/2B/2D réutilisés sans
dupliquer leurs règles. Acteur exclusivement construit depuis la session Django.
Pas de modèle, migration, donnée de démonstration, dépendance, CI, MCP ou IA.

## Contrats retenus

| Méthode et chemin | Entrée | Succès |
| --- | --- | --- |
| GET /api/labs/{id}/availability | Un seul paramètre date=YYYY-MM-DD | 200, {"slots": [...]} |
| GET /api/bookings | Aucun paramètre | 200, {"bookings": [...]} |
| POST /api/bookings | Objet JSON : workstation_id entier positif, starts_at et ends_at ISO 8601 avec T et fuseau explicite | 201, {"booking": {...}} |
| POST /api/bookings/{id}/cancel | Objet JSON vide {} | 200, {"booking": {...}}, y compris répétition autorisée |

Champs JSON exactement ceux indiqués ; champs inconnus ou propriétaire fourni
refusés en 422. Aucun paramètre supplémentaire, y compris un owner_id, accepté.
Les dates sont sérialisées explicitement en UTC, suffixe Z. Les slots ne donnent
que workstation_id, workstation_name, starts_at et ends_at, aucune identité ni
réservation d'autrui. Historique : id, workstation_id/name, laboratory_id/name,
starts_at, ends_at, created_at, cancelled_at, is_operational et status.
Création/annulation : id, workstation_id, starts_at, ends_at, created_at et
cancelled_at (null pour création). Aucun owner_id client n'est jamais utilisé.

## Erreurs et ordre des contrôles

Format stable conservé : {"error": "message lisible"}, sans détail SQL ni traceback.

- 401 : session absente, invalide, expirée ou acteur inactif.
- 403 : personnel à la création, autre propriétaire à l'annulation ; CSRF refusé.
- 404 : laboratoire, poste ou réservation inexistant.
- 409 : conflit de poste/personnel, quota, poste hors service, annulation trop
  tardive ou BookingChanged.
- 422 : forme invalide, date/créneau invalide, y compris début non futur.
- 400 : JSON syntaxiquement mal formé ou encodage UTF-8 invalide.
- 405 : méthode non autorisée, avec Allow (GET ; GET, POST ; ou POST).
- 415 : Content-Type différent d'application/json pour les mutations ; paramètre
  charset=utf-8 accepté. Un corps vide n'est pas un objet JSON valide.
- 500 : erreur inattendue, message générique ; jamais un conflit inventé.

Le middleware CSRF peut refuser avant la vue. Un POST sans session muni d'un
CSRF valide obtient 401 ; sans CSRF valide, il peut obtenir 403 d'abord. Avec
CSRF valide : méthode, authentification, forme, puis service métier. Aucun GET
ne modifie les données métier. Les refus CSRF des nouvelles routes sont JSON
même avec Accept: text/html ; les formulaires HTML existants sont préservés.

## Périmètre Slice 2 et arrêt

Périmètre technique livré par étapes : disponibilité, création pour soi,
historique et annulation propriétaire sur PostgreSQL. Références existantes :
AC-11 et AC-13 à AC-28 ; sécurité des sessions reliée à AC-46/49 lorsque prouvée.
Ce jalon ajoute la preuve HTTP aux preuves directes, sans déclarer les écrans
validés ni modifier les critères. Le regroupement définitif de Slice 2 reste à
valider par l'étudiant. Aucune nouvelle formulation personnelle n'est attribuée
à celui-ci ; sa note d'architecture reste à écrire par lui.

Rédaction, contrats détaillés et tests proposés avec l'aide de Codex. Arrêt avant
le jalon interface. Commit local autorisé après tests et revue, aucun push.

## Vérifications HTTP reproductibles et chemins utiles

Les tests isolés préparent leurs propres comptes, sessions et données, sans lire
les mots de passe étudiants ni écrire dans la base de développement :

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_booking_api.py --ds=tests.settings_postgres --reuse-db -v
.\.venv\Scripts\python.exe tools/check_coverage.py --postgresql
```

Vérification manuelle minimale, sans créer de données : si ton ancien serveur
utilise --noreload, arrête-le dans son terminal avec Ctrl+C puis démarre le code
actuel avec PostgreSQL explicite (ne lance pas les nouvelles API sur SQLite) :

```powershell
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --settings=src.config.postgres --insecure --noreload
```

Dans un autre terminal, `curl.exe -i http://127.0.0.1:8000/api/bookings` doit
retourner 401 JSON « Connexion requise. ». Un POST sans jeton est refusé 403,
même sans session. Les essais authentifiés 201/200 sont automatisés sur la base
de test ; aucun compte PostgreSQL de développement n'est implicitement préparé.
Un client authentifié doit obtenir le cookie CSRF via le formulaire existant,
puis transmettre sa valeur par X-CSRFToken et conserver son cookie de session.

Inventaire pour ta future note personnelle, sans la rédiger à ta place :

| Entrée | Routes | Services | Accès aux données |
| --- | --- | --- | --- |
| Disponibilités/historique | src/routes/bookings.py | src/services/booking_reads.py | src/data/booking_reads.py |
| Création | src/routes/bookings.py | src/services/booking_creation.py | src/data/booking_creation.py et booking_reads.py |
| Annulation | src/routes/bookings.py | src/services/booking_cancellation.py | src/data/booking_cancellation.py et verrous booking_creation.py |

Résolution : src/config/urls.py. Acteur de session : src/routes/session.py.
Forme, sérialisation et statuts : src/routes/booking_http.py. CSRF : middleware
Django conservé et adaptation ciblée src/routes/pages.py. Aucun ORM ajouté aux routes.

## Premiers résultats effectivement obtenus

Première intégration : 46 réussites et un échec de dispositif de test. Le client
Django omettait Content-Type lorsque le corps était vide, produisant 415 au lieu
du 400 attendu pour un JSON vide avec son en-tête présent. Le test envoie
désormais explicitement l'en-tête WSGI ; aucun statut n'a été affaibli.
Série complétée : 50 tests réussis en 1,17 s, vrais services et base PostgreSQL.
Seules injections : une panne DatabaseError pour vérifier 500 sans détail SQL,
et un changement d'indice de poste pour faire refuser réellement le service
BookingChanged. Aucune décision métier ni succès n'est remplacé par un mock.
Sortie locale ignorée : `.local/http-api-tests.txt`.

## Mesures finales et limites

Le lanceur inchangé `tools/check_coverage.py --postgresql` a réussi :

- 316 tests pytest réussis, un désélectionné, aucun ignoré, en 121,28 s ;
- 9 tests TP1 réussis en 13,323 s ; régressions TP2, 2C et 2D conservées ;
- services : 220/220 lignes et 74/74 branches (100 % chacune) ;
- adaptateurs nouveaux : booking_http 83/83 lignes et 20/20 branches ; bookings
  32/32 lignes et 4/4 branches ; ceci n'est pas une couverture du navigateur ;
- global Python, TP1 inclus : 1206/1283 lignes (94,00 %), 290/320 branches
  (90,625 %) ;
- inventaire : 49 fichiers de production, aucun absent ; réglages, migrations,
  outils et serveur TP1 inclus. Aucun seuil ni périmètre réduit.

Exclusions inchangées : tests, dépendances, fichiers générés et locaux. La seule
désélection PostgreSQL reste `test_guard_refuses_unmarked_or_wrong_database`,
dont l'assertion d'acceptation historique est spécifique à SQLite et inchangée,
exécutée en 1A sur ce moteur. Aucune mesure SQLite du jalon 3.
Rapport ignoré : `.local/coverage/f46e825e705047a2853571099f8f6381/coverage.json`.
Sortie brute ignorée : `.local/coverage-api-3.txt`.

Revue indépendante en lecture seule : aucun problème bloquant ou important.
L'alerte initiale sur un Cache-Control manquant lors du refus CSRF a été retirée :
csrf_failure avait déjà @never_cache, confirmé par les tests. Aucun correctif de
production demandé par le reviewer, aucun affaiblissement de protection.
Les vérifications ne valent ni validation UI/mobile, ni CI distante, ni MCP.
Le contrôle à 380 pixels reste reporté. Le regroupement définitif Slice 2 et la
note personnelle d'architecture restent ouverts ; pas d'autre formulation de
critère nécessaire pour les contrats HTTP déjà décidés et implémentés ici.

Contrôle Django avec tests.settings_postgres : aucun problème ; ex2 : 32/32 ;
diff vérifié sans erreur. Empreintes SQLite/marqueur/migration initiale conservées,
services et accès aux données inchangés. Profils privés, journaux de tests,
rapports de couverture, bases locales et .venv restent ignorés et non suivis.
Aucun secret lu pour le compte rendu, affiché ou destiné au commit.
