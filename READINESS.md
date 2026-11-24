# Readiness report: Lab booking — public partiellement vérifié

Ce document conserve les neuf rubriques du Lab 04. Il ne remplace pas le rapport personnel demandé par le cours. Le site public est accessible ; les parcours authentifiés et la persistance après redéploiement restent non vérifiés.

## 1. Live URL and how to verify it

URL publique : `https://lab-booking-phillipe.onrender.com`, fournie par l'étudiant et jointe par Codex le 24 novembre 2026 avec `curl` sur HTTPS. `course.json` contient cette URL. L'étudiant a observé le déploiement du SHA `dafa3ec`, la page `/login` mise en forme et `/health` avec `{"status":"ok","db":"ok"}`. Codex a relevé sur cette version : `/` 404, `/labs` 302 vers `/login?next=/labs`, `/login` 200, `/api/labs` 401 JSON, CSS 200 `text/css` et module JavaScript 200 `text/javascript`. Le correctif local de `/` donne une redirection 302 vers `/labs` en test Django ; son effet public reste à vérifier après déploiement. How I checked : observations de l'étudiant distinguées des réponses HTTPS relevées par Codex, sans session authentifiée.

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

Écran candidat : `/labs` (chargement, contenu, vide, erreur). L'étudiant a vu la page de connexion publique mise en forme ; l'écran `/labs` connecté et ses quatre états ne sont pas encore observés sur Render. How I checked : observation de l'étudiant et preuves locales antérieures dans `docs/UI.md`.

## 5. Request waterfall

Non vérifié : relever ultérieurement nombre de requêtes, dépendances et durée totale avec cache désactivé. How I checked : non exécuté.

## 6. Security basics checked

Sur le site public, Codex a vérifié la réponse HTTPS, HSTS, `/api/labs` à 401 JSON sans données et le cookie CSRF anonyme marqué `Secure` et `SameSite=Lax` ; il n'a pas vérifié le cookie de session après une vraie connexion. Les refus des écritures sans session et sans propriété, les secrets dans l'historique Git et les autres protections navigateur restent à examiner. How I checked : requêtes HTTPS publiques sans compte le 24 novembre et tests locaux existants. Un cookie CSRF anonyme ne prouve pas les attributs du cookie de session.

## 7. Known gaps, ranked by risk

Classement provisoire à réviser personnellement : (1) connexion, mutations et cookies de session publics, persistance après redéploiement et rollback non vérifiés (la persistance a été observée seulement avec des conteneurs locaux isolés) ; (2) connexion sociale Google absente ; (3) fournisseur IA réel et client MCP final non validés ; (4) éléments de la checklist UI encore sans preuve, dont les états non observés ; (5) note d'architecture et revue personnelles du Lab 03 non terminées. How I checked : état du dépôt, requêtes publiques non authentifiées, `docs/UI.md` et guides de clôture locaux ; ordre à discuter avec l'étudiant.

## 8. Model feature

Le code de suggestion et son repli manuel sont présents ; fournisseur désactivé par défaut. Une activation future transmettrait le besoin textuel saisi et au plus dix couples poste/créneau avec leurs caractéristiques utiles ; le code n'ajoute ni identité, ni session, ni historique au paquet. Le texte libre peut lui-même contenir des données personnelles. Quand le fournisseur est absent, lent, limité ou invalide, l'utilisateur reçoit un message explicite et garde le choix manuel ; ce n'est pas une suggestion IA réussie. Prix réel par appel, usage autorisé et essai avec clé non vérifiés. How I checked : `src/services/ai_suggestion.py`, `src/integrations/gemini.py` et tests hors réseau existants ; aucun appel réel.

## 9. MCP

Six outils existent dans le serveur stdio, dont quatre outils projet. Les outils projet agissent comme l'utilisateur actif de la session Django ordinaire fournie au processus : ils ne confèrent pas de privilège administrateur et appliquent les mêmes services et permissions que HTTP. Cette session permet à l'étudiant authentifié de lire ses données et de demander ses propres mutations selon les règles métier ; elle ne choisit pas librement un propriétaire. La remise d'une vraie session au client final et ses appels restent non vérifiés ; aucun serveur MCP public n'est préparé ici. How I checked : `mcp-server/project_runtime.py`, `mcp-server/project_tools.py` et contrôles stdio précédents ; aucun essai client final à cette étape.
