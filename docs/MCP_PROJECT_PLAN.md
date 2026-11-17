# Plan MCP projet — proposition à examiner

17 novembre 2026 · Base examinée : `5d830b1c15c60775c548dae81dc89c76c9fc2fb9`, arbre initial propre.
Autorisation actuelle : documentation seulement. Aucun mécanisme ci-dessous n'est implémenté ou validé fonctionnellement par ce plan.

Mise à jour après examen utilisateur : le plan est approuvé ; seule la
sous-étape 1 est autorisée à la construction et au commit local, sans push.
Son état et ses preuves sont dans [MCP_AUTH_1.md](MCP_AUTH_1.md).
Les contrats à six outils et le lanceur décrits ci-dessous restent la cible
des étapes suivantes : le mode projet de la sous-étape 1 n'expose que les deux
outils TP1, et aucune vraie clé de session n'est remise à Codex.

## 1. Session ordinaire Django

Recommandation : transmettre **la clé d'une session Django ordinaire**, dans
`LAB_BOOKING_MCP_SESSION`, héritée du processus client MCP. L'utilisateur ouvre
lui-même sa session locale dans l'application PostgreSQL du projet. Lui seul
copie la valeur de son propre cookie de session depuis les outils du navigateur,
la colle dans l'invite locale masquée du futur lanceur PowerShell, puis efface
son presse-papiers ; jamais dans le chat ou une capture. Codex ne voit pas cette
valeur. Cette saisie précède le démarrage du client. Aucun mot de passe
de compte n'est nécessaire au serveur MCP. Le lanceur ne passe jamais le jeton
dans ses arguments, un fichier de configuration ou l'historique du terminal ;
il fournit la variable uniquement à l'enfant client et retire sa propre variable
en `finally`, en préservant tout état préexistant. Le processus MCP ne lit
aucun cookie du navigateur et ne demande rien sur stdin, réservé au protocole.
Une nouvelle connexion ou rotation de session nécessite de relancer le client
avec la nouvelle clé. Ce parcours local de remise du jeton reste à construire
et examiner : aucun cookie ou secret existant n'a été consulté pour ce plan.

À **chaque appel projet**, un nouveau chargement de session depuis PostgreSQL
doit vérifier : expiration, données signées valides, backend autorisé,
identifiant issu de la session, utilisateur existant et actif, hash
d'authentification courant. Réutiliser `SessionStore`, le backend Django et la
comparaison constante de Django ; ne pas déduire l'authentification de la seule
existence d'une ligne de session. La couche de données résout ces informations ;
un service d'authentification construit `Actor` puis applique `require_authenticated`.
Ni `HttpRequest` factice ni appel à une route HTTP. Le cache de session/acteur
ne doit pas survivre à un appel.

Session absente, invalide, expirée, supprimée après déconnexion/révocation,
compte désactivé ou mot de passe changé : même refus `AuthenticationRequired`,
sans données métier. Ne pas renouveler silencieusement une session ; en cas de
rotation de clé secrète Django, demander une nouvelle connexion plutôt que
modifier la session du navigateur depuis MCP. La révocation interdit les appels
suivants ; elle n'annule pas rétroactivement une transaction déjà engagée.
Une panne de base produit une erreur interne expurgée, jamais un acteur par défaut.

Utiliser uniquement une session de compte ordinaire, jamais administrateur.
La proposition est de refuser les sessions `is_staff`/`is_superuser` à cette
entrée ; le rôle métier `personnel` n'est pas le drapeau Django `is_staff`.
Cela ne crée aucun privilège métier : seul un étudiant peut réserver, et seul
le propriétaire peut annuler, comme par HTTP. Ce périmètre d'authentification
MCP reste soumis à ton examen avant construction, sans changer la connexion HTTP.

La variable contient un secret en clair en mémoire : elle n'est pas un coffre.
Limiter son héritage au client de confiance et à ses enfants nécessaires,
éviter les dumps d'environnement, traces de requêtes et rapports de crash.
Ne jamais afficher le jeton, le hash, les cookies ou les profils. Aucun `.env`
supplémentaire ni jeton dans les arguments des outils ou dans leurs réponses.

## 2. Contrats des quatre outils

Tous les objets d'entrée sont fermés (`additionalProperties: false`) ; identifiants
entiers strictement positifs, sans booléens. Aucun `user_id`, `owner_id`, rôle ou
horloge fourni par le client. Dates-heures ISO 8601 avec fuseau, sorties UTC `Z`.
Les règles métier restent dans les services, pas dans les schémas MCP.

