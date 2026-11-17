# IA — sous-étape 2 : transport borné et API, sans interface

17 novembre 2026. Base locale : `3fa6ecb238e64761d95cff5ac0299aee01fda01a`,
arbre propre au début. L'utilisateur autorise adaptateur REST, processus borné,
API protégée, tests hors fournisseur, documentation et commit local seulement.
Code et tests préparés par Codex. Aucune installation, migration, clé réelle,
requête Google, facturation, interface, nouveau MCP, push ou déploiement.

## Sources et conditions d'usage

Relues le 17 novembre 2026 : [modèle](https://aistudio.google.com/docs/models/gemini-3.5-flash-lite),
[REST](https://aistudio.google.com/api-reference/generate-content/generate-content),
[sorties structurées](https://aistudio.google.com/docs/structured-output) et
[erreurs/relances](https://aistudio.google.com/docs/troubleshooting).
Le modèle approuvé reste `gemini-3.5-flash-lite` ; pas de remplacement. JSON Schema
avec enum des candidats, MIME JSON, une seule réponse générée et validation
applicative après décodage. Les recommandations Google de backoff ne sont pas
appliquées ici : le projet impose une tentative, sans SDK et sans retry implicite.

**Fait documenté**, [conditions Google, « Use Restrictions »](https://aistudio.google.com/docs/terms#use-restrictions),
en vigueur depuis le 23 mars 2026 :

> You may use only Paid Services when making API Clients available to users in the European Economic Area […]

La même phrase vise aussi la Suisse et le Royaume-Uni.

La rubrique « Paid Services » qualifie l'accès Gemini API de payant lorsque le
projet Cloud est associé à une facturation active. L'exception régionale de
traitement des données dans « Unpaid Services » ne supprime pas la restriction
de mise à disposition. **Interprétation pour Lab booking** : un site proposé aux
étudiants à Sofia semble concerné ; aucune exemption pédagogique n'est établie
par ces passages. Le niveau gratuit annoncé ne suffit pas à autoriser cet usage.
Il faut clarifier le cadre avant usage réel, sans activation de facturation dans
cette tâche. Les essais hors réseau sont indépendants de cet accès. Aucun compte,
quota disponible ou autorisation de notre projet Google n'a été vérifié.

## Responsabilités et configuration

- `src/services/ai_suggestion.py` conserve toutes les règles de suggestion et les
  lectures de disponibilité ; seul le type ClientInvalidOutput est ajouté pour
  traduire proprement un refus du décodeur. Aucun ORM dans le service ou la route.
- `src/integrations/gemini_http.py` : **unique point REST**, uniquement bibliothèque
  standard, endpoint HTTPS fixe `v1beta/models/gemini-3.5-flash-lite:generateContent`.
  TLS vérifié ; opener ne contenant que HTTPSHandler, donc ni proxy ambiant,
  redirection, défi d'authentification, cookie, ni relance automatique.
- `src/integrations/gemini_worker.py` : lit le paquet privé sur stdin, appelle le
  transport et renvoie une sélection ou un code fixe. N'importe ni Django ni un
  profil de base, ne lit aucun dotenv et n'écrit aucun diagnostic sensible.
- `src/integrations/gemini.py` : fabrique de configuration et supervision du
  processus enfant avec le même interpréteur Python, à la racine du dépôt.
  Cette séparation précise le fichier unique envisagé dans le plan : elle évite
  d'initialiser Django dans le worker et isole transport, cycle de vie et HTTP.

Configuration future : `LAB_BOOKING_AI_ENABLED=1` **et** `GEMINI_API_KEY` dans
l'environnement du serveur applicatif. Par défaut, désactivé ; aucune clé n'est
même recherchée tant que le flag n'est pas explicite. Clé absente → client absent,
zéro processus et zéro réseau. Pas de chargement ou réutilisation Gemini CLI.
La tâche actuelle n'autorise **pas** d'activer ce chemin avec une vraie clé.

Le parent ne transmet que la clé applicative et les paramètres minimaux dans un
pipe stdin privé ; aucune clé dans argv, URL, repr, fichier ou environnement
enfant. En-tête REST x-goog-api-key. Environnement enfant limité aux chemins OS et
à l'instrumentation de couverture ; aucune identité/session/historique/profil.
Pas de besoin, réponse brute ou exception fournisseur dans les journaux. Le
texte libre peut néanmoins contenir lui-même des informations personnelles.

Bornes : paquet local de 16 Kio ; réponse HTTP et réponse IPC de 64 Kio chacune ;
génération limitée à 128 tokens. JSON strict (doublons/NaN/Infinity refusés), une
réponse terminée par STOP, une partie textuelle, candidat connu et schéma exact.
Blocage, vide, interruption, troncature, contenu trop grand ou invalide → repli,
jamais réparation par un second appel. Aucune garantie de qualité de suggestion.

## Échéance et nettoyage

Échéance monotone globale donnée par le service, plafonnée à cinq secondes par
l'adaptateur. Elle commence avant sérialisation/lancement et n'est pas réinitialisée
à chaque étape. **500 ms sont réservées dans ce budget au nettoyage** ; le résultat
doit donc arriver au plus tard vers 4,5 s, moins le lancement et la communication.
Le worker reçoit cette échéance de travail et un timeout socket restant ; c'est
la supervision du parent, et non ce timeout socket, qui borne l'ensemble.

Un thread gère les pipes avec tampon plafonné ; le parent attend une queue puis
la fin du worker uniquement avec un temps restant explicite. Sortie excessive :
refus immédiat avant toute attente de fin naturelle. Processus encore vivant :
kill, wait borné, join borné, vérification du thread et fermeture des pipes, dans
la même échéance. Aucun Future abandonné ni attente communicate/join illimitée.
Une erreur de nettoyage est une erreur d'infrastructure, pas une suggestion valide.

Les tests contrôlent la fin effective du processus et la fermeture des pipes,
pas seulement la présence d'un timeout dans le code. Ils incluent un enfant qui
ne lit pas stdin, un enfant bloqué, celui qui ferme stdout mais tarde à finir et
un wait artificiellement retardé de 250 ms après kill. Ces derniers vérifient la
marge de nettoyage au sein du budget. Tolérance de mesure : **350 ms** pour
ordonnancement/instrumentation, pas 350 ms ajoutées au délai configuré. Il ne
s'agit pas d'un système temps réel : suspension du système ou noyau défaillant
ne permettent pas une garantie physique universelle. Aucun processus restant
n'est accepté par les assertions de ces essais. Pas de preuve d'accès Google,
d'annulation du calcul chez le fournisseur ou de délai exact dans le navigateur.

## Endpoint livré

`POST /api/labs/{id}/suggestion`, JSON exact :

```json
{"date":"2030-01-07","need":"Un poste pour travailler"}
```

Session Django et CSRF requis. Identité exclusivement issue de la session ;
user_id/owner_id ou candidats fournis par le navigateur sont refusés. Date
canonique ; besoin validé par le service, sans troncature. Corps limité à 16 Kio.
La route parse, obtient l'acteur, injecte le client, appelle le service et sérialise.
`non_atomic_requests` préserve l'absence de transaction pendant l'attente, même
si ATOMIC_REQUESTS était activé plus tard ; test explicite en autocommit.

| Cas | HTTP et résultat |
| --- | --- |
| Suggestion validée/revérifiée | 200, status suggested, candidate depuis l'application |
| Aucun candidat | 200, status no_candidates, candidate null, message ; zéro appel |
| Pas de session/compte inactif | 401 JSON, aucun appel |
| Personnel / CSRF invalide | 403 ; les deux refus sont testés séparément |
| Laboratoire absent | 404 |
| Forme/date/besoin/champs/corps trop grand | 422 |
| JSON mal formé / méthode / Content-Type | 400 / 405 avec Allow / 415 |
| Candidat devenu indisponible | 409, code candidate_unavailable |
| Désactivé/clé absente, quota ou panne | 503, code explicite |
| Délai | 504, code timeout |
| Sortie invalide | 502, code invalid_output |

Les réponses ne sont pas mises en cache. Un échec n'est jamais un succès IA :
status unavailable, candidate null, phrase lisible et code stable. L'API de
disponibilités manuelles reste utilisable après ces échecs ; aucune UI IA ou
preuve visuelle de ce repli n'est livrée. Aucune réservation créée/annulée.

## Commandes et preuves

À la racine, PowerShell, base PostgreSQL de **test dédiée** seulement :

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_gemini_adapter.py tests/test_ai_suggestion_api.py tests/test_ai_suggestion.py tests/test_ai_json_limits.py --ds=tests.settings_postgres --reuse-db -q
.\.venv\Scripts\python.exe tools/check_coverage.py --postgresql
```

La suite désactive les clients ambiants (sans lire les clés). Tests API : session/
CSRF réels et vrais services/PostgreSQL, client substitué ; un garde interdit
l'adaptateur réel. Tests REST : réponses HTTP injectées et sockets Python
interdits. Tests processus : programme local tests/ai_worker_fixture.py, sans
réseau ; entrée réelle du worker testée avec paquet vide incapable d'appeler le
fournisseur. Les configurations activées sont des mappings explicitement factices.
L'environnement Windows persistant reste intact.

AC-29 : bornes/parsing/schéma et vraie disponibilité ; AC-30 : vide/zéro appel et
message API ; AC-31 : modèle fixe et payload minimal inspectés ; AC-32 : données
applicatives de la suggestion ; AC-33 : sorties et candidats périmés ; AC-35 :
configuration absente, quota/panne et tentative unique ; AC-36 : simulations HTTP
et vrais processus locaux mesurés/reapés. Les parties UI restent non validées.
AC-34 (confirmation d'une suggestion depuis l'écran) reste à intégrer.

## Résultats de la version finale

- **129 tests ciblés réussis**, incluant service, transport, API et refus du corps
  excessif avant lecture. Test API avec vraie session/CSRF, faux fournisseur et
  PostgreSQL ; aucune preuve d'écran ou d'appel Google déduite de ces tests.
- Couverture/régression **PostgreSQL** : **540 réussis, 1 désélectionné**, puis
  **9 tests TP1 réussis**. Le seul test désélectionné,
  `test_guard_refuses_unmarked_or_wrong_database`, spécifique au garde SQLite
  historique, a réussi séparément (**1 test**) avec les réglages SQLite isolés.
- Services : **322/322 lignes et 108/108 branches (100 % chacun)**. Global Python :
  **1 765/1 865 lignes (94,64 %)**, **445/488 branches (91,19 %)**, TP1 inclus.
  Les quatre modules d'intégration et la route sont dans l'inventaire ; aucune
  exclusion ou seuil modifié. Rapport local ignoré :
  `.local/coverage/6b37ecda75914bd59dc49b85ec9da0cb/coverage.json`.
  Le warning no-data-collected du parent unittest ne supprime pas les données
  effectivement mesurées des serveurs TP1 enfants. Pas de nouvelle mesure globale
  SQLite ni de résultat GitHub Actions revendiqué.
- Régressions Node **23/23**, contrôle MCP TP1 **12/12**, ex2 **32/32** ; contrôle
  Django `--settings=tests.settings` sans erreur, `git diff --check` propre.

Chronométrage Windows local, version finale, du début de l'appel jusqu'au retour
après nettoyage (budget 5 s, tolérance d'assertion 350 ms) :

| Processus contrôlé | Secondes observées |
| --- | ---: |
| Réponse normale | 0,262753 |
| Bloqué | 4,512714 |
| Ne lit pas stdin | 4,517720 |
| Sortie excessive | 0,187992 |
| Arrêt inattendu | 0,192865 |
| Ferme stdout, tarde à finir | 4,510447 |
| Nettoyage retardé de 250 ms | 4,763058 |

Les six autres cas d'erreur IPC terminent entre 0,150987 et 0,235163 s. Treize
scénarios vérifient qu'aucun enfant n'est encore vivant et que ses pipes sont
fermés ; ce sont des observations de test, pas une validation réseau ou Linux.

Revue indépendante personnalisée, lecture seule : aucun constat bloquant ou
important. Amélioration retenue/corrigée : prise en charge d'HTTPError429 même
pour un opener injecté, classé quota, corps fermé sans lecture. Le chemin normal
de l'opener HTTPSHandler seul utilisait déjà response.status ; aucune fausse
déclaration de bug sur ce chemin. Tests spécifiques échouant avant correction,
puis réussis. Aucun constat écarté ; limites réelles conservées ci-dessus.

Le rapport JUnit local de chronométrage est ignoré :
`.local/ai-transport-2.xml`. Aucun test avec clé réelle et aucune observation
navigateur à cette sous-étape. Note personnelle, validation complète Gemini MCP,
Google OIDC et UI reportées, dont 380 pixels, restent ouverts.
