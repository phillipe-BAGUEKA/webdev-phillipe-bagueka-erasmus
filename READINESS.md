# Readiness report: Lab booking — préparation, public non vérifié

Ce squelette conserve les neuf rubriques du Lab 04. Il ne remplace pas le rapport personnel demandé par le cours. Les preuves du site public restent **non vérifiées**.

## 1. Live URL and how to verify it

Non vérifié : aucun déploiement public ni URL dans `course.json`. Vérifier ultérieurement HTTPS, page d'accueil et `/health` dans une fenêtre privée. How I checked : non exécuté.

## 2. Environment variables

| Nom | But | Source future | Secret |
| --- | --- | --- | --- |
| `DJANGO_SECRET_KEY` | Signature Django | nouvelle valeur générée pour Render | oui |
| `DATABASE_URL` | PostgreSQL TLS | tableau de bord Neon | oui |
| `DJANGO_ALLOWED_HOSTS` | Hôtes admis | domaine Render exact | non |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Origines HTTPS | domaine Render exact | non |
| `PORT` | Port Gunicorn | Render | non |
| `LAB_BOOKING_AI_ENABLED` | Activation volontaire de l'IA | choix futur ; 0 par défaut | non |
| `GEMINI_API_KEY` | Fournisseur IA facultatif | compte fournisseur, si autorisé | oui |
| `LAB_BOOKING_MCP_SESSION` | Client MCP local uniquement | session ordinaire hors Render | oui |

How I checked : noms relevés dans le code et `.env.example` le 23 novembre 2026 ; image et conteneur locaux lancés avec des valeurs éphémères, sans profil de démonstration ; démarrage Render non vérifié.

## 3. What happens when things fail

La sonde est testée localement sur conteneurs avec arrêt et redémarrage réel de leur base isolée : 200 → 503 → 200, avec réponses JSON génériques. Une URL inconnue a donné 404 sans détail ; une exception injectée dans le client Django du conteneur a donné 500 sans détail dans la réponse, sans requête réseau externe pour ce dernier cas. Les essais d'une panne réelle de Neon, d'un mauvais déploiement avec rollback et d'une requête mal formée sur le site public sont non vérifiés. How I checked : essai Docker isolé du 23 novembre 2026 et `tests/test_health.py` ; aucun essai public. Voir `docs/LAB04_DEPLOYMENT.md`.

## 4. Four states of one screen

Écran candidat : `/labs` (chargement, contenu, vide, erreur). Vérification sur site public non effectuée. How I checked : les preuves locales antérieures figurent dans `docs/UI.md` ; aucun nouvel essai public.

## 5. Request waterfall

Non vérifié : relever ultérieurement nombre de requêtes, dépendances et durée totale avec cache désactivé. How I checked : non exécuté.

## 6. Security basics checked

À vérifier personnellement avant publication : secrets dans fichiers suivis et historique Git, HTTPS et certificat publics, refus des écritures sans session et sans propriété, flags des cookies sur le site public. How I checked : terminaison HTTPS locale avec certificat autosigné de test, PostgreSQL local en TLS, statiques CSS/JavaScript servis avec leurs types MIME ; aucun audit de l'historique ni essai public. Un accès HTTP isolé ne prouve pas le comportement des cookies sécurisés.

## 7. Known gaps, ranked by risk

Classement provisoire à réviser personnellement : (1) déploiement, persistance après redéploiement, rollback et preuve HTTPS publics non réalisés (la persistance a été observée seulement avec des conteneurs locaux isolés) ; (2) connexion sociale Google absente ; (3) fournisseur IA réel et client MCP final non validés ; (4) éléments de la checklist UI encore sans preuve, dont les états non observés ; (5) note d'architecture et revue personnelles du Lab 03 non terminées. How I checked : état du dépôt, `docs/UI.md`, `docs/LAB04_DEPLOYMENT.md` et guides de clôture locaux ; ordre à discuter avec l'étudiant.

## 8. Model feature

Le code de suggestion et son repli manuel sont présents ; fournisseur désactivé par défaut. Une activation future transmettrait le besoin textuel saisi et au plus dix couples poste/créneau avec leurs caractéristiques utiles ; le code n'ajoute ni identité, ni session, ni historique au paquet. Le texte libre peut lui-même contenir des données personnelles. Quand le fournisseur est absent, lent, limité ou invalide, l'utilisateur reçoit un message explicite et garde le choix manuel ; ce n'est pas une suggestion IA réussie. Prix réel par appel, usage autorisé et essai avec clé non vérifiés. How I checked : `src/services/ai_suggestion.py`, `src/integrations/gemini.py` et tests hors réseau existants ; aucun appel réel.

## 9. MCP

Six outils existent dans le serveur stdio, dont quatre outils projet. Les outils projet agissent comme l'utilisateur actif de la session Django ordinaire fournie au processus : ils ne confèrent pas de privilège administrateur et appliquent les mêmes services et permissions que HTTP. Cette session permet à l'étudiant authentifié de lire ses données et de demander ses propres mutations selon les règles métier ; elle ne choisit pas librement un propriétaire. La remise d'une vraie session au client final et ses appels restent non vérifiés ; aucun serveur MCP public n'est préparé ici. How I checked : `mcp-server/project_runtime.py`, `mcp-server/project_tools.py` et contrôles stdio précédents ; aucun essai client final à cette étape.