| Outil et description proposée (>20 caractères) | Entrée exacte | Succès et service directement appelé |
| --- | --- | --- |
| `list_free_slots` — « Consulter les créneaux réservables pour un laboratoire et une date ; cette lecture ne réserve rien. » | `laboratory_id`, `date` (`YYYY-MM-DD`, jour Europe/Sofia) | `{slots: [...]}` : poste id/nom, début/fin ; `booking_reads.list_available_slots(actor, laboratory_id, day)`. Ordre début puis id du poste ; liste vide possible. |
| `my_bookings` — « Consulter uniquement son historique de réservations, avec les annulations et l'état actuel des postes. » | `{}` | `{bookings: [...]}` : id, poste id/nom, laboratoire id/nom, début/fin, création/annulation, état du poste et statut ; `booking_reads.list_personal_bookings(actor)`. Début puis id décroissants. |
| `book_slot` — « Réserver pour soi un poste sur un créneau précis, après confirmation explicite et revérification des règles. » | `workstation_id`, `starts_at`, `ends_at` | `{booking: {...}}` : id, poste, début/fin, création, annulation nulle ; `booking_creation.create_booking(actor, workstation_id, starts_at, ends_at)`. Propriétaire exclusivement issu de l'acteur. |
| `cancel_booking` — « Annuler sa propre réservation avant son début ; une répétition restitue l'annulation existante sans la modifier. » | `booking_id` | `{booking: {...}}` : mêmes champs, date d'annulation conservée ; `booking_cancellation.cancel_booking(actor, booking_id)`. Contrôle du propriétaire avant tout retour idempotent. |

Sorties : JSON sérialisé dans `content` de type `text`, compatible avec le style
TP1 existant. Refus d'exécution : `isError: true`, contenu JSON
`{error: {code, message}}`, sans statut HTTP inventé ni trace brute.
Authentification commune : `AuthenticationRequired`. Entrées mal formées :
`InvalidToolInput`. Disponibilités : `InvalidReadInput`, `LaboratoryNotFound`.
Création : `StudentRequired`, `WorkstationNotFound`, `WorkstationUnavailable`,
`InvalidBookingInput`, `SlotNotFuture`, `WorkstationConflict`, `PersonalConflict`,
`QuotaExceeded`. Annulation : `InvalidBookingInput`, `BookingNotFound`,
`NotBookingOwner`, `CancellationTooLate`, `BookingChanged`.
Historique : authentification, ou erreur interne expurgée. Erreurs inattendues :
`InternalError`, sans transformer une panne en conflit métier.
Les erreurs JSON-RPC de protocole restent distinctes ; les comportements TP1
existants ne sont pas modifiés par cette nouvelle traduction.

## 3. Fichiers et compatibilité

- `mcp-server/server.py` : conserver la boucle stdio et ajouter un mode explicite
  `--project`. Sans ce mode, les deux outils TP1 et le démarrage Python standard
  restent autonomes, sans import Django ni chargement de profil PostgreSQL.
- Mode proposé : `.\.venv\Scripts\python.exe mcp-server/server.py --project`,
  depuis la racine, réglages `src.config.postgres` ; catalogue des **six** outils.
  Les tests imposent explicitement leurs réglages PostgreSQL isolés au processus.
  Session manquante : handshake/catalogue fonctionnels, appels projet refusés.
  Configuration de base inutilisable : arrêt sûr avec diagnostic expurgé.
- Nouveau `mcp-server/project_tools.py` : validation/dispatch/sérialisation,
  appel du service d'authentification puis des services existants. Aucun ORM,
  SQL, client HTTP ou import de `src/routes/booking_http.py` dans les outils.
- Nouveaux `src/services/session_auth.py`, `src/data/session_auth.py` : politique
  de session et résolution Django séparées. Aucun changement des règles de
  réservation, migrations, comptes ou données de développement.
- Futur `tools/start_mcp_client.ps1` : saisie masquée et héritage temporaire de
  l'environnement. Configuration client sans valeur secrète, à documenter.
- Garder les versions négociées `2025-11-25` et `2025-06-18`, les notifications
  sans réponse, les ids et erreurs existants. **stdout : JSON-RPC seulement** ;
  diagnostics génériques sur stderr, sans corps d'appel, paramètres ou secrets.

## 4. Confirmation et résultats incertains

