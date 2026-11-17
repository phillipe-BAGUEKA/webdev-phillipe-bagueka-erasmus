# MCP — sous-étape 1 : mode projet et session

État historique de la sous-étape 1. Depuis, la rotation du mot de passe du rôle
de test a été effectuée et vérifiée, et les deux consultations ont été ajoutées
au mode projet. État courant : [MCP_READS_2.md](MCP_READS_2.md). Les résultats et
limites ci-dessous restent ceux de la sous-étape 1, sans réécriture des preuves.

## Périmètre réalisé

Le mode par défaut `python mcp-server/server.py` reste autonome, sans import
Django, accès PostgreSQL ou lecture de profil de développement. Le mode
`--project` initialise explicitement Django, exige PostgreSQL et les sessions
en base, puis vérifie la connexion. Il conserve les deux outils TP1 et leur
handshake ; **aucun des quatre outils projet n'est encore ajouté**.

Chemin d'authentification prévu pour leur futur dispatch :
`project_runtime.current_actor()` → `services.session_auth.authenticate_session`
→ `data.session_auth.session_identity` → backend de session et `get_user` Django
→ `Actor`. Ce point d'entrée n'est pas un nouvel outil ou une méthode RPC.
Chaque invocation relit la variable et une nouvelle session/utilisateur ;
aucun acteur n'est conservé entre les appels.

L'adaptateur fournit à `get_user` uniquement son contexte de session, sans
fabriquer de requête HTTP. Django contrôle la signature, l'expiration, le backend,
l'utilisateur et le hash d'authentification. Le SessionStore limité à la lecture
refuse `flush` et `cycle_key` : mot de passe ou clé changés nécessitent une
nouvelle connexion, sans suppression, prolongation ou rotation silencieuse.
Le sel de signature est explicitement celui du backend Django d'origine,
indépendamment du nom de sa sous-classe. Les sessions privilégiées Django sont
refusées ; le rôle métier `personnel` n'est pas le drapeau `is_staff`.

Une déconnexion/suppression de session ou désactivation interdit les appels
suivants. Une révocation ne garantit pas l'arrêt d'une transaction déjà engagée.
Une panne SQL est convertie à l'entrée MCP en `SessionAuthenticationUnavailable`,
sans détail de connexion ni chaînage affichable ; ce n'est ni un acteur, ni un
refus de session invalide, ni un conflit métier. Les futurs outils devront
traduire cette erreur technique en réponse MCP générique.
Le démarrage projet échoue avec un message générique sur stderr si la
configuration/connexion est inutilisable ; stdout reste réservé au JSON-RPC.

## Commandes

