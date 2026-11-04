# Première tranche — plan validé en trois points de contrôle

L’utilisateur a validé l’organisation en trois points, rapporté les observations des points 1 et 2, puis autorisé le point 3. Les résultats sont dans [CHECKPOINT1.md](CHECKPOINT1.md), [CHECKPOINT2.md](CHECKPOINT2.md) et [CHECKPOINT3.md](CHECKPOINT3.md). Le point 3 est implémenté et testé automatiquement. Après correction du MIME et du cache, Codex a observé le catalogue réel puis AC-48 : 3 → 2 → 3, avec Beta restauré à l’identique. L’utilisateur rapporte le refus JSON de l’API après déconnexion, sans statut HTTP relevé. Le contrôle à 380 pixels est reporté et non validé. La CI est maintenant adaptée localement sur autorisation explicite ; ses exécutions distantes restent à confirmer. Voir [TP2_FINALIZATION.md](TP2_FINALIZATION.md). La tranche complète n’est pas déclarée vérifiée manuellement ; les autres tranches restent hors périmètre.

Ordre : base et démonstration → connexion/protection/déconnexion → API et interface complète. À chaque point, arrêter la construction, présenter les résultats automatiques et laisser l’étudiant effectuer les vérifications indiquées avant le point suivant.

## Périmètre et commandes existantes

- Dans cette tranche : Django 5.2 LTS, utilisateur par e-mail, laboratoires, sessions Django, deux écrans, une API de consultation, données de démonstration et tests utiles.
- Hors tranche : postes, réservations, PostgreSQL, Google, IA, nouveaux outils MCP, espace du personnel, inscription publique et déploiement. Un rôle peut être porté par le modèle utilisateur sans construire les fonctions du personnel.
- Préserver le serveur et les tests du TP 1. Ne pas changer les règles d’approbation ni les seuils de couverture pour faciliter la livraison.

Commandes déjà décrites par les fichiers actuels, sans nouvel essai du TP 1 pendant la préparation du plan :

```powershell
python -m unittest discover -s mcp-server -p "test_*.py" -v
node mcp-server/check.mjs -- python mcp-server/server.py
npm.cmd test
npm.cmd run --silent mcp
node checks/ex2.mjs
```

Dans Codespaces, utiliser `npm` à la place de `npm.cmd`. `package.json` ne lance actuellement que les tests et le serveur du TP 1. Le démarrage Django local est documenté dans CHECKPOINT2.md et CHECKPOINT3.md ; la commande de couverture complète est maintenant exécutée et documentée dans CHECKPOINT3.md.

## Organisation proposée et circulation des données

La page `/labs` est protégée avant même l’envoi de son HTML. Son JavaScript appelle ensuite `GET /api/labs`, protégé séparément. Le parcours prévu est : `src/routes/labs.py` → `src/services/labs.py` → `src/data/labs.py` → modèle Laboratory → SQLite. Le service vérifie l’identité de l’acteur avant toute lecture. Les futurs outils MCP recevront un acteur issu de leur session et appelleront ces mêmes services, sans requête SQL propre.

Les services ne reçoivent ni `HttpRequest` ni message MCP. Un contexte d’acteur minimal porte l’identité et le rôle ; une erreur de service peut être traduite en redirection pour une page ou en HTTP 401 pour l’API. Aucun accès direct à l’ORM dans les routes ou services.

Django gère les mots de passe et les sessions : le modèle User conserve un hash, et les mécanismes Django vérifient ce hash. Le service d’authentification utilise un adaptateur de données vers l’authentification Django, sans réimplémenter la cryptographie. Les middlewares SessionMiddleware et AuthenticationMiddleware reconstituent l’utilisateur. `login()` et `logout()` sont appelés par l’adaptateur HTTP : création/rotation de session à la connexion, invalidation côté serveur à la déconnexion. Avec le moteur de sessions en base, la table `django_session` conserve la session et le cookie du navigateur en porte l’identifiant, pas le mot de passe. Ces écritures internes au framework ne constituent pas une seconde logique métier.