L'agent présente poste, laboratoire, date et heures Europe/Sofia avant création,
puis attend une confirmation explicite. Avant annulation, il présente la
réservation et demande confirmation. Une consultation ne vaut pas confirmation.
Conserver les demandes d'autorisation du client, sans mode automatique global.
Ces instructions et descriptions guident l'agent : **le serveur ne peut pas
attester qu'un humain a approuvé dans un client MCP arbitraire**. Ne pas ajouter
un simple booléen prétendant le garantir. Après réponse réseau/protocole perdue,
consulter l'historique avant toute nouvelle mutation ; aucune relance automatique
de création. L'idempotence d'annulation ne dispense pas de vérifier le propriétaire.

## 5. Tests et trois sous-étapes proposées

1. **Authentification + mode projet**, avec tests de refus écrits en premier :
   session absente/inventée, données corrompues, expirée, supprimée, backend
   inconnu, hash absent/invalide, mot de passe changé, utilisateur supprimé ou
   inactif, session privilégiée. Sur un même processus, session valide puis
   déconnexion HTTP réelle/révocation : appel suivant refusé. Aucun secret dans
   stdout/stderr, erreurs ou arguments. Régression TP1 sans Django configuré.
2. **Deux consultations**, avec tests directs et sous-processus stdio réel :
   initialize → notification initialized → tools/list → tools/call. Six outils,
   descriptions ≥20 caractères, aucune fuite entre utilisateurs, ordre, liste
   vide, refus sans mutation. Fixtures validées/commitées sur la base **de test**
   pour être visibles depuis la connexion du sous-processus ; jamais la base dev.
3. **Deux mutations et équivalence HTTP/MCP** : succès, rôle, propriétaire
   (y compris réservation déjà annulée), quota, conflits, horaires et refus sans
   mutation ; répétition d'annulation sans nouvelle date. Comparer résultats
   métier et états finaux sur jeux initiaux identiques, sans passer par HTTP
   depuis les outils. Régressions concurrentes conservées. Vérifier le flux
   réel stdio et les appels aux fonctions partagées, pas seulement des mocks.

Chaque sous-étape : tests pertinents, diff, revue selon AGENTS, puis commit
distinct **seulement après autorisation de construction/enregistrement**.
Fichiers de tests proposés : `tests/test_mcp_session_auth.py` et
`tests/test_project_mcp.py`, en conservant `mcp-server/test_server.py` et son
vérificateur. Réutiliser pytest et la bibliothèque standard, sans nouvelle dépendance.
Traçabilité : titres exacts AC-37/38/39, et AC métier réellement prouvés ; aucun
AC renommé ou futur déclaré couvert par sa simple présence dans un titre.

## 6. CI, couverture et documents

Étendre les suites déjà lancées par `npm test`/la couverture aux nouveaux tests
avec PostgreSQL éphémère, migrations depuis une base vide et sessions synthétiques
créées uniquement pour les tests. Conserver le contrôle MCP TP1 séparé ; ajouter
la vérification du mode projet avec ses réglages de test, sans secret local en CI.
Inclure tout nouveau Python de production dans l'inventaire : services **100 %
lignes et branches**, global **≥80 % lignes**, serveur TP1 inclus. Aucun seuil
abaissé, fichier retiré ou contrôle neutralisé. Aucun changement CI maintenant.

Lors de la construction : actualiser SPEC (outils/auth/traçabilité/résultats
réels), AGENTS, README, USAGE et AGENT_LOG ; documenter lancement, fin de session,
erreurs et confirmation. Aucun essai Gemini nécessaire aux tests protocole.
Le précédent ex3 **11/18 sous Windows** reste un diagnostic historique, pas une
mesure de ce plan : `spawnSync npm ENOENT`, exigences IA, note personnelle et
traçabilité complète restent notamment ouvertes dans SLICE2_FINALIZATION.
Ne pas modifier le vérificateur pour le rendre vert. UI reportée, note/revue
personnelles, IA/Google, déploiement et ambiguïtés professorales restent ouverts.

## Sources effectivement relues

Pages récupérées par curl le 17 novembre 2026 après échec de l'outil Web :
- [TP3](https://webdev-course.tu-sofia.workers.dev/en/resources/exercises/3/),
  **Goal** et **Steps** : plan revu avant code, étapes testables, note personnelle.
- [Projet](https://webdev-course.tu-sofia.workers.dev/en/guides/project/),
  **The requirements, exactly**, **4. Your own MCP server, over your own API**,
  **7. Tests that trace, and 80% coverage**, **When you build which part** :
  ≥3 outils supplémentaires, descriptions ≥20 caractères, services identiques,
  session ordinaire en environnement, jamais administrateur, tests traçables.

Le mode optionnel, le nom de variable, le lanceur Windows et les contrats JSON
sont des propositions de Codex pour ce dépôt, pas des prescriptions du professeur.
