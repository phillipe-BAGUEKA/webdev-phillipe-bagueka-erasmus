# Point 2 — connexion locale, page protégée et déconnexion

Construit avec l’aide de Codex le 4 novembre 2026. L’utilisateur a depuis confirmé l’affichage de la connexion et de son erreur, l’accès connecté à Laboratoires, la redirection sans session vers /login?next=/labs et le parcours connexion/déconnexion au clavier avec focus visible. Ces observations lui sont attribuées, sans conclusion sur sa compréhension. Le contrôle à 380 pixels est reporté à sa demande, non effectué. Ce guide conserve le périmètre et les résultats du point 2 ; l’API et la liste ajoutées ensuite sont décrites dans [CHECKPOINT3.md](CHECKPOINT3.md).

## Vérifications du point 1 rapportées par l’utilisateur

L’utilisateur a indiqué avoir personnellement défini les mots de passe de `student1@demo.example` et `student2@demo.example`, relancé le seed (0 compte, 0 laboratoire créés), constaté toutes les migrations [X], les trois laboratoires DEMO - Laboratory Alpha/Beta/Gamma et les deux étudiants (`role=student`, `is_active=1`, `is_staff=0`, `is_superuser=0`). Il a aussi constaté l’absence de table métier de poste ou de réservation. Ces observations sont attribuées à l’utilisateur, sans affirmation sur sa compréhension. Codex n’a ni demandé ces mots de passe ni réinitialisé ces comptes.

## Fichiers et responsabilités

| Fichiers | Rôle |
| --- | --- |
| `src/data/users.py` | Adaptateur vers `authenticate()` de Django : hachage/vérification natifs et accès utilisateur par le backend Django. |
| `src/services/auth.py`, `access.py` | Refus uniforme des identifiants invalides/inactifs et exigence d’un acteur authentifié actif, indépendants d’un HttpRequest ou d’un message MCP. |
| `src/routes/forms.py`, `session.py` | Validation du formulaire HTTP, conversion de la session Django en acteur, sélection d’une destination de retour interne. |
| `src/routes/auth.py` | Création/rotation de session par `login()`, invalidation par `logout()` ; réponses HTML ou JSON selon Accept. Aucune requête ORM applicative dans les routes. |
| `src/routes/pages.py` | Pages connexion/laboratoires et erreur CSRF lisible. La page protégée appelle le service de contrôle d’accès. |
| `src/config/base.py`, `urls.py` | Templates, fichiers statiques, protection contre le clickjacking, traitement CSRF et quatre routes du point 2. |
| `src/templates/` et `src/static/` | Formulaires HTML avec libellés et jetons CSRF ; JavaScript fetch uniquement pour les actions de session ; CSS sobre, adaptation à la largeur, focus visible, messages de chargement/erreur/succès. |
| `tests/conftest.py`, `http_helpers.py`, `test_auth.py`, `test_access.py`, `test_logout.py` | Comptes temporaires, client avec `enforce_csrf_checks=True`, preuves automatiques des parcours et refus. |

Connexion : formulaire → route → service d’authentification → adaptateur de données → Django. Le résultat revient à la route, qui établit la session Django. Consultation : middleware Django → acteur → service d’accès → page. Déconnexion : POST avec CSRF → `logout()` Django → suppression de la session côté serveur. Les écritures techniques du framework restent distinctes des futures règles métier partagées HTTP/MCP.

Le rôle et le mot de passe ne sont pas modifiés par ces parcours. Django peut mettre à jour `last_login` après une connexion réussie, conformément à son fonctionnement natif. Aucun compte ni laboratoire n’est créé par la connexion.

Le paramètre `next` accepte uniquement le chemin relatif de la page protégée existante (`/labs`, avec ses paramètres ou fragment). Les URL externes, les URL absolues et les autres destinations reviennent à `/labs`. La vérification est appliquée au formulaire affiché et au POST, même forgé directement. Les erreurs d’adresse inconnue, de mauvais mot de passe ou de compte inactif utilisent le même message. Connexion et déconnexion requièrent POST et un CSRF valide ; aucun `csrf_exempt`.

## Lancement local vérifié

Dans le terminal PowerShell de VS Code, à la racine du dépôt :

```powershell
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --insecure --noreload
```

Garde ce terminal ouvert pendant ton essai ; Ctrl+C arrête le serveur. `--insecure` est l’option Django de développement servant les CSS/JavaScript malgré DEBUG=False. Elle ne désactive pas les contrôles CSRF ou les sessions. `--noreload` évite un second processus ; redémarre le serveur après une modification du code. La clé locale est chargée normalement par Django au démarrage, sans commande d’affichage, modification ou nouvelle génération de secret.

URL :

- Connexion : <http://127.0.0.1:8000/login>
- Page protégée : <http://127.0.0.1:8000/labs>

Utilise le même hôte `127.0.0.1` pendant tout le parcours. Aucun nouveau seed, migrate, changepassword ou pip install n’est nécessaire sur la copie déjà préparée. Le contrôle de démarrage effectué par Codex a été arrêté après les requêtes publiques ; il ne laisse pas de serveur tournant.