Les règles métier, dont les futures règles de propriétaire, quota et chevauchement, restent dans `src/services/`. La protection CSRF des opérations POST et les attributs du cookie sont du transport HTTP : cookie HttpOnly et SameSite=Lax, Secure en HTTPS ; configuration locale HTTP explicitement distincte. Ne pas désactiver CSRF pour faciliter les essais.

## Dépendances proposées

Les dépendances du socle sont figées dans requirements.txt et requirements-dev.txt. Le point 3 ajoute coverage.py 7.17.1 dans .venv, avec l’autorisation de l’utilisateur. Les résultats réels et le périmètre sont consignés dans CHECKPOINT3.md ; pytest-cov n’est pas nécessaire au lanceur local et n’est pas installé.

| Dépendance | Rôle | Moment |
| --- | --- | --- |
| Django, dernier correctif compatible de la série 5.2 LTS | ORM, migrations, hash des mots de passe, authentification, sessions, vues et templates | Point 1 |
| tzdata, sur Windows si requis | Base de fuseaux pour Europe/Sofia ; ne pas coder un décalage fixe | Point 1 |
| pytest et pytest-django | Assertions, base de test isolée, client HTTP Django et identifiants AC-n dans les tests collectés | Point 1 |
| coverage.py compatible avec `patch = subprocess` (au moins 7.10) | Mesure réelle des lignes et branches Python, y compris les sous-processus du serveur TP 1 | Point 3, non installé au point 1 |
| pytest-cov compatible, si utilisé par le chemin CI existant | Intégration de coverage.py dans les commandes pytest-cov déjà présentes en CI ; même configuration de mesure | Point 3, non installé au point 1 |

SQLite et les utilitaires standards nécessaires sont fournis avec Python. Aucun Django REST Framework, framework frontend, pilote PostgreSQL, client OAuth, SDK IA ou SDK MCP n’est requis pour cette tranche. La référence Linux/Codespaces reste Python 3.12 ; vérifier aussi le Python local 3.13 avant de figer les versions. Toute dépendance ajoutée nécessite l’autorisation applicable.

## Point de contrôle 1 — structure, utilisateur, laboratoires et démonstration

Soutient AC-47 et AC-48, sans encore déclarer ces parcours terminés.

### Fichiers prévus

| Fichier ou groupe | Rôle |
| --- | --- |
| `manage.py`, `src/__init__.py`, `src/config/{__init__,settings,urls,wsgi}.py` | Entrée Django, réglages, URL et exécution locale ; configuration par environnement, sans clé réelle dans les sources |
| `requirements.txt`, `requirements-dev.txt` | Dépendances applicatives et de test, avec versions fixées lors de la construction |
| `src/data/{__init__,apps,models,managers}.py` | Application Django de données ; User adapté à l’e-mail dès le départ, Laboratory et gestionnaire utilisateur utilisant les mécanismes Django |
| `src/data/migrations/0001_initial.py` et `__init__.py` | Création initiale de User et Laboratory, avant tout premier migrate ; migrations Django pour auth/contenttypes/sessions en complément |
| `src/data/management/commands/seed_demo.py` et packages `__init__.py` nécessaires | Création idempotente d’un petit jeu de données dans une base de démonstration dédiée, sans écraser des données existantes |
| `tests/{__init__,settings,conftest}.py`, `tests/test_models.py`, `pytest.ini` | Réglages de tests uniquement factices, isolation SQLite, assertions sur les données et collecte des tests |
| `.gitignore` | Ignorer le venv, les bases et artefacts de démonstration/test et les rapports générés, sans masquer sources ou migrations ; préserver les règles de secrets existantes |

Modèle proposé : User fondé sur AbstractUser, e-mail unique comme identifiant de connexion, sans champ username utilisé pour se connecter ; gestionnaire compatible, mot de passe Django et rôle métier explicite étudiant/personnel. Le rôle métier ne doit pas être confondu avec l’accès à l’admin Django ; aucune interface admin n’est exposée dans cette tranche. Laboratory a au minimum un identifiant et un nom. Le choix détaillé des champs sera relu dans la migration avant son application.

Tables nécessaires : utilisateur personnalisé et laboratoire, ainsi que les tables techniques des applications Django retenues, notamment `django_session`. Aucune table de poste ou de réservation maintenant. Fixer AUTH_USER_MODEL avant de générer/appliquer la première migration. La préparation des données est séparée des migrations de schéma.