Depuis la racine, avec l'instance dédiée 5433 et la base de test déjà préparées :

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_mcp_session_auth.py tests/test_project_mcp.py --ds=tests.settings_postgres --reuse-db --tb=short -q
$env:PYTEST_ADDOPTS = '--tb=short'
.\.venv\Scripts\python.exe tools/check_coverage.py --postgresql
node mcp-server/check.mjs -- .\.venv\Scripts\python.exe mcp-server/server.py
```

Le premier test valide de vraies sessions Django sur `test_lab_booking_1a`.
Le test stdio démarre un sous-processus avec `tests.settings_postgres`, sans
jeton réel hérité, et échange initialize/notification/tools-list/tools-call.
Un autre démarre Python avec `-S` et un module de réglages introuvable pour
prouver que le mode TP1 n'importe pas Django. Un réglage SQLite est refusé par
le mode projet, sans appliquer de migration ni écrire dans la démonstration.

Commande du **futur usage local** (non essayée avec ton client ou ta session) :

```powershell
.\.venv\Scripts\python.exe mcp-server/server.py --project
```

Elle sélectionne `src.config.postgres` par défaut ; les tests imposent leur
propre `DJANGO_SETTINGS_MODULE`. Ce remplacement est destiné au processus de
test : en usage local, ne pas hériter d'un autre module de réglages. Tout réglage
non PostgreSQL ou sans sessions en base est refusé. Sans session, le
handshake/catalogue TP1 reste disponible. L'adaptateur accepte uniquement
`LAB_BOOKING_MCP_SESSION`, jamais
un identifiant d'utilisateur fourni dans les paramètres d'un outil.

## Remise du jeton : limites

Aucun lanceur à saisie masquée n'est livré dans cette sous-étape. Aucun cookie
du navigateur, vrai jeton, compte de démonstration ou mot de passe utilisateur
n'a servi aux essais. Il n'y a pas de connexion automatique ni d'OAuth.
Le transfert manuel prévu dans MCP_PROJECT_PLAN reste une opération locale
sensible : valeur en mémoire/environnement et éventuellement presse-papiers,
accessible aux processus suffisamment privilégiés. La compatibilité avec le
client final n'est pas vérifiée ; ne pas mettre de clé en argument, journal,
configuration suivie ou environnement Windows persistant. Une nouvelle session
nécessitera de redémarrer le client avec sa nouvelle clé.

## Preuves et travaux ouverts

Tests d'abord : échec pertinent `ModuleNotFoundError` sur la première session
absente, puis implémentation. Le premier contrôle d'une vraie session a ensuite
échoué à cause du sel modifié par la sous-classe ; correction de ce sel puis
**28 tests ciblés réussis**. Ils couvrent aussi session inconnue, expirée,
supprimée, corrompue, backend/identifiant/hash absent ou invalide, compte supprimé,
inactif/privilégié, mot de passe changé, rotation avec clé de repli et révocation
entre deux appels dans le même processus. Comparaison des lignes de sessions
avant/après refus et succès ; aucune réparation silencieuse. La connexion est
une vraie connexion Django Client/session, pas un user_id considéré comme preuve.

Le premier essai a rencontré un timeout ; pg_ctl a confirmé que le cluster
dédié était arrêté. Il a été redémarré par l'outil existant, sans provisionnement.
La trace pytest détaillée de cette erreur a exposé le mot de passe du rôle
PostgreSQL de test ; il n'est pas reproduit ici. Traces courtes utilisées ensuite.
Aucune rotation de cet identifiant n'est prétendue effectuée ; sa rotation reste à
examiner séparément avec l'utilisateur, sans interrompre les preuves de code.

Mesure PostgreSQL finale par le lanceur existant : **348 tests réussis, 1 désélectionné**
(`test_guard_refuses_unmarked_or_wrong_database`, spécifique à SQLite), puis
**9 tests TP1 réussis**. Couverture : services **227/227 lignes et 76/76 branches**
(100 % chacune), global Python **1287/1365 lignes (94,29 %)** et **304/336 branches
(90,48 %)**. Les nouveaux modules et le serveur TP1 sont inclus ; inventaire,
exclusions et seuils inchangés. Rapport ignoré :
`.local/coverage/7be6fdc11fd446d3991a98ccd735bd84/coverage.json`.
Le sous-processus TP1 avec `-S` produit un avertissement coverage « No data was
collected » : son environnement sans site-packages sert précisément à prouver
l'autonomie ; les autres sous-processus mesurent effectivement le serveur TP1.
Ce n'est pas une mesure de couverture SQLite ou du rendu navigateur.

Autres résultats : **23 tests Node**, **12/12 contrôles MCP TP1**, **32/32 ex2**,
contrôle Django sans problème. Le test SQLite désélectionné reste exécuté
séparément avec `tests.settings_sqlite_legacy` : **1 réussi**, base temporaire
isolée, pas `data/demo.sqlite3`. Les refus initiaux `spawn EPERM` de Node dans le
bac à sable ont été résolus par relance autorisée hors de celui-ci. Résultats
locaux seulement : CI non modifiée, aucun nouveau résultat GitHub présumé.
AC-37/38 restent partiels (socle seulement), AC-39 non réalisé.
Revue indépendante : conversion des erreurs SQL à la frontière MCP et précision
du remplacement de réglages retenues, corrigées ; aucun constat écarté.
La suite de couverture a été relancée après cette correction, avec un nouveau
test qui vérifie l'absence de détail synthétique du pilote dans l'erreur rendue.
Dernière passe ciblée après revue : **29 tests réussis**.
Les outils projet, confirmations d'agent, intégration client, IA, Google,
déploiement, note/revue personnelles et vérifications UI reportées restent ouverts.
SQLite, migrations et instance 5432 sont préservées. Aucun push autorisé ici.
