# Readiness report: Lab booking — public partiellement vérifié

Ce document conserve les neuf rubriques du Lab 04. Il ne remplace pas le rapport personnel demandé par le cours. Le site public, les deux connexions de démonstration, une réservation, sa persistance après un nouveau déploiement du même commit et son annulation ont été observés. Les limites des preuves sont précisées ci-dessous.

## 1. Live URL and how to verify it

URL publique : `https://lab-booking-phillipe.onrender.com`, fournie par l'étudiant et jointe par Codex le 24 novembre 2026 avec `curl` sur HTTPS. `course.json` contient cette URL. L'étudiant a observé le déploiement initial du SHA `dafa3ec`, la page `/login` mise en forme et `/health` avec `{"status":"ok","db":"ok"}`. Sur cette version initiale, Codex a relevé `/` à 404, `/labs` à 302 vers `/login?next=/labs`, `/login` à 200, CSS et JavaScript à 200 avec MIME correct. Après publication de `449bf7b`, Codex a relevé `/` à 302 vers `/labs`, `/health` à 200 JSON et `/api/labs` sans session à 401 JSON avec `{"error": "Connexion requise."}`, sans liste. Le contrôle officiel `node checks/ex4.mjs` a confirmé la page et son titre : 27/34, avec sept points restants explicités dans `docs/LAB04_DEPLOYMENT.md`. How I checked : observations de l'étudiant distinguées des réponses HTTPS et du vérificateur observés par Codex, sans session authentifiée.

Le 24 novembre, l'étudiant a exécuté localement le préparateur Neon à saisie masquée et transmis uniquement « Préparation réussie : 2 comptes, 1 laboratoire, 2 postes créés. » Codex n'a vu ni la saisie ni les lignes de base directement. Les deux connexions ont ensuite été confirmées par l'étudiant après réinitialisation ciblée. How I checked : messages de résultat rapportés par l'étudiant, distincts d'un essai navigateur de Codex.

Lors de sa première tentative avec `student-public@demo.example`, l'étudiant a vu « Adresse e-mail ou mot de passe incorrect ». Le code de préparation utilise cette adresse exacte et le premier mot de passe masqué saisi ; un test PostgreSQL isolé confirme l'authentification Django d'un compte ainsi créé. Le diagnostic local masqué et en lecture seule, exécuté par l'étudiant, a rendu `DEMO_LOGIN:PASSWORD_MISMATCH:catalogue=1/2`. Le mot de passe ressaisi ne correspond donc pas au hash du compte dans la base interrogée. La revue a reproduit sous Windows une conversion CRLF qui pouvait ajouter un retour chariot au mot de passe enregistré ; le transport est corrigé, mais sa responsabilité exacte sur le premier essai Neon ne peut pas être établie rétrospectivement par les connexions réussies après reset. L'étudiant a rapporté `DEMO_RESET:OK` pour les deux comptes, avec saisie masquée. How I checked : retours non sensibles de l'étudiant, test du transport Windows et tests du code, sans accès aux mots de passe ni à l'URL de base.

Après le reset, l'étudiant a confirmé que les deux connexions Render fonctionnent. Codex a observé dans Edge la session du compte personnel sur `/labs`, avec un laboratoire `DEMO PUBLIC - Laboratory` chargé et un historique personnel vide. À ce stade initial, les réservations, la persistance après redéploiement et les attributs des cookies HTTPS restaient à contrôler ; les relevés ultérieurs figurent ci-dessous. How I checked : retour de l'étudiant pour les deux connexions ; observation navigateur de Codex limitée au compte personnel et au catalogue.

Le 25 novembre, Codex a de nouveau relevé sur HTTPS `/health` à 200 JSON et `GET /api/bookings` sans session à 401 JSON, sans utiliser de cookie. Ces requêtes publiques anonymes ne valent pas preuve du parcours étudiant connecté. `LAB_BOOKING_AI_ENABLED=0` reste le réglage demandé ; aucune intégration OpenAI ni aucun appel fournisseur n'a été effectué. How I checked : `curl` sans session et état du dépôt ; la valeur effective de la variable sur Render a été confirmée séparément par l'étudiant, comme indiqué ci-dessous.

Avant le redéploiement de persistance, l'étudiant a lu dans Render le SHA Live `b96772aabfd0b737222de3ef8fe44f2cf1c5cc44` et confirmé `LAB_BOOKING_AI_ENABLED=0`. Cette version a quatre jobs CI réussis sur le [run 45319378370](https://github.com/phillipe-BAGUEKA/webdev-phillipe-bagueka-erasmus/actions/runs/45319378370). How I checked : SHA et réglage rapportés depuis le tableau de bord Render par l'étudiant ; résultat CI relevé sur GitHub Actions. Aucun secret Render n'a été lu par Codex.

