# Lab 04 — préparation locale

## Première mise en ligne et correctif, 24 novembre 2026

L'étudiant a signalé le déploiement réussi de `dafa3ec` après remplacement de
`DJANGO_SECRET_KEY`. Sur le domaine public Render, il a observé `/` avec
« Page introuvable », `/labs` redirigé vers la connexion correctement mise en
forme et `/health` avec `{"status":"ok","db":"ok"}`. Codex a relevé les
statuts HTTPS correspondants (404, 302 et 200), l'API `/api/labs` à 401 JSON et
les fichiers CSS/JavaScript à 200 avec leurs types MIME attendus.

Le routeur ne définissait aucune route `/`. Le correctif y ajoute une redirection
temporaire vers `/labs`, qui conserve le contrôle de session existant. Render
signalait aussi `Control server error: [Errno 13] Permission denied:
'/home/appuser'`. L'image utilise volontairement l'UID 10001 sans créer de
répertoire personnel. Le socket de contrôle facultatif de Gunicorn cherchait
son chemin sous ce répertoire. La configuration désactive ce seul socket ; elle
n'élargit pas les permissions du conteneur. L'image corrigée a été construite
localement et son utilisateur, l'absence de répertoire personnel et le réglage
du socket ont été vérifiés. L'absence du message dans les journaux Render doit
encore être confirmée après le redéploiement.

La préparation limitée de comptes et d'un catalogue de démonstration publics
est décrite dans [NEON_PUBLIC_DEMO.md](NEON_PUBLIC_DEMO.md). Elle requiert une
saisie masquée locale de la chaîne Neon et de deux nouveaux mots de passe. La
procédure a été exécutée par l'étudiant, qui a rapporté « Préparation réussie :
2 comptes, 1 laboratoire, 2 postes créés. » Codex n'a pas vu la saisie ni les
lignes de la base directement. Les connexions publiques,
mutations, attributs du cookie de session et persistance après redéploiement
restent donc à observer.

Vérifications locales du correctif : 71 tests ciblés PostgreSQL réussis ;
`npm test` : 616 tests PostgreSQL, une garde SQLite séparée, 9 tests TP1 et 66 tests
Node réussis. Couverture officielle PostgreSQL et TP1 : services 407/407 lignes
et 124/124 branches ; global Python 2156/2601 lignes et 520/648 branches, soit
82,36 % combiné. L'inventaire inclut aussi les scripts locaux ignorés de
`.local`, sans exclusion nouvelle. `node checks/ex2.mjs` : 32/32. Avant
publication du correctif, `node checks/ex4.mjs` : 25/34 ; les deux échecs de
page publique reflètent encore le 404 du SHA déployé, et les autres échecs
portent sur la reconnaissance structurelle de la couverture Python, des
preuves UI et du prix fournisseur non mesuré. Aucun vérificateur n'a été modifié.
L'image `lab-booking:render-fix` a été construite. Un essai de démarrage dans
cette image avec les réglages statiques, sans base ni secret, a lancé Gunicorn
27.0.1 et deux workers sans message de socket ; l'arrêt programmé du processus
ne constitue pas une preuve des journaux Render après redéploiement.