Base de démonstration proposée : `data/demo.sqlite3`, dédiée et jetable, créée pour ce jalon. Deux comptes étudiants fictifs et trois laboratoires fictifs suffisent. Le seed refuse de remplacer des lignes préexistantes divergentes. Pour chaque nouveau compte, il crée d’abord un mot de passe inutilisable avec Django, puis invite l’opérateur à choisir et confirmer localement un mot de passe avec une saisie masquée, avant de le hacher avec Django. Une interruption laisse le compte non connectable ; une commande Django `changepassword` permettra de terminer cette préparation localement. Le seed ne change jamais le mot de passe d’un compte préexistant. L’étudiant connaît ainsi les identifiants nécessaires à AC-47 sans les publier : aucun mot de passe dans le seed, les arguments de commande, les journaux ou les fichiers suivis. Les tests créent séparément leurs utilisateurs et mots de passe factices dans leur base isolée, sans utiliser ces comptes de démonstration.

Adaptation autorisée au point 1 : `tools/init_local.py` génère une nouvelle clé de développement dans `.local/django-dev-key`, ignorée par Git, sans afficher sa valeur ni lire/remplacer une clé existante. Les réglages locaux chargent seulement cette clé ; les tests utilisent `tests/settings.py` sans charger les secrets locaux. Aucun accès à `.gemini/.env`. Le démarrage exact du point 1, dont l’initialisation locale et l’alternative `seed_demo --no-input`, est documenté dans CHECKPOINT1.md.

### Commandes prévisionnelles

PowerShell, depuis la racine :

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt
.\.venv\Scripts\python.exe manage.py makemigrations data
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py showmigrations
.\.venv\Scripts\python.exe manage.py seed_demo
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe -m pytest tests/test_models.py -v
```

Codespaces/Linux :

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt -r requirements-dev.txt
.venv/bin/python manage.py makemigrations data
.venv/bin/python manage.py migrate
.venv/bin/python manage.py showmigrations
.venv/bin/python manage.py seed_demo
.venv/bin/python manage.py check
.venv/bin/python -m pytest tests/test_models.py -v
```

Inspecter la migration générée avant `migrate`. À partir du premier schéma appliqué, tout changement devient une nouvelle migration ; ne pas régénérer silencieusement la migration initiale.

### Vérifications et arrêt

- Automatiques : création d’une base de test neuve par les migrations, utilisateur par e-mail, unicité de l’e-mail, vérification d’un mot de passe factice par Django sans stockage en clair, présence des laboratoires, seed répétable sans duplication ni écrasement. Ces tests de fondation ne prouvent pas encore la connexion ou l’affichage.
- Étudiant : ouvrir uniquement la base de démonstration dans le visualiseur SQLite ; vérifier la table utilisateur et les trois laboratoires, puis la liste des migrations appliquées. Vérifier qu’aucune table de réservation n’a été créée. Ne pas recopier un hash ou un secret dans la conversation.
- Point d’arrêt : présenter les résultats et attendre la vérification de la base avant la construction de l’authentification.

## Point de contrôle 2 — connexion, protection et déconnexion

Couvre AC-46, AC-47 et AC-49. L’API de liste peut encore être absente ; les assertions d’accès à cette API seront terminées au point 3. Une protection de page ne sera pas présentée comme une API déjà protégée.

### Fichiers prévus

| Fichier ou groupe | Rôle |
| --- | --- |
| `src/data/users.py` | Adaptateur vers l’authentification Django ; aucune vérification cryptographique maison |
| `src/services/{__init__,auth,access}.py` | Authentification applicative, contexte minimal d’acteur et contrôle partagé d’accès authentifié ; erreurs indépendantes du transport |
| `src/routes/{__init__,auth,pages}.py`, modification de `src/config/urls.py` | Adaptateurs HTTP, formulaires/JSON, login/logout Django, redirection des pages protégées et conversion des erreurs |
| `src/templates/{base,login,labs}.html` | Page de connexion, structure commune et page protégée des laboratoires ; aucun contenu de liste fictif présenté comme un résultat de base |
| `src/static/js/{login,logout}.js`, `src/static/css/app.css` | fetch de connexion/déconnexion, protection CSRF, erreurs lisibles, styles simples et focus |
| `tests/{test_auth,test_access,test_logout}.py` | Tests HTTP et services, dont rejet des mauvais identifiants et réutilisation de l’ancien cookie |