L'étudiant a ouvert `DEMO PUBLIC - Laboratory` comme `student-public@demo.example` : 20 créneaux réservables affichés le 30 novembre 2026. Il a confirmé une seule fois `DEMO PUBLIC - Poste A`, 08:00–09:00 Europe/Sofia, puis rapporté sa présence dans « Mes réservations » avec l'état affiché « Coming soon ». Il a laissé cette réservation active pour comparer après redéploiement. Le statut HTTP du POST, son identifiant de base et une lecture directe de Neon n'ont pas été relevés. How I checked : observations navigateur transmises par l'étudiant, distinctes des tests automatisés et des requêtes anonymes de Codex.

L'étudiant a déclenché dans Render « Manual Deploy → Deploy latest commit » sans modifier les variables et a rapporté un nouveau déploiement de ce même SHA, affiché « Deployed » le 25 novembre 2026 à 02:24:04 GMT+2. Après ce déploiement, Codex a relevé `/health` à 200 JSON en HTTPS. L'étudiant a rechargé `/labs` puis confirmé dans « Mes réservations » le même poste A, le même créneau du 30 novembre 08:00–09:00 Europe/Sofia et le même état « Coming soon ». Ces observations vérifient la persistance du créneau de démonstration à travers ce redéploiement applicatif sur la même base Neon ; elles ne comprennent ni identifiant interne de la ligne ni inspection directe de Neon. How I checked : statut et horodatage Render et comparaison de l'historique rapportés par l'étudiant ; requête `curl` sans session par Codex.

Après la preuve de persistance, l'étudiant a annulé une fois cette réservation. L'écran a affiché « Réservation annulée ; elle reste dans ton historique. » Après rechargement, « Mes réservations » indique une ligne pour `DEMO PUBLIC - Laboratory · DEMO PUBLIC - Poste A`, le 30 novembre 08:00–09:00 Europe/Sofia, état « Annulée · Poste en service ». Le statut HTTP du POST d'annulation n'a pas été relevé. How I checked : texte et état du navigateur transmis par l'étudiant ; aucune action sur le compte ni lecture directe de Neon par Codex.

L'étudiant a d'abord indiqué que le créneau libéré n'était pas proposé. Lors d'un relevé détaillé suivant, il a confirmé le champ date `30/11/2026`, le message « 20 créneau(x) réservable(s) » et `DEMO PUBLIC - Poste A` à 08:00–09:00 ainsi qu'à 09:00–10:00, sans erreur visible. Ce second relevé lève le doute initial : le créneau annulé est de nouveau proposé. Aucune nouvelle réservation n'a été créée pour ce contrôle. How I checked : comparaison des deux retours de l'étudiant ; les tests PostgreSQL existants couvrent séparément la libération du créneau, mais ne remplacent pas cette observation publique.

## 2. Environment variables

| Nom | But | Source future | Secret |
| --- | --- | --- | --- |
| `DJANGO_SECRET_KEY` | Signature Django | nouvelle valeur générée pour Render | oui |
| `DATABASE_URL` | PostgreSQL TLS avec vérification du nom et de la CA système | chaîne directe de la base Neon existante, à contrôler localement | oui |
| `DJANGO_ALLOWED_HOSTS` | Hôtes admis | facultatif pour le domaine Render initial, dérivé de `RENDER_EXTERNAL_HOSTNAME` | non |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Origines HTTPS | facultatif pour le domaine Render initial, dérivé de `RENDER_EXTERNAL_HOSTNAME` | non |
| `PORT` | Port Gunicorn | Render | non |
| `LAB_BOOKING_AI_ENABLED` | Activation volontaire de l'IA | choix futur ; 0 par défaut | non |
| `GEMINI_API_KEY` | Fournisseur IA facultatif | compte fournisseur, si autorisé | oui |
| `LAB_BOOKING_MCP_SESSION` | Client MCP local uniquement | session ordinaire hors Render | oui |

How I checked : noms relevés dans le code et `.env.example` le 24 novembre 2026 ; image et conteneur locaux lancés avec des valeurs éphémères. L'étudiant a exécuté le contrôle Neon en lecture seule avec saisie masquée et a transmis son succès pour Django, `verify-full`, la CA de l'image et PostgreSQL 16. Il a également rapporté le déploiement Render du SHA `dafa3ec` après remplacement de `DJANGO_SECRET_KEY`. Codex n'a lu ni l'URL de base ni la clé. Les valeurs exactes configurées dans Render restent hors de ce rapport.

