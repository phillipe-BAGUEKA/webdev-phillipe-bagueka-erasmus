# TP 2 — préparation locale avant publication

État au 4 novembre 2026, préparé avec l’aide de Codex. La spécification et la première tranche de Lab booking sont présentes ; cette étape aligne les documents et la CI, sans commencer une autre tranche. Aucun commit ni push n’est effectué. Les résultats ci-dessous sont **locaux sous Windows**, pas des exécutions GitHub Actions.

## Réalisé, observé et encore prévu

| Élément | État et source de la preuve |
| --- | --- |
| Utilisateur par e-mail, laboratoires, migrations initiales, sessions Django | Construits ; tests isolés exécutés. L’utilisateur a rapporté la préparation personnelle des mots de passe et les contrôles du socle. |
| Connexion, protection de la page/API, déconnexion et ancien cookie | Tests exécutés. L’utilisateur a confirmé le parcours local et le clavier avec focus visible. |
| Liste chargée par fetch depuis SQLite | Codex a observé Alpha, Beta et Gamma dans Edge sur l’instance réelle après correction du MIME et du cache. |
| AC-48 | Codex a observé **3 → 2 → 3** dans Edge, puis comparé Beta restauré à sa sauvegarde : même id et tous les champs identiques. Pas de nouvelle manipulation pendant la finalisation. |
| API après déconnexion, retour utilisateur | Corps `{"error": "Connexion requise."}`, sans laboratoire. Ce texte seul ne prouve pas le statut HTTP ; les tests isolés vérifient séparément 401. |
| Affichage à 380 pixels | Reporté par l’utilisateur, non validé. Aucune conformité mobile globale revendiquée. |
| Postes, réservations, personnel, Google, IA, PostgreSQL et nouveaux outils MCP | Spécifiés pour la suite ; non construits par cette tranche. Les deux outils TP1 restent inchangés. |
| CI distante et publication | Workflow adapté localement ; premier résultat GitHub Actions encore à confirmer après publication autorisée. |

Les critères AC-46 à AC-49 ont des preuves automatisées ; les observations manuelles restent attribuées à leur auteur dans SPEC.md et CHECKPOINT3.md. Cela ne certifie ni la compréhension personnelle de l’étudiant ni l’acceptation pédagogique du professeur. Les questions de compréhension et challenges sont reportés à la fin du projet à la demande de l’utilisateur.

## Lancement et données

Les commandes de nouvelle installation, migration et préparation masquée des mots de passe figurent dans [CHECKPOINT1.md](CHECKPOINT1.md). Elles ne sont pas rejouées sur les données existantes. [README.md](../README.md) donne le lancement courant et les URL ; [CHECKPOINT3.md](CHECKPOINT3.md) explique le serveur lancé en arrière-plan et le redémarrage nécessaire avec `--noreload`. Les tests utilisent `tests.settings`, une base isolée et une valeur publique de clé de test ; ils ne chargent pas les secrets locaux ni la base de démonstration.

## CI adaptée et contrôles conservés

`.github/workflows/ci.yml` conserve les jobs `test`, `coverage`, `mcp` et `spec`, déclenchés sur push et pull request. Les actions checkout/setup existantes sont conservées. Python est explicitement configuré en **3.13**, cohérent avec la branche locale ; Node reste en **22.x**. Le correctif exact installé par GitHub pourra différer des versions locales. Le conteneur Codespaces existant reste en Python 3.12, non modifié ni validé ici.

