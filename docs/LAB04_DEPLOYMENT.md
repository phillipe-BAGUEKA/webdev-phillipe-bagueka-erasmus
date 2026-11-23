# Lab 04 — préparation locale

Sources consultées le 23 novembre 2026 : [Exercise 04, Steps et What you build](https://webdev-course.tu-sofia.workers.dev/en/resources/exercises/4/) ; [Project, The requirements exactly](https://webdev-course.tu-sofia.workers.dev/en/guides/project/). Les exemples du cours supposent Node ; notre application utilise Django, Gunicorn, PostgreSQL et la couverture Python existante.

## Livrables et contrôles exacts du cours

- Une image Docker construite et démarrée, un service Render en HTTPS, une base Neon persistante et une CI verte qui construit l'image et impose la couverture : [Exercise 04, What you build](https://webdev-course.tu-sofia.workers.dev/en/resources/exercises/4/).
- Les variables obligatoires vérifiées au démarrage et listées sans secrets dans `.env.example` ; `/health` répond 200 avec base disponible, 503 sinon ; erreurs publiques courtes sans trace : [Exercise 04, Steps 1 et 4](https://webdev-course.tu-sofia.workers.dev/en/resources/exercises/4/).
- `READINESS.md` avec neuf rubriques en anglais, preuves « How I checked », trois écarts classés ; états UI, waterfall, sécurité, modèle et MCP ; `docs/UI.md`, `course.json` et `checks/ex4.mjs` après mise en ligne : [Exercise 04, What you build et Steps 10–14](https://webdev-course.tu-sofia.workers.dev/en/resources/exercises/4/).
- Démonstrations ultérieures : CI qui bloque un mauvais déploiement, donnée persistante après redéploiement, retour à une version précédente, panne DB et requête invalide, site accessible le jour de la soutenance : [Exercise 04, Steps 6–10](https://webdev-course.tu-sofia.workers.dev/en/resources/exercises/4/) ; [Project, Application and data](https://webdev-course.tu-sofia.workers.dev/en/guides/project/).

## Fichiers et démarrage préparés

`Dockerfile` installe les dépendances figées, collecte les fichiers statiques sans secret réel, puis lance Gunicorn avec `src.config.production` sur `PORT` (10000 par défaut), sans privilège root. `.dockerignore` écarte données, profils, tests et fichiers locaux du contexte. `production.py` exige `DJANGO_SECRET_KEY`, `DATABASE_URL`, `DJANGO_ALLOWED_HOSTS` et `DJANGO_CSRF_TRUSTED_ORIGINS` au démarrage. Les erreurs de configuration ne reproduisent jamais la chaîne de connexion. Le PostgreSQL distant exige TLS. Les sessions restent dans la base. WhiteNoise sert les fichiers collectés avec manifeste et compression. `GET /health` exécute `SELECT 1` dans la couche de données : 200 `{"status":"ok","db":"ok"}` ou 503 `{"status":"error","db":"down"}` sans détail sensible. La redirection HTTPS, les cookies sécurisés, les hôtes et les origines CSRF sont propres au profil de production.

`.env.example` ne contient que des valeurs factices. Les vraies valeurs iront dans Render, jamais dans Git ni dans l'image. L'IA reste désactivée par défaut ; une clé éventuelle ne doit pas venir du profil Gemini CLI. Le serveur MCP stdio ne sera pas exposé par le service web. SQLite, PostgreSQL local 5433 et l'instance 5432 restent indépendants du futur Neon.

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

Ce parcours ne valide pas Render, Neon, le certificat public, les cookies de session sécurisés dans un vrai navigateur ni la persistance après un redéploiement Render. Les essais publics de `READINESS.md` restent non vérifiés.

Le profil accepte `sslmode=verify-full`, mais le test local a utilisé `sslmode=require` avec un certificat autosigné. Cela prouve le chiffrement de la liaison de test, pas l'authentification du serveur PostgreSQL. [Neon explique la différence entre `require` et `verify-full`](https://neon.com/blog/postgres-needs-better-connection-security-defaults). La revue indépendante a relevé que le validateur actuel de `DATABASE_URL` refuse un paramètre `sslrootcert` éventuel : il faudra choisir et tester la source de confiance des certificats dans l'image, puis adapter ce validateur si nécessaire avant la mise en ligne. `.env.example` est un exemple non déployable en l'état. Aucun essai Neon n'a été effectué.

Contrôles finaux sur l'état local : `npm test` réussi (595 tests PostgreSQL, un test de garde SQLite exécuté séparément, 9 TP1 et 66 Node ; un test spécifique à SQLite désélectionné dans le lot PostgreSQL). `tools/check_coverage.py --postgresql` a réussi lors de sa seconde exécution : services 407/407 lignes (100 %) et 124/124 branches (100 %) ; global Python 2074/2463 lignes (84,21 %) et 490/598 branches (81,94 %), total combiné 83,76 %, TP1 inclus et inventaire inchangé. Le premier passage instrumenté avait échoué sur l'attente de 15 s d'une réponse MCP stdio ; le même cas ciblé a ensuite réussi en 7,61 s sous couverture. La couverture JavaScript séparée a réussi : 63 tests, 97,97 % lignes et 94,69 % branches. Ex2 : 32/32 hors bac à sable après un `EPERM` Windows local ; Ex4 officiel : 21/29, notamment faute d'URL et de preuves publiques, et à cause de limites de reconnaissance structurale. Aucun contrôle ni seuil modifié.

Préparation de publication du 24 novembre 2026 : le job `test` de `.github/workflows/ci.yml` lance maintenant `docker build --tag lab-booking:ci .` sans condition. Une erreur de construction fera échouer ce job ; les jobs `coverage`, `mcp` et `spec` conservent leurs commandes et seuils. La même commande a réussi localement, puis une construction `--no-cache` a réellement exécuté `pip install` et `collectstatic` (7 fichiers copiés, 21 traités). Aucune base, variable de connexion ni clé n'a été fournie au build ; `static_build.py` ne charge que les réglages statiques sans secret. Les 22 tests ciblés de production ont réussi sur PostgreSQL de test ; Ex2 : 32/32. La réussite des jobs GitHub doit encore être constatée sur le SHA publié.

## Étapes personnelles sur Render et Neon

Vérifier encore les offres lors de la création. Le cours prescrit un service web Render Docker et une base Neon persistante. [Render Free](https://render.com/docs/free) indique que sa base Postgres gratuite expire après 30 jours ; [Render Deploys](https://render.com/docs/deploys) décrit « After CI Checks Pass » ; [Render Health Checks](https://render.com/docs/health-checks) permet de définir `/health`. La [page des offres Neon](https://neon.com/docs/introduction/plans) donne les limites actuelles, à confirmer dans le compte. Gratuit annoncé ne garantit pas l'accès effectif.

Le [plan gratuit Neon, mis à jour le 18 novembre 2026](https://neon.com/docs/introduction/plans), annonce 1 Go de stockage par projet et 100 CU-heures par mois ; ces quotas sont documentés, pas testés sur le compte de l'étudiant. Aucune ressource distante n'a été créée ici. Lors d'une étape future autorisée :

1. Dans la [console Neon](https://console.neon.tech/), créer un **nouveau projet** et une base pour Lab booking, dans une région proche du futur service Render (par exemple Frankfurt si cette région est proposée aux deux comptes). Choisir le niveau gratuit uniquement s'il est effectivement disponible, sans transférer les données locales. Relever la chaîne de connexion depuis **Connect**, sans la mettre dans Git ni dans le chat.
2. Vérifier sur ce nouveau projet la connexion depuis l'image avec vérification du certificat serveur (`verify-full` et chaîne de confiance disponible dans l'image), avant de considérer le lien Neon prêt. Le `sslmode=require` de l'essai local ne suffit pas à cette preuve.
3. Après publication autorisée et CI adaptée au Lab 04 (construction Docker réellement contrôlée), ouvrir [Render Dashboard → New → Web Service](https://render.com/docs/web-services), connecter ce dépôt GitHub et sa branche `main`, choisir l'environnement **Docker** issu du `Dockerfile`, la région compatible avec Neon et le plan effectivement disponible. Ne pas utiliser la configuration Python de l'exemple Django Render : le conteneur possède déjà son `CMD` Gunicorn.
4. Dans les variables d'environnement du service, renseigner `DATABASE_URL` depuis Neon, une nouvelle `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS` avec le domaine Render exact, `DJANGO_CSRF_TRUSTED_ORIGINS` avec son origine `https://`, et `LAB_BOOKING_AI_ENABLED=0`. `PORT` est normalement fourni par Render ; vérifier sa valeur au démarrage. Ne pas ajouter `GEMINI_API_KEY`, `LAB_BOOKING_MCP_SESSION` ni les variables Google inutilisées. Aucun secret dans les arguments de build.
5. Configurer **Health Check Path** sur `/health` et **Auto-Deploy → After CI Checks Pass**. Vérifier que la CI du SHA déployé a réussi, puis seulement déclencher la création/déploiement ; contrôler dans les journaux sans secrets l'application des migrations et le démarrage Gunicorn. [Render précise les conditions des checks CI](https://render.com/docs/deploys#configuring-auto-deploys).

La connexion sociale Google reste absente : ne pas inventer d'URL de callback. Les éventuels coûts, quotas et limitations doivent être confirmés dans les comptes avant création. La construction Docker est désormais bloquante dans le job `test` ; sa réussite distante reste à vérifier sur le SHA publié avant tout déploiement.

À démontrer plus tard sur Render : conteneur public démarré, persistance après redéploiement, rollback chronométré, erreurs sur site public, quatre états et waterfall navigateur, recherche personnelle de secrets dans Git, coût et accès réels au modèle, client MCP final. `READINESS.md` devra décrire méthode et preuve, jamais une supposition.