## 3. What happens when things fail

La sonde est testée localement sur conteneurs avec arrêt et redémarrage réel de leur base isolée : 200 → 503 → 200, avec réponses JSON génériques. Une URL inconnue a donné 404 sans détail ; une exception injectée dans le client Django du conteneur a donné 500 sans détail dans la réponse, sans requête réseau externe pour ce dernier cas. Sur Render, l'étudiant a vu `/health` avec `{"status":"ok","db":"ok"}` et Codex a relevé HTTP 200. La panne réelle de Neon, un rollback et une réponse 500 publique restent non vérifiés. How I checked : essai Docker isolé du 23 novembre, `tests/test_health.py`, puis requête HTTPS publique du 24 novembre.

## 4. Four states of one screen

Écran candidat : `/labs` (chargement, contenu, vide, erreur). L'étudiant a vu la page de connexion publique mise en forme ; Codex a observé dans Edge le contenu du catalogue connecté avec le compte personnel. Les états chargement, vide et erreur de `/labs` sur Render ne sont pas encore observés. How I checked : observation de l'étudiant, observation Edge de Codex et preuves locales antérieures dans `docs/UI.md`.

## 5. Request waterfall

Non vérifié : relever ultérieurement nombre de requêtes, dépendances et durée totale avec cache désactivé. How I checked : non exécuté.

## 6. Security basics checked

Sur le site public, Codex a vérifié la réponse HTTPS, HSTS, `/api/labs` à 401 JSON sans données et le cookie CSRF anonyme marqué `Secure` et `SameSite=Lax`. Le 25 novembre, l'étudiant a relevé dans Edge après connexion HTTPS la présence de `sessionid` avec `Secure=oui`, `HttpOnly=oui` et `SameSite=Lax`, sans transmettre sa valeur. Les refus des écritures sans session et sans propriété, les secrets dans l'historique Git et les autres protections navigateur restent à examiner. How I checked : requêtes HTTPS publiques sans compte par Codex, puis colonnes du navigateur rapportées par l'étudiant ; les tests locaux ne remplacent pas ces observations.

## 7. Known gaps, ranked by risk

Classement provisoire à réviser personnellement : (1) rollback non vérifié ; la persistance, l'annulation et la libération du créneau ont été observées après un nouveau déploiement applicatif du même SHA sur Neon, sans preuve par identifiant interne ni statut HTTP des mutations ; (2) connexion sociale Google absente ; (3) fournisseur IA réel et client MCP final non validés ; (4) éléments de la checklist UI encore sans preuve, dont les états non observés ; (5) note d'architecture et revue personnelles du Lab 03 non terminées. Les deux connexions publiques et les attributs du cookie de session ont été confirmés par l'étudiant. How I checked : état du dépôt, retours de l'étudiant, observation Edge du compte personnel, `docs/UI.md` et guides de clôture locaux ; ordre à discuter avec l'étudiant.

## 8. Model feature

Le code de suggestion et son repli manuel sont présents ; fournisseur désactivé par défaut. Une activation future transmettrait le besoin textuel saisi et au plus dix couples poste/créneau avec leurs caractéristiques utiles ; le code n'ajoute ni identité, ni session, ni historique au paquet. Le texte libre peut lui-même contenir des données personnelles. Quand le fournisseur est absent, lent, limité ou invalide, l'utilisateur reçoit un message explicite et garde le choix manuel ; ce n'est pas une suggestion IA réussie. Prix réel par appel, usage autorisé et essai avec clé non vérifiés. How I checked : `src/services/ai_suggestion.py`, `src/integrations/gemini.py` et tests hors réseau existants ; aucun appel réel.

## 9. MCP

Six outils existent dans le serveur stdio, dont quatre outils projet. Les outils projet agissent comme l'utilisateur actif de la session Django ordinaire fournie au processus : ils ne confèrent pas de privilège administrateur et appliquent les mêmes services et permissions que HTTP. Cette session permet à l'étudiant authentifié de lire ses données et de demander ses propres mutations selon les règles métier ; elle ne choisit pas librement un propriétaire. La remise d'une vraie session au client final et ses appels restent non vérifiés ; aucun serveur MCP public n'est préparé ici. How I checked : `mcp-server/project_runtime.py`, `mcp-server/project_tools.py` et contrôles stdio précédents ; aucun essai client final à cette étape.
