# TP3 — Jalon 1A : instance PostgreSQL dédiée

État au 11 novembre 2026, préparation avec Codex. Ce jalon utilise les binaires
PostgreSQL 16.4 déjà installés, Python 3.13.7, Django 5.2.18 et Psycopg 3.3.8.
Aucune installation supplémentaire pendant la création de l'instance.

## Isolation et fichiers locaux

- Instance privée : %LOCALAPPDATA%\LabBooking\PostgreSQL16, utilisateur Windows
  courant, UTF-8, écoute uniquement 127.0.0.1:5433, cluster_name=lab_booking_1a.
- Initialisation SCRAM-SHA-256 pour les accès locaux et TCP, sans trust.
- Aucun service Windows ajouté. L'instance existante sur 5432 n'est pas modifiée.
- Base de développement lab_booking_1a, propriétaire lab_booking_1a_dev.
- Base de test précréée test_lab_booking_1a, propriétaire lab_booking_1a_test.
- Les deux rôles applicatifs sont LOGIN, NOSUPERUSER, NOCREATEDB, NOCREATEROLE,
  NOINHERIT, NOREPLICATION, NOBYPASSRLS. PUBLIC n'a pas de droit sur ces deux
  bases ; les essais croisés entre rôles/bases sont refusés.
- Le bootstrap reste distinct des comptes utilisés par Django.

Profils locaux ignorés, non suivis, à ne jamais afficher ou publier :

| Chemin relatif au dépôt | Rôle |
| --- | --- |
| .local/postgres-1a-bootstrap.json | Administration du seul cluster dédié |
| .local/postgres-1a-dev.json | Connexion Django de développement et nouvelle clé locale |
| .local/postgres-1a-test.json | Connexion des tests PostgreSQL et clé technique distincte |

Les fichiers sont créés vides, leur héritage ACL est retiré et l'accès accordé
au SID Windows courant avant écriture. Les mots de passe applicatifs sont
aléatoires et distincts. Le mot de passe bootstrap explicitement autorisé par
l'utilisateur n'est pas reproduit ici. Aucun secret antérieur n'a été consulté.
Le fichier temporaire initdb a été supprimé dans finally ; aucun secret nouveau
n'a été trouvé dans les fichiers candidats à Git ni dans le journal du cluster.

## Démarrage, statut, arrêt

Depuis la racine du dépôt, PowerShell :

~~~powershell
.\.venv\Scripts\python.exe tools/local_postgres.py start
.\.venv\Scripts\python.exe tools/local_postgres.py status
.\.venv\Scripts\python.exe tools/local_postgres.py stop
~~~

Après redémarrage de Windows, lancer start puis status : aucun démarrage
automatique n'est installé. Ne pas lancer start si l'instance tourne déjà ;
un échec ou un port occupé n'autorise pas à arrêter un autre processus.
Le statut réalise une connexion authentifiée et vérifie port, cluster et dossier.
L'arrêt fast ferme les connexions du seul cluster dédié ; attendre la fin des tests.

L'action init est une opération initiale, déjà effectuée : ne pas la relancer.
Elle refuse un dossier/profil existant, teste le port, utilise initdb --pwfile
avec un fichier protégé avant écriture et le nettoie même en cas d'erreur.
L'action provision n'est pas un seed : elle refuse les profils/rôles/bases
existants. En cas d'échec partiel, conserver les objets et demander un diagnostic.

## Django : sélection explicite

~~~powershell
.\.venv\Scripts\python.exe tools/local_postgres.py verify
.\.venv\Scripts\python.exe manage.py check --settings=src.config.postgres
.\.venv\Scripts\python.exe manage.py showmigrations --settings=src.config.postgres
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --insecure --noreload --settings=src.config.postgres
~~~

Le runserver est une commande prévue, pas un nouveau parcours navigateur validé.
Aucun compte de démonstration n'est créé : les tables métier de développement
restent vides. Ne pas rediriger seed_demo/demo_labs vers PostgreSQL.
Les réglages SQLite et pytest.ini restent inchangés. PostgreSQL est la sélection
explicite pour la suite ; les futures contraintes ne seront pas rendues portables.

## Migrations et tests

Les 16 migrations existantes ont été appliquées avec src.config.postgres,
dont data.0001_initial inchangée. showmigrations indique [X] pour toutes.
Django check et la recherche de dérive des migrations réussissent.

Commande complète exécutée sur PostgreSQL :

~~~powershell
.\.venv\Scripts\python.exe -m pytest tests --ds=tests.settings_postgres --reuse-db -q --tb=short
~~~

Premier résultat : 118 réussites, un échec en 75,76 s. L'échec est
test_guard_refuses_unmarked_or_wrong_database : il attend que le garde SQLite
accepte un chemin temporaire muni d'un marqueur ; PostgreSQL refuse correctement
ce seed SQLite. Ce test existant reste intact et est exécuté dans la suite SQLite.

