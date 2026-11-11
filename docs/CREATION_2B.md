# Jalon 2B — création transactionnelle

## Périmètre consigné avant le code

État initial propre au commit 470a7ef. Autorisation : création par un étudiant
actif, service indépendant du transport, accès aux données, transaction et tests
directs PostgreSQL. AC-11 et AC-13 à AC-21 sont concernés partiellement : les
parcours HTTP et visuels restent absents. Aucun critère approuvé n'est réécrit.

Plan : tests de refus d'abord, constat rouge, implémentation, régressions et
couverture PostgreSQL, revue indépendante et commit local. Verrous dans l'ordre
utilisateur puis poste ; relecture des données et de l'heure avant décision.
Les disponibilités de 2A ne constituent jamais une autorisation de création.

Hors périmètre : annulation, HTTP, UI, MCP, IA, migrations, dépendances, CI,
données de démonstration, SQLite et instance 5432. La concurrence avec plusieurs
connexions relève de 2C ; le regroupement définitif Slice 2 et la note personnelle
d'architecture restent ouverts. La rédaction et le code proposés sont de Codex,
à partir des décisions de l'étudiant, sans validation professorale présumée.

## Contrat et chemin des données

`create_booking(actor, workstation_id, starts_at, ends_at, *, clock=None)` retourne
un `CreatedBooking` immuable : booking_id, owner_id, workstation_id, starts_at,
ends_at et created_at. Les dates sont conscientes du fuseau, normalisées en UTC.
Il n'existe aucun argument permettant de choisir un autre propriétaire.
L'acteur est fourni par un adaptateur authentifié de confiance, jamais construit
directement à partir d'un JSON client. Le compte réel est relu sous verrou : un
acteur périmé n'accorde aucun rôle ou accès que la base ne confirme plus.

Service → contexte transactionnel de données → verrou utilisateur → verrou
poste → horloge courante → validations métier → requêtes de conflits/quota →
insertion ORM → résultat immuable. Aucun ORM dans le service, ni requête HTTP/MCP.
Le protocole de verrouillage est préparé pour 2C, pas démontré concurrent ici.
Les futurs chemins d'écriture devront respecter ce même ordre commun.

`clock` est une fonction appelée après les verrous ; l'omettre utilise l'heure
Django. Les tests contrôlent cette fonction, y compris une heure devenue égale
au début demandé après acquisition des verrous. La durée est exactement une
heure et le début est une heure entière entre 08:00 et 17:00, du lundi au
vendredi Europe/Sofia. Aucun horizon ou règle supplémentaire n'est ajouté.
Les comptages et lectures de conflits sont réutilisés depuis l'accès aux données
de 2A, et exécutés de nouveau dans la transaction de création.

## Refus explicites

- `AuthenticationRequired` : acteur absent/inactif ou compte disparu/inactif.
- `StudentRequired` : rôle courant différent d'étudiant.
- `WorkstationNotFound`, `WorkstationUnavailable` : poste absent/hors service.
- `InvalidBookingInput` : identifiant, date, horloge ou créneau non conforme.
- `SlotNotFuture` : début inférieur ou égal à l'heure relue.
- `WorkstationConflict`, `PersonalConflict` : chevauchement non annulé.
- `QuotaExceeded` : déjà trois réservations futures non annulées.

Les erreurs de création héritent de `BookingError`, sauf l'erreur authentifiée
déjà partagée. Leur traduction HTTP reste future. Les deux contraintes
d'intervalle connues et les deux exclusions sont reconnues par leur nom **et**
leur SQLSTATE. La couche de données laisse d'abord sortir le bloc atomique pour
rollback, puis signale la contrainte au service. Une autre erreur d'intégrité
reste une erreur de base, sans devenir arbitrairement un conflit métier.

## Commandes et portée