Routes prévues : GET `/login`, POST `/api/auth/login`, GET `/labs`, POST `/api/auth/logout`. Connexion valide : session Django créée/renouvelée ; identifiants incorrects : refus sans session authentifiée. Page `/labs` sans session : redirection vers `/login`. Déconnexion : invalidation de la session en base par Django, pas seulement effacement du cookie côté navigateur. La session ne doit pas donner accès à une page ou API protégée après déconnexion, même si l’ancien cookie est rejoué.

Pas de nouvelle dépendance hors de celles prévues au point 1. Pas de JWT, session maison, inscription publique ou Google.

Rappel de la revue du socle : ajouter `XFrameOptionsMiddleware` avant de servir les écrans, puis vérifier la protection contre le clickjacking. Les paramètres HTTPS appartiennent au futur environnement concerné. Les tests de fondation du point 1 ne remplacent pas les tests de parcours portant les identifiants AC-46, AC-47 et AC-49.

### Commandes prévisionnelles

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_auth.py tests/test_access.py tests/test_logout.py -v
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --insecure --noreload
```

Le point 2 conserve DEBUG=False. `--insecure` demande uniquement à runserver de servir les fichiers statiques locaux ; `--noreload` utilise un seul processus, à redémarrer après modification. CSRF et le contrôle des sessions restent actifs. Dans Codespaces, remplacer le chemin Python par `.venv/bin/python` et écouter sur `0.0.0.0:8000`, puis utiliser le port transféré. Ajouter uniquement l’hôte exact nécessaire dans les réglages autorisés et, si nécessaire, l’origine CSRF HTTPS ; ne pas désactiver ces protections ni ouvrir tous les hôtes. Ce parcours Codespaces n’a pas été exécuté ici.

### Vérifications et arrêt

- Automatiques : tests des services avec acteur absent/présent ; login valide/invalide ; client HTTP avec contrôles CSRF ; cookie et session Django ; redirection de `/labs` sans session ; logout puis rejet de l’ancien cookie. Les tests collectés portent les AC-n concernés via leurs identifiants pytest, par exemple `test_page_access[AC-46-anonymous-page]`. Aucun test n’est affaibli pour adapter la spécification au résultat.
- Étudiant : ouvrir `/labs` en navigation privée, constater la redirection, essayer un mot de passe incorrect puis le compte de démonstration correct ; se déconnecter et revenir sur `/labs`. L’écran de liste ne sera déclaré terminé qu’au point 3.
- Point d’arrêt : présenter ces résultats et attendre la vérification de la connexion/déconnexion avant de terminer la liste.

## Point de contrôle 3 — API, liste en base et parcours complet

Termine AC-46 à AC-49, notamment la preuve de lecture de la base demandée par AC-48.

### Fichiers prévus

| Fichier ou groupe | Rôle |
| --- | --- |
| `src/data/labs.py` | Requêtes ORM du catalogue ; pas de liste en mémoire substituée aux données |
| `src/services/labs.py` | Contrôle de l’acteur puis lecture des laboratoires via la couche de données ; réutilisable ultérieurement par MCP |
| `src/routes/labs.py`, modification de `src/config/urls.py` | GET `/api/labs`, réponse JSON et HTTP 401 sans données si la session manque ou est invalidée |
| `src/static/js/labs.mjs`, finalisation de `src/templates/labs.html` et des styles | Chargement par fetch, état vide, erreur lisible et liste réellement retournée par l’API ; module testable avec Node |
| `src/data/management/commands/demo_labs.py` et helpers dans `src/data/` | Procédure AC-48 limitée à une base jetable connue : inspection, retrait d’une ligne de démonstration avec sauvegarde ciblée, puis restauration |
| `tests/test_labs.py`, compléments de `test_access.py` et `test_logout.py`, `tests/test_demo_labs.py`, `tests/labs_ui.test.mjs` | Assertions sur la liste, la base, le HTTP 401, les garde-fous de restauration et les états du script client |
| `.coveragerc`, `tools/check_coverage.py` et tests ciblés du lanceur | Mesure Python incluant les sous-processus TP1 et échec si les tests ou seuils ne passent pas |
| `README.md`, `AGENTS.md`, `AGENT_LOG.md`, `USAGE.md`, `SPEC.md` | Commandes vérifiées, résultats observés et traçabilité ; Spec vs result distingue tests exécutés, observations utilisateur reçues et essais manuels en attente, selon la dernière demande |

Ne créer aucune route CRUD de laboratoire : la gestion du personnel appartient à une tranche suivante. Les commandes de démonstration servent uniquement à préparer/vérifier la base de ce jalon, sans devenir une API applicative.

### Commandes prévisionnelles

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_labs.py tests/test_access.py tests/test_logout.py tests/test_demo_labs.py -v
.\.venv\Scripts\python.exe manage.py demo_labs list
curl.exe -i http://127.0.0.1:8000/labs
curl.exe -i http://127.0.0.1:8000/api/labs
```