- `test` installe `requirements.txt` et `requirements-dev.txt`, vérifie les dépendances et Django avec les réglages isolés, contrôle la dérive des migrations sans les écrire, exécute pytest, conserve `npm test` pour les neuf tests TP1 et lance explicitement les tests JavaScript existants.
- `coverage` réutilise sans modification `tools/check_coverage.py` et `.coveragerc`. Le lanceur exécute pytest et les tests TP1 sous coverage.py, combine les sous-processus, contrôle l’inventaire de production et refuse les tests en échec ou les seuils non atteints.
- Les seuils bloquants sont **100 % des lignes et branches des services Python**, puis **au moins 80 % des lignes Python globales**. L’ancien passage Node sur des services JavaScript inexistants est remplacé par la mesure des services réellement écrits en Python. Le seuil JavaScript existant de 80 % des lignes est conservé séparément. Il ne devient pas une preuve de couverture de tous les fichiers frontend.
- Le vérificateur MCP original reste exécuté avec `npm run --silent mcp`, sous un Python explicitement choisi. Le contrôle `node checks/ex2.mjs` et l’historique Git complet de son job sont conservés. Le contrôle conditionnel de construction Docker est conservé ; aucun Dockerfile n’existe encore et aucun build Docker n’est revendiqué.
- Les anciennes sorties « No project yet » ne permettent plus d’ignorer l’application désormais présente. Aucun `continue-on-error`, seuil abaissé ou test affaibli n’est ajouté. Aucun pytest-cov ou autre paquet supplémentaire n’est installé ; les deux fichiers de dépendances existants sont la référence.