Depuis la racine, avec l'instance dédiée déjà opérationnelle :

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_booking_creation.py --ds=tests.settings_postgres --reuse-db -v
.\.venv\Scripts\python.exe tools/check_coverage.py --postgresql
.\.venv\Scripts\python.exe manage.py check --settings=src.config.postgres
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run --settings=src.config.postgres
```

La couverture conserve tout l'inventaire Python de production, TP1, réglages,
migrations et outils compris. Exclusions inchangées : tests, dépendances,
répertoires générés/locaux. Seuils inchangés : services 100 % lignes et branches,
global au moins 80 % lignes. Aucune mesure SQLite de 2B. La seule désélection
PostgreSQL est `test_guard_refuses_unmarked_or_wrong_database` : son assertion
d'acceptation d'une cible SQLite historique n'est pas applicable à PostgreSQL ;
elle reste inchangée et a été exécutée dans la suite SQLite de 1A. Pas d'autre
test métier ignoré pour obtenir une réussite.

## Preuves de développement

- Rouge avant implémentation : le premier refus AC-15 échoue avec
  ModuleNotFoundError, car le service n'existe pas encore.
- Première série : 30 tests directs réussis. Série étendue : 51 réussites et
  deux échecs dans les dispositifs de test. PostgreSQL rapporte one_hour avant
  positive_interval pour un intervalle nul ; le gestionnaire User valide déjà
  l'unicité avant l'INSERT. Les règles et assertions métier sont conservées :
  diagnostic positive_interval simulé explicitement, doublon inséré par l'ORM
  sans le gestionnaire pour provoquer réellement l'erreur de base non liée.
- Série directe corrigée : 55 tests réussis en 2,14 s. Les violations one_hour
  et les deux exclusions sont réelles sur PostgreSQL ; positive_interval est
  un diagnostic simulé, sans suppression de contrainte. Aucun essai concurrent.
- Test du protocole : ordre utilisateur → poste → horloge observé dans la
  transaction ; début devenu égal à maintenant refusé. Il ne simule pas une
  attente réelle entre connexions, prévue en 2C.
- Django : aucun problème, aucune dérive modèles/migrations. Aucun migrate.
- `node checks/ex2.mjs` : 32/32 après relance autorisée hors bac à sable ; le
  premier lancement était bloqué par EPERM sur un ancien cache pytest local.

## Régression et couverture réellement mesurées

Le lanceur inchangé `tools/check_coverage.py --postgresql` a réussi :

- 231 tests pytest réussis, un seul désélectionné, aucun ignoré, en 184,09 s ;
- 9 tests unittest du serveur TP1 réussis en 17,942 s ;
- services : 168/168 lignes et 56/56 branches (100 % chacune) ;
- nouveau service : 65/65 lignes et 22/22 branches ;
- nouvel accès aux données : 43/43 lignes et 6/6 branches ;
- global : 1009/1086 lignes (92,91 %), 246/276 branches (89,13 %) ;
- inventaire de 45 fichiers de production, aucun absent, aucune exclusion ajoutée.

Rapport local ignoré :
`.local/coverage/a2fa736a234645a98a8e35d58fadad6a/coverage.json`.
Journal brut local : `.local/coverage-2b-final.txt`.
Le pourcentage combiné lignes/branches de coverage n'est pas le pourcentage
global des lignes ; les chiffres ci-dessus distinguent les deux mesures.

Les empreintes SHA-256 de demo.sqlite3, demo.marker et 0001_initial sont inchangées.
Aucune migration, configuration CI, dépendance ou donnée de démonstration modifiée.
Les profils dédiés demeurent ignorés et non suivis ; leurs nouvelles valeurs
autorisées n'apparaissent dans aucun candidat Git. Aucun secret préexistant lu.
Le contrôle à 380 pixels reste reporté. Aucun résultat distant ni concurrence
n'est revendiqué. Arrêt avant 2C ; aucun push autorisé pour ce jalon.

Revue indépendante en lecture seule par l'agent personnalisé reviewer : aucun
constat bloquant ou important. Sa demande de consigner les chiffres définitifs
et de maintenir les limites 2C est retenue ci-dessus. Aucun constat écarté,
aucune correction de code demandée. Les contrôles du diff indexé et des valeurs
sensibles sont réalisés séparément avant le commit local.