Après le push de `449bf7b`, les quatre jobs du [run CI
45309644035](https://github.com/phillipe-BAGUEKA/webdev-phillipe-bagueka-erasmus/actions/runs/45309644035)
ont réussi : `test` (616 tests PostgreSQL, garde SQLite séparée, 9 TP1, 66 Node
et build Docker), `coverage`, `mcp` et `spec`. La CI a mesuré 407/407 lignes
et 124/124 branches des services ; global Python 2157/2274 lignes et 521/572
branches (94,10 % combiné), et couverture JavaScript sur 63 tests. Le
dénominateur Python diffère du local, car les scripts ignorés de `.local` ne
figurent pas dans le clone CI.

Le site public a ensuite répondu `/` 302 vers `/labs`, `/health` 200 JSON et
`/api/labs` sans session 401 JSON `{"error": "Connexion requise."}` sans liste.
L'étudiant a ensuite rapporté le succès du préparateur (deux comptes, un
laboratoire, deux postes), puis un refus de connexion pour le compte étudiant.
Le code fixe son adresse à `student-public@demo.example` et utilise le premier
mot de passe masqué de la préparation. Un test PostgreSQL isolé confirme que le
backend Django accepte le compte créé ainsi. `tools/check_neon_demo_login.py`
propose un diagnostic en lecture seule avec la même URL et ce mot de passe,
saisis localement et jamais affichés. L'étudiant a obtenu
`DEMO_LOGIN:PASSWORD_MISMATCH:catalogue=1/2`. Il demande un reset ciblé des
deux comptes ; la commande masquée et ses limites sont dans
`docs/NEON_PUBLIC_DEMO.md`. L'étudiant a ensuite transmis `DEMO_RESET:OK`
après saisie masquée. L'étudiant a ensuite confirmé que les deux connexions
Render fonctionnent ; Codex a observé le compte personnel et le catalogue
sur `/labs` dans Edge. Les réservations publiques restent non vérifiées.
La revue a reproduit la conversion CRLF de l'ancien transport texte sous
Windows, qui pouvait laisser un retour chariot dans le mot de passe stocké.
Le préparateur, le diagnostic et le reset utilisent maintenant un flux binaire
UTF-8 ; un test de non-régression contrôle ce point. La responsabilité exacte
de ce défaut sur l'essai Neon initial ne peut pas être prouvée par le seul
succès des connexions après réinitialisation.