Référence officielle consultée pour cette adaptation : [construction et tests Python avec GitHub Actions](https://docs.github.com/en/actions/tutorials/build-and-test-code/python) (4 novembre 2026). L’exécution des commandes sous Windows ne valide pas l’installation réseau des dépendances ni le workflow complet sur Ubuntu.

## Commandes et résultats locaux

Depuis la racine, avec Python **3.13.7**, Node **22.12.0**, Django **5.2.18**, coverage.py **7.17.1** déjà installés. Aucune installation effectuée pendant cette finalisation.

| Commande exécutée | Résultat réel |
| --- | --- |
| `.\.venv\Scripts\python.exe -m pip check` | Aucun conflit. |
| `.\.venv\Scripts\python.exe manage.py check --settings=tests.settings` | Aucun problème, 0 masqué. |
| `.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run --settings=tests.settings` | Aucun changement détecté ; aucune migration écrite/appliquée. |
| `.\.venv\Scripts\python.exe tools/check_coverage.py` | **105 tests pytest réussis** en 61,35 s, puis **9 tests TP1 réussis** en 8,603 s ; seuils atteints, code 0. |
| `node --test --experimental-test-coverage --test-coverage-include='src/**' --test-coverage-exclude='tests/**' --test-coverage-lines=80 tests/labs_ui.test.mjs` | **7/7 tests réussis**, code 0 ; module labs.mjs : lignes 97,26 %, branches 95,65 %, fonctions 100 %. |
| `node mcp-server/check.mjs -- .\.venv\Scripts\python.exe mcp-server/server.py` | **12/12 contrôles réussis**, code 0 ; équivalent Windows du lancement Python employé par le script npm en CI. |
| `node checks/ex2.mjs` | **32/32 contrôles réussis**, code 0, exécuté hors du bac à sable après les blocages de lecture connus sur les répertoires temporaires pytest. |
| `git diff --check` | Code 0, aucune erreur d’espacement signalée. |

La suite Python a d’abord terminé avec 88 succès et 17 erreurs de préparation dues aux permissions du répertoire temporaire pytest dans le bac à sable, code 1. Les commandes Node ont d’abord rencontré `spawn EPERM`. Les mêmes vérifications ont ensuite réussi lors des relances autorisées hors de cette restriction, sans modification des assertions ou seuils. Le résultat initial n’est pas masqué.

Le lanceur TP1 parent émet encore `No data was collected` car ses tests sont exclus de la mesure ; les sous-processus du serveur sont néanmoins présents et mesurés dans le rapport combiné. Node 22.12 émet un avertissement expérimental concernant glob. Aucun de ces avertissements n’est supprimé.

## Périmètre de couverture

Rapport brut de cette exécution, local et ignoré : `.local/coverage/8fe5122df5804a579d21ff74c2228c64/coverage.json`. Le lanceur crée un nouveau répertoire à chaque mesure ; il ne réutilise pas les succès d’une précédente exécution.

| Mesure Python | Résultat | Seuil bloquant |
| --- | --- | --- |
| Lignes des services | **25/25 = 100 %** | 100 % |
| Branches des services | **4/4 = 100 %** | 100 % |
| Lignes globales | **587/642 = 91,43 %** | 80 % |
| Branches globales | **151/172 = 87,79 %** | Informatif |
| Lignes du serveur TP1 | **91/106 = 85,85 %** | Incluses dans le global ; exécution obligatoire |

Le tableau standard coverage.py affiche **90,66 %** en combinant lignes et branches : ce n’est pas le pourcentage de lignes utilisé pour le seuil global. Le périmètre Python inclut `src/` (configuration, migrations et commandes comprises), `manage.py`, `tools/` et `mcp-server/server.py`. Les fichiers non exécutés restent dans le dénominateur, notamment réglages locaux, manage.py et WSGI à 0 %. Aucun secret n’est lu pour les couvrir.

Exclusions inchangées dans `.coveragerc` : `tests/*`, `mcp-server/test_server.py` (tests) et `.venv/*` (dépendances tierces). L’inventaire ne traite pas Git, les caches, node_modules et les artefacts `.local` comme du code de production. Aucun pragma ou branche TYPE_CHECKING n’est exclu. La mesure des sous-processus TP1 reste activée par `patch = subprocess`.

La mesure Node porte sur le module effectivement chargé par les sept tests : `labs.mjs`. Elle ne mesure pas login.js/logout.js non chargés par cette suite, HTML/CSS, le rendu visuel ou l’ensemble du projet multilangage. Les vérifications HTTP des parcours de session et les observations navigateur restent des preuves distinctes. Cette limite n’est pas corrigée artificiellement par une exclusion supplémentaire ou une déclaration de conformité mobile.

## Fichiers locaux protégés et publication proposée

Vérification par métadonnées Git uniquement : `.gemini/.env`, `.local/django-dev-key`, `data/demo.sqlite3`, `data/demo-lab-2-ac48-20261104.json` et `.venv/pyvenv.cfg` existent, sont ignorés et non suivis ; aucun fichier de `.venv/`, `.local/` ou `data/` n’est suivi. Aucun contenu de secret, cookie ou mot de passe n’a été affiché. La sauvegarde Beta reste locale ; aucune nouvelle manipulation de données n’a été effectuée. Les réglages partageables `.gemini/settings.json` et le modèle `.env.example` restent suivis. Le SHA-256 de la migration initiale reste `DB3A8FE7A120260B3338A8ABE7B2E91BA1C90FF150EA01F340BC3230861A1D1B` ; aucun diff TP1 n’est présent.

Le futur commit doit inclure le travail de la tranche déjà présent et cette finalisation, après relecture, sans `git add -f` :

| Groupe à inclure | Rôle |
| --- | --- |
| `.github/workflows/ci.yml` | Tests et couverture réels dans les quatre jobs conservés. |
| `.gitignore`, `.coveragerc`, `pytest.ini`, `requirements.txt`, `requirements-dev.txt`, `manage.py` | Configuration de la tranche, dépendances figées, exclusion des données locales et lancement. |
| `AGENTS.md`, `README.md`, `SPEC.md`, `AGENT_LOG.md`, `USAGE.md` | Instructions, spécification, preuves et attribution de l’assistance. |
| `docs/CHECKPOINT1.md`, `docs/CHECKPOINT2.md`, `docs/CHECKPOINT3.md`, `docs/SLICE1_PLAN.md`, `docs/TP2_FINALIZATION.md` | Guides et état vérifiable de la tranche. |
| `src/` | Configuration, modèles, migration initiale déjà appliquée, accès aux données, services, routes, templates et ressources statiques de la tranche uniquement. |
| `tests/` | Tests isolés Python et JavaScript existants de la tranche. |
| `tools/init_local.py`, `tools/check_coverage.py` | Préparation locale sans écrasement et vérification de couverture. |

Les fichiers sous src/, tests/ et tools/ proviennent de la construction précédente ; aucun n’a été modifié pendant cette finalisation. Le serveur/tests TP1, les données de cours, la configuration Gemini et les fichiers du conteneur ne font pas partie des changements proposés. La liste exhaustive peut être relue sans indexation avec `git diff --name-only` et `git ls-files --others --exclude-standard`.

Message de commit proposé : `feat(lab-booking): deliver TP2 first slice with tests and CI`.


<details>
<summary>Liste exacte des 71 fichiers proposés (non indexés pendant cette étape)</summary>

```text
.coveragerc
.github/workflows/ci.yml
.gitignore
AGENTS.md
AGENT_LOG.md
README.md
SPEC.md
USAGE.md
docs/CHECKPOINT1.md
docs/CHECKPOINT2.md
docs/CHECKPOINT3.md
docs/SLICE1_PLAN.md
docs/TP2_FINALIZATION.md
manage.py
pytest.ini
requirements-dev.txt
requirements.txt
src/__init__.py
src/config/__init__.py
src/config/base.py
src/config/settings.py
src/config/urls.py
src/config/wsgi.py
src/data/__init__.py
src/data/apps.py
src/data/demo.py
src/data/demo_labs.py
src/data/labs.py
src/data/management/__init__.py
src/data/management/commands/__init__.py
src/data/management/commands/demo_labs.py
src/data/management/commands/seed_demo.py
src/data/managers.py
src/data/migrations/0001_initial.py
src/data/migrations/__init__.py
src/data/models.py
src/data/users.py
src/routes/__init__.py
src/routes/auth.py
src/routes/forms.py
src/routes/labs.py
src/routes/pages.py
src/routes/session.py
src/services/__init__.py
src/services/access.py
src/services/auth.py
src/services/labs.py
src/static/css/app.css
src/static/js/labs.mjs
src/static/js/login.js
src/static/js/logout.js
src/templates/base.html
src/templates/csrf_error.html
src/templates/labs.html
src/templates/login.html
tests/__init__.py
tests/conftest.py
tests/http_helpers.py
tests/labs_ui.test.mjs
tests/settings.py
tests/test_access.py
tests/test_auth.py
tests/test_coverage_runner.py
tests/test_demo_data.py
tests/test_demo_labs.py
tests/test_labs.py
tests/test_logout.py
tests/test_models.py
tests/test_static_assets.py
tools/check_coverage.py
tools/init_local.py
```

</details>

## Avant et après une publication autorisée

La revue indépendante a été effectuée une fois par l’agent personnalisé `reviewer`, en lecture seule, après adaptation et tests. Aucun problème bloquant ou important n’a été relevé ; aucun constat n’a été écarté et aucune correction supplémentaire n’a été nécessaire. La liste des 71 fichiers a été comparée à l’état Git : fichiers présents, aucun ignoré dans cette liste et aucun fichier indexé. Les liens Markdown locaux ont été contrôlés.

Avant publication : examiner le diff et la liste de fichiers, conserver les attributions et les limites ci-dessus. Le report du contrôle à 380 pixels doit rester visible ; le statut HTTP manuel non relevé ne doit pas être inventé. Aucun autre développement n’est requis pour préparer ce commit.

Après autorisation distincte : commit/push sans écraser le travail distant, puis contrôler les jobs `test`, `coverage`, `mcp` et `spec` sur le SHA publié. Tant que cette exécution distante n’existe pas, ne pas annoncer une CI verte sur GitHub. L’acceptation du TP et les attentes pédagogiques restent à valider avec l’enseignant ; la finalisation technique locale ne remplace pas cette validation.