Codespaces : même commande avec `.venv/bin/python`, et `curl` plutôt que `curl.exe`. Les requêtes au serveur depuis le terminal peuvent rester sur `http://127.0.0.1:8000`, même lorsque le navigateur passe par le port transféré.

Procédure AC-48 réalisée sous forme de commandes distinctes, à exécuter par l’utilisateur : `demo_labs list` vérifie la base dédiée et son marqueur. `backup` prépare un fichier exclusif avec l’identifiant et les champs du laboratoire ; `withdraw` exige cette sauvegarde valide avant de retirer la ligne. `restore` restitue la même ligne sans écraser de conflit. L’identifiant 2 désigne le laboratoire fictif Beta. Ces opérations sont testées sur données isolées, sans exécution sur la base de démonstration de l’utilisateur pendant la construction.

```powershell
.\.venv\Scripts\python.exe manage.py demo_labs backup --id 2 --snapshot data/demo-lab-2.json
.\.venv\Scripts\python.exe manage.py demo_labs withdraw --snapshot data/demo-lab-2.json
.\.venv\Scripts\python.exe manage.py demo_labs restore --snapshot data/demo-lab-2.json
```

Ces commandes existent maintenant ; le guide CHECKPOINT3.md les présente une par une. Elles ne sont pas destinées à une base contenant des données à conserver. Les tests vérifient les refus de mauvaise cible, sauvegarde absente/invalide, ligne changée et conflit de restauration. Il n’existe aucune commande de purge ou de réinitialisation générale.

### Vérifications et arrêt

- Automatiques : AC-46 sur page et API, AC-47 avec identifiants valides/invalides, AC-48 sur base temporaire avec retrait/restauration, AC-49 avec l’ancien cookie sur page et API. Assertions sur statuts, redirections, contenu JSON, absence de données après refus, compte utilisateur conservé et lignes rétablies. L’API de liste doit renvoyer HTTP 401 sans laboratoires pour les sessions absentes et invalidées ; une redirection HTML de l’API ne satisfait pas le critère.
- Étudiant : se connecter et voir les trois laboratoires ; retirer uniquement la ligne autorisée dans la base de démonstration, recharger et constater sa disparition, la restaurer, recharger et constater son retour. Vérifier ensuite déconnexion, redirection de page et HTTP 401 de l’API sans session. La preuve de rejeu de l’ancien cookie sera apportée par un test automatique préparé, sans recopier un cookie de session réel dans la conversation.
- Interface : vérifier les états applicables des deux écrans et le clavier. Ne pas déclarer l’ensemble des critères UI du projet final réalisé avec ces seuls écrans.
- Point d’arrêt : présenter les résultats automatiques, les observations utilisateur reçues et les essais encore attendus. Selon la dernière demande, Spec vs result contient uniquement ce bilan factuel, sans déclarer un essai manuel réussi avant son retour. Attendre ce retour avant toute autre tranche.

## Couverture Python : mesure réalisée et limites