Relance des tests applicables, sans modifier cette assertion :

~~~powershell
.\.venv\Scripts\python.exe -m pytest tests --ds=tests.settings_postgres --reuse-db -q --tb=short -k "not test_guard_refuses_unmarked_or_wrong_database"
.\.venv\Scripts\python.exe -m pytest tests --ds=tests.settings -q --tb=short
~~~

Les résultats finaux et la revue sont consignés dans AGENT_LOG.md.
La relance PostgreSQL donne 121 réussites, un test SQLite désélectionné (98,30 s).
La suite SQLite complète donne 121 réussites, un test PostgreSQL ignoré (97,77 s).
Les tests ciblés supplémentaires après revue sont consignés séparément au journal.
--reuse-db est requis : la base de test est précréée et son rôle est NOCREATEDB.
Ne pas utiliser --create-db. Les tests n'utilisent jamais la base de développement.

Les profils sont validés avant connexion ; aucun repli silencieux vers SQLite.
La couverture n'est pas remesurée par cette étape : ses seuils et son périmètre
restent inchangés. Aucune nouvelle migration métier, extension, réservation,
restriction de rôle, modification CI/npm ou publication. Le contrôle à 380 pixels
reste reporté. Ce jalon ne prouve aucun futur comportement de réservation.

## Incident d'exécution corrigé

La première capture des sorties pg_ctl sous Windows attendait la fermeture
de handles hérités par le serveur démarré. L'opération a été interrompue,
ce qui a aussi arrêté ce nouveau cluster. run_pg utilise maintenant DEVNULL ;
le nouveau cluster a été redémarré, identifié, puis provisionné sans réinitialiser
le dossier. Un test protège ce mode de lancement. Rien n'a ciblé le service 5432.

## Cl?ture locale et couverture r?elle

Commande ex?cut?e : `.\.venv\Scripts\python.exe tools/check_coverage.py`.
Le lanceur est inchang?, sans remplacement d'inventaire ou exclusion ajout?e.
Mesure du 11 novembre 2026 sur SQLite de test, pas sur PostgreSQL :

| Mesure | R?sultat |
| --- | --- |
| pytest sous couverture | 134 r?ussites, 1 test PostgreSQL ignor?, 90,48 s |
| Tests TP1 sous couverture | 9 r?ussites, 7,021 s |
| Lignes des services | 25/25, 100 % |
| Branches des services | 4/4, 100 % |
| Lignes globales Python | 767/840, 91,31 % |
| Branches globales Python | 189/216, 87,50 % |
| src/config/postgres.py | 11/11 lignes |
| src/config/postgres_config.py | 20/20 lignes, 4/4 branches |
| tools/local_postgres.py | 85/95 lignes, 16/20 branches |
| tools/setup_postgres.py | 64/72 lignes, 18/20 branches |
| Serveur TP1 | 91/106 lignes, inclus dans le global |

L'inventaire compte 38 fichiers de production sans fichier manquant. Sont
conserv?es les exclusions des tests, environnements/d?pendances et r?pertoires
techniques g?n?r?s. Les r?glages, migrations, outils et chemins non ex?cut?s de
production restent dans le d?nominateur. Le taux combin? lignes/branches affich?
par coverage.py (90,53 %) n'est pas le taux de lignes utilis? pour le seuil.
Rapport local ignor? :
`.local/coverage/f1d8b962758c46b4bd6ca35169b1c908/coverage.json`.

Une premi?re mesure r?ussie donnait 711/840 lignes. Douze tests suppl?mentaires
v?rifient les connexions synth?tiques, privil?ges des r?les g?n?r?s, sorties sans
secret, distribution des commandes et imports explicites des r?glages. Ils
r?ussissent sous SQLite (12/12) et avec les r?glages PostgreSQL (12/12), sans
provisionnement r?el. Ces simulations ne deviennent pas une mesure de couverture
PostgreSQL : les r?gressions PostgreSQL r?elles ant?rieures restent distinctes.

Le seul test d?s?lectionn? dans la r?gression PostgreSQL est
`tests/test_demo_data.py::test_guard_refuses_unmarked_or_wrong_database`.
Son assertion sp?cifique au chemin/marqueur SQLite reste ex?cut?e et r?ussie dans
la suite SQLite compl?te ; elle n'a ?t? ni modifi?e ni marqu?e skip.
Le test ignor? sous SQLite est `test_postgresql_identity_and_existing_schema`.

La revue ind?pendante de cl?ture n'a trouv? aucun blocage. Son constat de test
n?gatif manquant a ?t? ?cart? apr?s inspection :
`test_same_named_cluster_in_other_directory_is_refused` v?rifie d?j? le refus
avant profils/DDL quand le port et le nom correspondent mais pas le dossier.
Aucun r?sultat GitHub Actions n'est revendiqu? pour cette cl?ture locale.
Aucun provisionnement, transfert ou test de concurrence n'a ?t? rejou?.
