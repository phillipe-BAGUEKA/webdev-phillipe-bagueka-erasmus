# TP3 — Jalon 1B : schéma PostgreSQL des réservations

Périmètre autorisé par l'utilisateur : modèles, nouvelles migrations, contraintes
PostgreSQL et tests isolés. Aucun service métier, route, écran, MCP, IA ou CI.
Les décisions étudiant uniquement et réannulation propre HTTP 200 sont consignées
dans SPEC.md ; leur application appartient aux prochains jalons.

## Plan actualisé et arrêt

1. 1A enregistré : instance indépendante 5433 et profils privés.
2. 1B : Workstation/Booking, migrations 0002/0003, contraintes et tests de schéma.
3. 2A livré séparément : disponibilités et historique personnel, sans mutation ;
   voir READ_SERVICES_2A.md.
4. 2B construit sur autorisation explicite : création transactionnelle par un
   étudiant actif ; voir CREATION_2B.md. Aucun service d'annulation.
5. 2C autorisé et testé séparément : trois scénarios concurrents AC-22/23/24,
   connexions distinctes et attente de verrou PostgreSQL observée. Voir
   CONCURRENCY_2C.md ; aucune garantie universelle de concurrence n'est inférée.
6. Regroupement définitif des critères Slice 2 et statuts HTTP de refus encore
   ouverts avant les étapes correspondantes ; HTTP et interface restent futurs.
7. MCP/IA/personnel/Google restent des étapes distinctes du projet final.

Ne pas rédiger la note d'architecture personnelle de l'étudiant à sa place.

## Modèles et portée des garanties

Workstation appartient à Laboratory (PROTECT), avec name et is_operational.
Le nom est unique dans son laboratoire. Aucun champ matériel n'est ajouté.
Booking référence User et Workstation (PROTECT), avec starts_at, ends_at,
created_at et cancelled_at nullable. Le dernier champ conserve la ligne annulée.
Les dates sont des colonnes PostgreSQL timestamp with time zone.

Contraintes : fin strictement supérieure au début ; durée exacte d'une heure ;
deux exclusions GiST sur TSTZRANGE(starts_at, ends_at, '[)') : même poste ou même
propriétaire, lorsque cancelled_at IS NULL. Les deux extrémités adjacentes sont
compatibles. Les clés étrangères créent leurs index et les exclusions leurs
index GiST ; aucun index d'optimisation spéculatif n'est ajouté.

Les contraintes ne vérifient pas le rôle étudiant, le quota, les horaires, le
caractère futur, l'état du poste ni la propriété d'une demande d'annulation.
Le modèle seul n'assure aucune sémantique HTTP ou idempotence métier.

## Migrations et comptes

- 0001_initial inchangée.
- 0002_btree_gist active l'extension PostgreSQL trusted.
- 0003_workstation_booking crée tables, relations et contraintes.
- Base de vérification dédiée lab_booking_1b_verify, créée vide par le bootstrap,
  propriétaire lab_booking_1a_dev ; PUBLIC n'a pas accès.
- Toute la chaîne de 18 migrations a été appliquée sur cette base vide.
- Les deux nouvelles migrations ont été appliquées sur lab_booking_1a puis,
  via pytest --reuse-db, sur test_lab_booking_1a.
- Les migrations et l'extension sont appliquées avec les propriétaires non
  administrateurs : btree_gist n'a pas nécessité le bootstrap. Celui-ci n'a servi
  qu'à créer la base de vérification. Aucun privilège Django n'est augmenté.

## Commandes explicites

```powershell
.\.venv\Scripts\python.exe manage.py showmigrations --settings=src.config.postgres
.\.venv\Scripts\python.exe manage.py check --settings=src.config.postgres
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run --settings=src.config.postgres
.\.venv\Scripts\python.exe tools/check_coverage.py --postgresql
```