Objectifs conservés : 100 % de la couche `src/services/` (lignes et branches), au moins 80 % des lignes globalement sur le périmètre Python mesuré. Le lanceur lit les compteurs du rapport structuré de coverage.py et contrôle ces valeurs séparément ; le seul `fail_under` d’un rapport combinant lignes et branches ne suffit pas à garantir le seuil de lignes. Aucun seuil du dépôt n’est diminué. Les résultats exacts, le rapport local et les exclusions sont dans CHECKPOINT3.md.

Périmètre mesuré : tout notre Python exécutable du dépôt, dont `src/` avec configuration, migrations et commandes de démonstration, `manage.py`, les utilitaires Python ajoutés et `mcp-server/server.py`. Exclusions justifiées uniquement pour les tests (`tests/`, `mcp-server/test_server.py`), le venv et les dépendances tierces. Pas d’exclusion des services, des erreurs, des migrations, ni d’ajout de pragma pour faire monter le taux. La configuration couvre le dépôt et les sous-dossiers sans package pour compter aussi le serveur TP1 non importé.

`tools/check_coverage.py` utilise le Python courant. Il exécute les tests de la tranche et les tests TP1 existants sous coverage.py avec branches, instrumente les sous-processus via `patch = subprocess`, combine les données puis applique les deux seuils. Il échoue si un test échoue, si un seuil manque, si aucun service n’est mesuré ou si un fichier Python de production manque au rapport. Il exige des lignes effectivement exécutées du serveur TP1. Ses propres chemins d’échec sont testés avec des rapports fictifs distincts de la mesure réelle.

Commande unique exécutée sur Windows :

```powershell
.\.venv\Scripts\python.exe tools/check_coverage.py
```

Dans Codespaces, commande prévue mais non essayée ici : `.venv/bin/python tools/check_coverage.py`. Le lanceur regroupe pytest, les tests unittest TP1, la combinaison des fichiers des processus et les rapports global/services. Il affiche les taux lignes/branches et termine avec un code non nul si une vérification échoue, sans ignorer une commande intermédiaire en échec.

Cette mesure est une couverture Python, pas une preuve de couverture JavaScript, HTML/CSS, UI ou d’intégration fournisseur. La couverture globale du projet multilangage ne sera pas déclarée acquise à partir du seul rapport Python ; la vérification des portions frontend reste à compléter sans abaisser le seuil global du cours.

La CI du modèle de cours utilisait deux appels pytest-cov qui ne mesuraient pas le serveur TP1 et n’installait pas requirements-dev.txt. Après autorisation explicite, `.github/workflows/ci.yml` utilise maintenant les deux fichiers de dépendances déclarés et le même `tools/check_coverage.py`, avec le même `.coveragerc` et le même inventaire qu’en local. Le seuil des services Python exige 100 % des lignes **et** branches ; celui des lignes Python globales reste à 80 %. L’ancien contrôle Node ciblant des services JavaScript inexistants est remplacé par ce contrôle des services réellement écrits en Python. Les tests JavaScript et leur seuil de lignes de 80 % sont conservés séparément, sans les présenter comme une mesure Python ou de tout le frontend. Aucun outil de test n’est déplacé dans les dépendances applicatives ; aucun contrôle métier ou seuil n’est affaibli. Cette configuration locale n’est pas une exécution GitHub Actions réussie.

## Références techniques et validation du plan

Documents officiels consultés pour préparer le plan : [utilisateur personnalisé dès la migration initiale](https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project), [sessions Django en base](https://docs.djangoproject.com/en/5.2/topics/http/sessions/#using-database-backed-sessions), [sous-processus avec pytest-cov](https://pytest-cov.readthedocs.io/en/latest/subprocess-support.html), [configuration coverage.py](https://coverage.readthedocs.io/en/latest/config.html#run-patch). Les commandes exécutées sous Windows et leurs résultats figurent dans les guides CHECKPOINT1 à CHECKPOINT3 et TP2_FINALIZATION.md. Les variantes Codespaces et l’exécution distante de la CI restent non essayées ici.

Les trois points ont reçu l’autorisation de construction, puis la préparation locale de la CI a été explicitement autorisée. Arrêt avant publication et avant toute autre tranche. Le contrôle à 380 pixels reste reporté, non validé. Aucun commit ou push n’est autorisé à cette étape. Aucun critère n’est déclaré vérifié manuellement sur la seule base de l’approbation du plan.