`node checks/ex4.mjs` a atteint 27/34 : la page et son titre passent désormais.
Restent : détection structurelle de la commande de couverture Python et de son
seuil services à 100 % (les jobs CI prouvent l'exécution réelle), 17 cases UI
non cochées et absence de capture reconnue, prix fournisseur non mesuré et
deux recherches de mots anglais que le texte français de la section Model ne
satisfait pas. Ce résultat n'est pas une clôture du Lab 04. L'absence du message
Gunicorn dans les nouveaux journaux Render n'est pas directement observable
par Codex et reste à confirmer par l'étudiant.

Sources consultées le 23 novembre 2026 : [Exercise 04, Steps et What you build](https://webdev-course.tu-sofia.workers.dev/en/resources/exercises/4/) ; [Project, The requirements exactly](https://webdev-course.tu-sofia.workers.dev/en/guides/project/). Les exemples du cours supposent Node ; notre application utilise Django, Gunicorn, PostgreSQL et la couverture Python existante.

## Livrables et contrôles exacts du cours

- Une image Docker construite et démarrée, un service Render en HTTPS, une base Neon persistante et une CI verte qui construit l'image et impose la couverture : [Exercise 04, What you build](https://webdev-course.tu-sofia.workers.dev/en/resources/exercises/4/).
- Les variables obligatoires vérifiées au démarrage et listées sans secrets dans `.env.example` ; `/health` répond 200 avec base disponible, 503 sinon ; erreurs publiques courtes sans trace : [Exercise 04, Steps 1 et 4](https://webdev-course.tu-sofia.workers.dev/en/resources/exercises/4/).
- `READINESS.md` avec neuf rubriques en anglais, preuves « How I checked », trois écarts classés ; états UI, waterfall, sécurité, modèle et MCP ; `docs/UI.md`, `course.json` et `checks/ex4.mjs` après mise en ligne : [Exercise 04, What you build et Steps 10–14](https://webdev-course.tu-sofia.workers.dev/en/resources/exercises/4/).
- Démonstrations ultérieures : CI qui bloque un mauvais déploiement, donnée persistante après redéploiement, retour à une version précédente, panne DB et requête invalide, site accessible le jour de la soutenance : [Exercise 04, Steps 6–10](https://webdev-course.tu-sofia.workers.dev/en/resources/exercises/4/) ; [Project, Application and data](https://webdev-course.tu-sofia.workers.dev/en/guides/project/).

## Fichiers et démarrage préparés

`Dockerfile` installe les dépendances figées, collecte les fichiers statiques sans secret réel, puis lance Gunicorn avec `src.config.production` sur `PORT` (10000 par défaut), sans privilège root. `.dockerignore` écarte données, profils, tests et fichiers locaux du contexte. `production.py` exige `DJANGO_SECRET_KEY` et `DATABASE_URL`. Les hôtes et origines CSRF sont soit explicites, soit déduits du domaine initial `RENDER_EXTERNAL_HOSTNAME` fourni par Render ; hors Render ou pour un domaine personnalisé, les valeurs exactes doivent être renseignées. Les erreurs de configuration ne reproduisent jamais la chaîne de connexion. Pour un hôte Neon, le profil exige `verify-full`, la CA système et le channel binding ; le `require` du test local autosigné reste accepté seulement pour d'autres hôtes. Les sessions restent dans la base. WhiteNoise sert les fichiers collectés avec manifeste et compression. `GET /health` exécute `SELECT 1` dans la couche de données : 200 `{"status":"ok","db":"ok"}` ou 503 `{"status":"error","db":"down"}` sans détail sensible. La redirection HTTPS, les cookies sécurisés, les hôtes et les origines CSRF sont propres au profil de production.

`.env.example` ne contient que des valeurs factices. Les vraies valeurs sont configurées dans Render, jamais dans Git ni dans l'image. L'IA reste désactivée par défaut ; une clé éventuelle ne doit pas venir du profil Gemini CLI. Le serveur MCP stdio n'est pas exposé par le service web. SQLite, PostgreSQL local 5433 et l'instance 5432 restent indépendants de Neon.

`GOOGLE_CLIENT_ID` et `GOOGLE_CLIENT_SECRET` restent dans l'exemple pour la fonctionnalité future spécifiée et pour le contrôle ex2 ; le code actuel ne les lit pas. Ils ne sont ni nécessaires au démarrage ni à renseigner sur Render maintenant. Ce point diffère de la consigne Lab 04 de retirer les variables inutilisées : il sera résolu lorsque la connexion Google sera implémentée ou après clarification avec le professeur, sans prétendre que la fonctionnalité existe.

`manage.py check --deploy` émet deux avertissements HSTS (`SECURE_HSTS_INCLUDE_SUBDOMAINS` et `SECURE_HSTS_PRELOAD`) : ils restent désactivés intentionnellement sur le domaine partagé `onrender.com`. Le profil configure néanmoins HSTS pour l'hôte exact, les cookies sécurisés, CSRF et HTTPS. [Django décrit le risque d'un HSTS mal réglé](https://docs.djangoproject.com/en/5.2/ref/settings/#secure-hsts-seconds).

## Vérifications et commandes futures

Les pages inconnues reçoivent une phrase 404 ; un échec non traité reçoit une phrase 500. Le test d'intégration vérifie que le détail synthétique de l'exception reste dans le journal serveur `django.request`, jamais dans la réponse. Le journal d'accès Gunicorn est désactivé pour ne pas enregistrer les chemins ou paramètres de requête pouvant contenir des données d'utilisateur.

Sur Render gratuit, le `CMD` applique les migrations avant de lancer Gunicorn ; un échec stoppe le démarrage. [La commande pré-déploiement n'est disponible que pour les services payants](https://render.com/docs/deploys#pre-deploy-command), et [l'offre gratuite n'a ni shell ni tâche ponctuelle](https://render.com/docs/free). Une future migration non compatible avec l'ancien conteneur demandera une stratégie distincte. Les valeurs Render ne sont utilisées qu'à l'exécution, pas lors de `collectstatic` dans l'image.

Après préparation personnelle d'un fichier local ignoré avec des valeurs **nouvelles** pointant vers une base isolée (jamais la base de démonstration) :

```sh
docker build -t lab-booking:local .
docker run --rm --env-file <fichier-local-ignore> lab-booking:local python manage.py migrate --noinput
docker run --rm -p 10000:10000 --env-file <fichier-local-ignore> lab-booking:local
curl -i http://127.0.0.1:10000/health
```

La redirection HTTPS est active en production, sauf pour `/health` : Render [accepte aussi 3xx comme « sain »](https://render.com/docs/health-checks#success-criteria), ce qui masquerait une panne de base si la sonde était redirigée avant sa requête SQL. L'accès public HTTP est redirigé vers HTTPS par [l'edge Render](https://render.com/docs/tls). La sonde interne peut donc atteindre la vue et répondre 200 ou 503 selon la base.

### Validation locale en conteneurs — 23 novembre 2026

Docker Desktop Linux était d'abord indisponible (`open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.`). Après son démarrage, Docker Engine 27.4.0 a répondu et `docker build` a construit l'image. Un premier lancement du banc d'essai a rencontré une course pendant l'initialisation temporaire de PostgreSQL ; l'attente a été corrigée pour exiger une connexion TCP effective. Cet échec concerne le banc local, pas l'application. L'essai final a utilisé un réseau Docker neuf, un volume neuf, PostgreSQL 16 et une base `lab04_isolated` créée avec zéro table applicative. Identifiants et clé Django ont été générés en mémoire pour cet essai, sans profil existant ni argument contenant une valeur sensible. La connexion applicative PostgreSQL utilisait TLS avec un certificat autosigné local ; ce test ne valide ni Neon ni son certificat public.

Observations de l'essai final :

| Contrôle | Résultat observé |
| --- | --- |
| Démarrage | 18 migrations appliquées à la base neuve ; travailleurs Gunicorn démarrés ensuite ; connexion applicative PostgreSQL avec TLS confirmée par `pg_stat_ssl`. |
| Santé | `GET /health` : 200 et `{"status":"ok","db":"ok"}` ; après arrêt du conteneur DB : 503 et `{"status":"error","db":"down"}` ; après redémarrage DB : 200. |
| HTTPS local et statiques | Caddy local avec certificat autosigné et terminaison HTTPS ; `/login` 200 ; CSS collecté 200 `text/css` et module JavaScript de connexion 200 `text/javascript`. Le client du banc acceptait explicitement ce certificat de test. |
| Erreurs publiques | URL inexistante derrière le proxy : 404, corps `Page introuvable.` ; exception synthétique injectée dans le client Django du conteneur en configuration de production : 500, corps `Une erreur est survenue.`, sans détail de l'exception. Le 500 n'a pas été déclenché par une requête réseau externe. |
| Persistance | Un laboratoire synthétique créé dans cette seule base a gardé le même identifiant et le même nom après suppression et recréation du conteneur applicatif avec le volume DB inchangé. |
| Nettoyage | Conteneurs applicatif, DB et proxy, réseau, volume et image propres à cet essai supprimés ; absence vérifiée des ressources nommées. |

Ce parcours local ne valide pas à lui seul Render, Neon, le certificat public, les cookies de session sécurisés dans un vrai navigateur ni la persistance après un redéploiement Render. Les observations publiques ultérieures sont distinguées dans `READINESS.md`.

Le test local du 23 novembre a utilisé `sslmode=require` avec un certificat autosigné. Cela prouve le chiffrement de la liaison de test, pas l'authentification du serveur PostgreSQL. [Neon explique la différence entre `require` et `verify-full`](https://neon.com/blog/postgres-needs-better-connection-security-defaults). Le 24 novembre, le profil Django a été adapté pour accepter `sslrootcert=system` uniquement avec `sslmode=verify-full`, en plus de l'option facultative `channel_binding=require`. L'image contient libpq 18 et un bundle CA Linux explicitement fourni à OpenSSL par `SSL_CERT_FILE` ; le build vérifie que ce fichier existe et n'est pas vide. Cette combinaison a réussi le contrôle Neon en lecture seule décrit ci-dessous. `.env.example` reste un exemple non déployable tel quel.

Contrôles finaux sur l'état local : `npm test` réussi (595 tests PostgreSQL, un test de garde SQLite exécuté séparément, 9 TP1 et 66 Node ; un test spécifique à SQLite désélectionné dans le lot PostgreSQL). `tools/check_coverage.py --postgresql` a réussi lors de sa seconde exécution : services 407/407 lignes (100 %) et 124/124 branches (100 %) ; global Python 2074/2463 lignes (84,21 %) et 490/598 branches (81,94 %), total combiné 83,76 %, TP1 inclus et inventaire inchangé. Le premier passage instrumenté avait échoué sur l'attente de 15 s d'une réponse MCP stdio ; le même cas ciblé a ensuite réussi en 7,61 s sous couverture. La couverture JavaScript séparée a réussi : 63 tests, 97,97 % lignes et 94,69 % branches. Ex2 : 32/32 hors bac à sable après un `EPERM` Windows local ; Ex4 officiel : 21/29, notamment faute d'URL et de preuves publiques, et à cause de limites de reconnaissance structurale. Aucun contrôle ni seuil modifié.

Préparation de publication du 24 novembre 2026 : le job `test` de `.github/workflows/ci.yml` lance maintenant `docker build --tag lab-booking:ci .` sans condition. Une erreur de construction fait échouer ce job ; les jobs `coverage`, `mcp` et `spec` conservent leurs commandes et seuils. La même commande a réussi localement, puis une construction `--no-cache` a réellement exécuté `pip install` et `collectstatic` (7 fichiers copiés, 21 traités). Aucune base, variable de connexion ni clé n'a été fournie au build ; `static_build.py` ne charge que les réglages statiques sans secret. Les 22 tests ciblés de production ont réussi sur PostgreSQL de test ; Ex2 : 32/32. Les [quatre jobs du SHA 321dd2a](https://github.com/phillipe-BAGUEKA/webdev-phillipe-bagueka-erasmus/actions/runs/45290679164) ont ensuite réussi, y compris la construction Docker.

### Contrôle Neon en lecture seule — réussi le 24 novembre 2026

L'étudiant a créé le projet Neon `lab-booking`, la base `lab_booking`, PostgreSQL 16 en région AWS Frankfurt et l'offre Free. Ces informations viennent de l'étudiant. Après deux diagnostics ciblés et sans divulguer l'URL, il a exécuté le contrôle final depuis l'image Docker corrigée et transmis : « Connexion Neon vérifiée : Django, verify-full, CA de l'image, lecture seule, PostgreSQL 16. » Codex a vérifié le code et l'image qui produisent ce résultat, mais n'a pas vu la saisie ni la console de l'étudiant. Ce paragraphe décrit le contrôle antérieur au déploiement, désormais réalisé selon le rapport de l'étudiant.

Depuis la racine du dépôt, la commande interactive est `.\.venv\Scripts\python.exe .local\check_neon_readonly.py`. Ce script local, ignoré par Git, demande la chaîne **Direct connection** avec saisie masquée. Il vérifie le domaine Neon et le nom de base, conserve l'hôte direct et les identifiants, impose `sslmode=verify-full`, `sslrootcert=system` et `channel_binding=require`, puis transmet la chaîne uniquement par l'entrée standard d'un conteneur éphémère sans journal Docker. Le conteneur ne lance ni le `CMD` de migration ni Gunicorn : il charge `src.config.production` et effectue seulement des lectures SQL, avec `default_transaction_read_only=on`. Le résultat attendu est un message de réussite sans URL, ou une catégorie d'échec sans détail sensible. Le jeton de connexion ne doit pas être collé dans la conversation, dans une commande, dans un profil ni dans Git. Cette remise locale n'est pas une validation du déploiement Render.

Le premier essai a rendu une erreur TLS générique. Le prédiagnostic SSL de Python dans l'image passait, mais libpq ne validait pas le certificat avec son magasin par défaut (`DB_TLS_CERT_OTHER`). Pointer `SSL_CERT_FILE` vers le bundle CA Linux a permis la connexion et la lecture. Un contrôle initial de `pg_stat_ssl` côté base a ensuite rejeté le résultat (`DB_ASSERT_CONNECTION`) ; ce point ne décrit pas nécessairement la liaison client vers le proxy Neon. Le contrôle final utilise l'indicateur SSL de **la connexion libpq cliente** (`pgconn.ssl_in_use`), le nom de la base, le mode lecture seule et la version. Aucun essai n'a lancé la commande normale du conteneur, qui exécuterait des migrations.

## Étapes personnelles sur Render et Neon

Le cours prescrit un service web Render Docker et une base Neon persistante. [Render Free](https://render.com/docs/free) indique que sa base Postgres gratuite expire après 30 jours ; [Render Deploys](https://render.com/docs/deploys) décrit « After CI Checks Pass » ; [Render Health Checks](https://render.com/docs/health-checks) permet de définir `/health`. La [page des offres Neon](https://neon.com/docs/introduction/plans) donne les limites annoncées, à confirmer dans le compte. Gratuit annoncé ne garantit pas l'accès effectif.

Le [plan gratuit Neon, mis à jour le 18 novembre 2026](https://neon.com/docs/introduction/plans), annonce 1 Go de stockage par projet et 100 CU-heures par mois ; l'étudiant a confirmé l'offre Free de son projet, sans contrôle des quotas effectifs par Codex. La ressource Neon a été créée par l'étudiant ; aucune autre ressource distante n'a été créée par Codex. Les étapes ci-dessous décrivent la préparation historique du premier déploiement et ne demandent pas de recréer les ressources :

1. Dans la [console Neon](https://console.neon.tech/), ouvrir le projet existant `lab-booking`, choisir la base `lab_booking`, puis **Connect → Connection string → Direct connection** (ne pas sélectionner le pooler). Copier localement la chaîne entière, sans la mettre dans Git ni dans le chat. L'hôte direct est approprié au premier démarrage qui applique les migrations ; aucun transfert de données locales n'est prévu.
2. Exécuter le contrôle masqué ci-dessus. Après réussite effective, employer dans Render la **même chaîne directe** avec l'hôte, le rôle, le mot de passe et la base Neon d'origine, mais avec les paramètres de requête validés `sslmode=verify-full&sslrootcert=system&channel_binding=require`. Ne jamais publier ni journaliser cette chaîne. Sans message de réussite du contrôle, ne pas considérer `DATABASE_URL` prêt.
3. Dans le formulaire [Render → New → Web Service](https://render.com/docs/web-services), connecter ce dépôt GitHub et sa branche `main`, choisir l'environnement **Docker** issu du `Dockerfile`, une région proche de Frankfurt et le plan effectivement disponible. Ne pas utiliser la configuration Python de l'exemple Django Render : le conteneur possède déjà son `CMD` Gunicorn.
4. Dans les variables d'environnement du service, renseigner `DATABASE_URL` validée, une nouvelle `DJANGO_SECRET_KEY` et `LAB_BOOKING_AI_ENABLED=0`. Pour le domaine Render initial, laisser `DJANGO_ALLOWED_HOSTS` et `DJANGO_CSRF_TRUSTED_ORIGINS` absents : le profil valide `RENDER_EXTERNAL_HOSTNAME` fourni par Render à l'exécution et en déduit exactement ce nom et son origine HTTPS. Si un domaine personnalisé est ajouté plus tard, saisir alors les valeurs explicites correspondantes. `PORT` est normalement fourni par Render ; vérifier sa valeur au démarrage. Ne pas ajouter `GEMINI_API_KEY`, `LAB_BOOKING_MCP_SESSION` ni les variables Google inutilisées. Aucun secret dans les arguments de build.
5. Configurer **Health Check Path** sur `/health` et **Auto-Deploy → After CI Checks Pass**. Vérifier que la CI du SHA déployé a réussi, puis seulement déclencher la création/déploiement ; contrôler dans les journaux sans secrets l'application des migrations et le démarrage Gunicorn. [Render précise les conditions des checks CI](https://render.com/docs/deploys#configuring-auto-deploys).

La connexion sociale Google reste absente : ne pas inventer d'URL de callback. Les éventuels coûts, quotas et limitations doivent être confirmés dans les comptes avant création du service Render. La construction Docker est bloquante dans le job `test` ; sa réussite distante sur le prochain correctif TLS devra être vérifiée avant tout déploiement.

À démontrer plus tard sur Render : connexion et mutations publiques, persistance après redéploiement, rollback chronométré, réponse 500 publique, quatre états et waterfall navigateur, recherche personnelle de secrets dans Git, coût et accès réels au modèle, client MCP final. `READINESS.md` doit décrire méthode et preuve, jamais une supposition.