## Parcours navigateur à effectuer

1. Ouvre une fenêtre privée et accède directement à `/labs`. Attendu : redirection vers `/login?next=/labs`, sans identité ni catalogue affiché.
2. Utilise l’un de tes comptes et un mot de passe volontairement incorrect. Attendu : « Adresse e-mail ou mot de passe incorrect. », sans ouverture de session. Le bouton redevient utilisable.
3. Saisis personnellement le mot de passe correct. Attendu : ouverture de `/labs`, titre Laboratoires, ton e-mail et bouton Se déconnecter. La liste des laboratoires n’est pas encore construite.
4. Clique sur Se déconnecter. Attendu : retour à la connexion avec « Tu es déconnecté. ». Rouvre directement `/labs` : nouvelle redirection vers la connexion.
5. Recommence au clavier (Tab, Maj+Tab, Entrée) et à une largeur de téléphone. Attendu : libellés visibles, focus identifiable, contrôles accessibles, texte lisible sans défilement horizontal. Pour la checklist complète, vérifier aussi 380, 768 et 1280 pixels ; elle n’est pas cochée automatiquement.
6. Vérification courte du retour : ouvre `/login?next=https%3A%2F%2Fexample.com`, puis connecte-toi. Attendu : rester sur l’application, à `/labs`. L’URL externe n’est pas visitée par l’application.

Confirme seulement le résultat des étapes et les éventuels messages d’erreur. Ne transmets ni mot de passe, ni cookie, ni capture affichant une donnée sensible. La preuve du rejeu de l’ancien cookie est apportée par les tests isolés ; aucune extraction de ton cookie réel n’est nécessaire.

## Contrôles exécutés et portée

```powershell
.\.venv\Scripts\python.exe -m pytest -v
.\.venv\Scripts\python.exe manage.py check --settings=tests.settings
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run --settings=tests.settings
node --check src/static/js/login.js
node --check src/static/js/logout.js
node checks/ex2.mjs
git diff --check
```

- Suite exécutée : **71 tests réussis** (25 du socle, 46 du point 2). Les comptes/données automatisés sont créés par les tests et n’utilisent pas la base de démonstration. Le CSRF est réellement activé, avec refus du jeton absent/incorrect et de l’origine externe.
- AC-47 : connexion locale, message uniforme, compte inactif, formulaire HTML et JSON, rotation de session, retour interne. Les mots de passe et rôles sont préservés ; aucun compte créé.
- AC-46 : partie page et service d’accès uniquement, dont perte d’accès après désactivation du compte de test. Aucune preuve d’API de laboratoires.
- AC-49 : POST obligatoire, suppression de la session en base, refus de réutilisation de l’ancien cookie et protection CSRF. Aucune preuve d’API de laboratoires.
- AC-48 reste au point 3 ; les tests de données du point 1 ne constituent pas sa validation complète.
- `check` ne relève aucun problème ; `makemigrations --check --dry-run` ne détecte aucun changement. L’empreinte de la migration initiale est inchangée. Les deux fichiers JavaScript passent `node --check`.
- `node checks/ex2.mjs` : **31/32**, code de sortie 1 ; seul `the spec vs result note is filled in` échoue, comme attendu avant la vérification complète. `git diff --check` réussit (code 0). Aucun contrôle n’a été modifié pour obtenir ce résultat.
- Requêtes HTTP locales sans identifiants : connexion, CSS et deux scripts répondent 200 ; `/labs` répond 302 vers la connexion. Ce contrôle ne teste pas l’exécution JavaScript ni le rendu dans un navigateur.
- Revue indépendante effectuée une fois, en lecture seule : aucun défaut bloquant ou important. Une négociation plus fine de l’en-tête Accept est une amélioration différée si les besoins d’API évoluent ; les formulaires et scripts actuels utilisent les formats prévus. Aucune correction de code n’a été jugée nécessaire après cette revue.

À la fin du point 2, le rendu, le clavier et le parcours avec tes comptes restaient à vérifier manuellement. Tu as depuis confirmé la connexion/déconnexion au clavier et le focus visible ; le contrôle à 380 pixels reste reporté. Aucun test navigateur automatisé, essai Google/IA ou exécution Codespaces n’est revendiqué. Aucune dépendance, migration, modification du serveur MCP ou de CI n’a été ajoutée pendant ce point. La mesure de couverture et les observations du catalogue sont consignées dans CHECKPOINT3.md ; l’adaptation locale ultérieure de la CI et ses limites sont dans [TP2_FINALIZATION.md](TP2_FINALIZATION.md).

Références techniques consultées le 4 novembre 2026 : [authentification et sessions Django](https://docs.djangoproject.com/en/5.2/topics/auth/default/), [protection CSRF](https://docs.djangoproject.com/en/5.2/howto/csrf/) et [fichiers statiques en développement](https://docs.djangoproject.com/en/5.2/howto/static-files/).