Le lanceur garde l'inventaire et les exclusions de production, les seuils
100 % lignes/branches des services et 80 % lignes globales, TP1 inclus.
--postgresql sélectionne tests.settings_postgres --reuse-db ; seule la précédente
exception SQLite test_guard_refuses_unmarked_or_wrong_database est désélectionnée.
Les assertions de ce test restent inchangées. Aucun résultat PostgreSQL n'est
déduit de SQLite et aucune couche de compatibilité des contraintes n'est ajoutée.

## Tests historiques et preuves partielles

- Le test de migration initiale inspecte maintenant l'état historique de 0001,
  toujours limité à User/Laboratory, au lieu de demander l'absence des nouvelles
  tables dans le schéma courant. Le test d'identité PostgreSQL vérifie désormais
  la présence des deux nouvelles tables.
- Les tests unitaires de sauvegarde TP2 isolent le garde de schéma, déjà isolé
  partiellement auparavant. Les assertions de sauvegarde et de refus restent
  présentes. Un nouveau test vérifie que le garde réel refuse les nouvelles
  relations avant toute opération. La procédure TP2 n'est pas redirigée vers PG.
- Première suite avant adaptation : 138 réussites, 14 échecs, 1 désélection.
  Les échecs concernent ces anciennes hypothèses de schéma et la lecture des
  arguments pytest par le nouveau parseur du lanceur. main accepte désormais
  une liste d'arguments explicite pour ses tests, sans changer leurs assertions.
- Après adaptation : 67 tests ciblés réussis. Les résultats finaux de couverture
  PostgreSQL et de régressions seront consignés dans AGENT_LOG.md.

Correspondance partielle : AC-14 (types d'instants), AC-15 (ligne valide), AC-16
(intervalle/durée seulement), AC-17/18 (exclusions séquentielles), AC-19 (adjacence),
AC-25/28 (annulation conservée et libération du conflit). Aucun de ces AC n'est
déclaré complètement validé par ces seuls tests. AC-22/23/24 restent non prouvés :
aucune demande simultanée, aucun verrou de service ou quota n'a été testé.

SQLite et 5432 restent préservés. Les tests de la nouvelle tranche nécessitent
PostgreSQL : les commandes/CI historiques SQLite ne sont pas prétendues compatibles
avec 0002/0003. La CI reste inchangée ; son alignement nécessitera une autorisation
ultérieure. Le contrôle 380 pixels reste reporté.

## Résultats locaux finaux

- Couverture exécutée avec --postgresql : 155 tests pytest réussis, un test
  SQLite désélectionné, aucun test ignoré (54,16 s), puis neuf tests TP1 réussis
  (8,881 s). Aucun appel fournisseur.
- Services : 25/25 lignes et 4/4 branches (100 %).
- Global Python : 808/885 lignes (91,30 %), 188/218 branches (86,24 %).
- Les 41 fichiers de production sont inventoriés, nouvelles migrations et
  réglages inclus. Exclusions et seuils inchangés ; aucune mesure SQLite 1B.
- Rapport brut local ignoré :
  .local/coverage/2f42e953a1ab4854a38829bb823764e6/coverage.json.
- Tests de contraintes seuls : 19 réussites ; tests JavaScript existants : 7/7.
- Trois bases dédiées migrées : développement, test précréé, vérification vide.
  Les tables métier et sessions de développement/vérification restent vides.
  Aucun rôle Django n'a SUPERUSER, CREATEDB ou CREATEROLE.
- Contrôles Django et dérive des migrations réussis ; 0001 et les empreintes
  SQLite/marqueur sont inchangés. Aucun secret/profil n'est destiné au commit.
- Revue indépendante : aucun problème bloquant/important ; précision du type
  Catalogue retenue dans les tests. Documentation et journal finalisés après revue.
- Aucun push, résultat CI distant, scénario concurrent ou validation mobile ajouté.

Références techniques : documentation Django 5.2 des contraintes PostgreSQL et
documentation PostgreSQL 16 de btree_gist (extension trusted installable par le
propriétaire non administrateur disposant de CREATE sur la base).
