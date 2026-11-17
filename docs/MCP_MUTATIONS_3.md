# MCP — sous-étape 3 : création et annulation

Finalisation ultérieure : connexion MCP-only de Gemini CLI observée avec identité
factice, sans appel fournisseur ; les appels d'outils et la vraie remise du jeton
restent en attente. Configuration et publication :
[MCP_FINALIZATION.md](MCP_FINALIZATION.md). Les preuves ci-dessous restent celles
de la sous-étape 3.

## Livraison et contrats

Le mode `--project` ajoute `book_slot` et `cancel_booking` aux quatre outils
déjà présents. Sans ce mode, les deux outils TP1 restent autonomes, sans Django
ni connexion PostgreSQL. Aucun service métier, migration, dépendance ou CI modifié.
L'incident PostgreSQL est déjà traité : sa rotation n'a pas été répétée.

| Outil | Entrée exacte (objet fermé) | Service directement appelé | Succès |
| --- | --- | --- | --- |
| `book_slot` | `workstation_id` entier positif, `starts_at`, `ends_at` ISO 8601 avec fuseau | `booking_creation.create_booking(actor, workstation_id, starts_at, ends_at)` | `{booking:{id,workstation_id,starts_at,ends_at,created_at,cancelled_at:null}}` |
| `cancel_booking` | `booking_id` entier positif | `booking_cancellation.cancel_booking(actor, booking_id)` | Même objet, avec date d'annulation conservée ; répétition autorisée sans nouvelle mutation. |

Les dates de sortie sont UTC Z. `structuredContent` et le JSON de `content[0].text`
correspondent exactement. Le gestionnaire authentifie à nouveau la session puis
valide seulement la forme ; les services appliquent rôle, disponibilité, horaires
Sofia, début futur, quota, conflits, propriétaire, limite d'annulation et transaction.
Ni ORM, SQL, couche de données ou détour HTTP dans les outils. Le propriétaire
vient uniquement de l'acteur ; `user_id`/`owner_id` et tout champ supplémentaire
sont refusés, ainsi que booléens et dates sans fuseau.

Les refus métier connus deviennent `isError:true` et `{error:{code,message}}` :
StudentRequired, WorkstationNotFound, WorkstationUnavailable, InvalidBookingInput,
SlotNotFuture, WorkstationConflict, PersonalConflict, QuotaExceeded, BookingNotFound,
NotBookingOwner, CancellationTooLate et BookingChanged. AuthenticationRequired
reste distinct ; les formats invalides deviennent InvalidToolInput, les pannes
inattendues InternalError. Aucun texte d'exception, chaîne SQL, secret ou identité
d'autrui n'est sérialisé. Les erreurs JSON-RPC de protocole restent séparées.

## Confirmation et incertitude

Descriptions ≥20 caractères, annotations standard : `readOnlyHint:false` et
`openWorldHint:false` pour les deux ; création `idempotentHint:false` et
`destructiveHint:false` (ajout) ; annulation `idempotentHint:true` et
`destructiveHint:true` (changement d'état). Un client peut ignorer ces indications.
Elles ne sont ni une preuve de consentement humain, ni une barrière de sécurité.
Le serveur applique toujours les permissions, mais ne peut pas attester qu'un
humain a approuvé dans un client arbitraire. Aucun champ `confirmed` trompeur.

L'agent doit présenter le poste, le laboratoire, la date et les heures Sofia,
puis demander une confirmation explicite avant création ; même principe avant
annulation. Conserver les confirmations du client, sans approbation globale.
Aucune relance automatique de mutation après un transport incertain : une réponse
perdue ne prouve pas l'échec de création. Consulter `my_bookings`, examiner l'état,
puis demander une nouvelle décision si nécessaire. L'idempotence d'annulation ne
dispense pas de cette prudence ni du contrôle du propriétaire ; elle concerne
l'effet après une première annulation, pas la disponibilité éternelle de la session.

## Tests et preuves

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_mcp_mutations.py tests/test_mcp_reads.py tests/test_project_mcp.py tests/test_mcp_session_auth.py tests/test_secret_error_safety.py --ds=tests.settings_postgres --reuse-db -q
.\.venv\Scripts\python.exe tools/check_coverage.py --postgresql
node mcp-server/check.mjs -- .\.venv\Scripts\python.exe mcp-server/server.py
node checks/ex2.mjs
git diff --check
```

Échec pertinent avant implémentation : le test de catalogue attendait six outils
et n'en trouvait que quatre. Après ajout : **92 tests ciblés réussis**.
Régression complète PostgreSQL : **411 tests réussis, 1 désélectionné** (le seul
test historique spécifique à SQLite), puis **9 tests TP1 réussis**. Le test
`test_guard_refuses_unmarked_or_wrong_database` conserve son assertion et réussit
séparément avec `tests.settings_sqlite_legacy` (**1 réussi**, base temporaire).
**23 tests Node**, MCP TP1 **12/12**, ex2 **32/32**, contrôle Django et diff propres.

Couverture PostgreSQL : services **227/227 lignes et 76/76 branches (100 %)** ;
global Python **1438/1524 lignes (94,36 %)** et **342/378 branches (90,48 %)** ;
adaptateur projet **90/90 lignes et 30/30 branches**. TP1, réglages et outils
existants sont inclus ; inventaire, seuils et exclusions inchangés. Rapport
ignoré : `.local/coverage/083c4a5190894e708dc38a20957320df/coverage.json`.
L'avertissement coverage du sous-processus TP1 `-S` reste attendu ; les autres
processus mesurent réellement ce serveur. Aucune preuve de CI distante présumée.

Revue indépendante en lecture seule : aucun défaut fonctionnel/sécurité bloquant.
Deux constats retenus : attendre la relance ciblée après les assertions renforcées
(terminée **92/92**, puis catalogue renforcé **1/1**) et corriger les docstrings
obsolètes du runtime/adaptateur. Aucun constat écarté. Les changements après la
mesure complète sont des assertions/titres de tests, retours à la ligne et
docstrings, sans modification du comportement de production mesuré.

Les tests utilisent seulement `test_lab_booking_1a` sur 5433, des sessions Django
synthétiques et une horloge contrôlée dans le processus serveur stdio. Les 14 cas
de création et 8 d'annulation sont rejoués par HTTP avec CSRF actif depuis les
mêmes lignes initiales. La restauration de fixtures ne concerne que cette base
de test : aucune réservation de démonstration n'est supprimée. Les IDs générés
des créations sont normalisés pour comparer les effets ; chaque ID renvoyé par
MCP est aussi vérifié contre sa ligne persistée et son propriétaire authentifié.
Les représentations des erreurs diffèrent (statut HTTP / code d'outil), leurs
décisions et effets sont comparés.

Les refus sont comparés à une empreinte avant/après des lignes Booking/Session ;
annulation validée : même ligne et seul cancelled_at change. Deux annulations
successives via stdio conservent le timestamp ; après annulation, une répétition
après le début est encore acceptée. Un test direct de l'adaptateur, instrumentant
la couche de données uniquement dans le test, compte une seule écriture pour
deux appels. Ce dernier n'est pas présenté comme une observation SQL du processus
stdio. Autre propriétaire refusé même si la ligne est déjà annulée ; poste hors
service annulable. Session absente/inconnue/révoquée refusée sans mutation.

AC-37 et AC-38 ont des preuves automatisées stdio pour les six outils / quatre
outils projet. AC-39 est démontré pour les scénarios de parité cités, pas tous
les comportements possibles. Les tests concurrents existants sont conservés ;
aucun nouvel ordonnancement concurrent par MCP n'est revendiqué. Aucun essai
Gemini, appel IA, vrai jeton ou parcours avec le client final n'a été effectué.

## Procédure du futur essai client — préparée, non exécutée

1. Choisir le client final et vérifier son lancement stdio depuis la racine du
   dépôt : `.\.venv\Scripts\python.exe mcp-server/server.py --project`, profil
   PostgreSQL de développement explicite, sans réglage de test hérité. Vérifier
   auparavant son héritage d'environnement et ses confirmations ; aucune
   configuration client existante n'est modifiée par cette livraison.
2. Lors d'une prochaine étape autorisée, ouvrir une session ordinaire de
   démonstration PostgreSQL. L'utilisateur seul remet sa clé via une invite
   locale masquée d'un lanceur encore à préparer/vérifier ; jamais dans le chat,
   une capture ou des arguments. Variable `LAB_BOOKING_MCP_SESSION` limitée à
   l'enfant client, sans fichier secret supplémentaire ni environnement Windows
   persistant ; effacer le presse-papiers si utilisé. Ne pas reprendre une ancienne
   clé depuis des logs. Ce n'est ni OAuth ni une connexion automatique.
3. Vérifier le catalogue réel à six outils, puis l'historique et les disponibilités
   du laboratoire dédié. Demander une création seulement sur un créneau retourné,
   après résumé et confirmation explicite. Relever uniquement outil, arguments
   métier, résultat et effet visible, jamais en-têtes ou jetons.
4. Vérifier la présence de la réservation dans l'historique, demander confirmation
   avant son annulation, puis vérifier sa conservation avec cancelled_at.
   En cas de transport incertain, arrêter les mutations et relire l'historique ;
   ne pas renvoyer automatiquement la création ou l'annulation.
5. Après déconnexion de cette même session Django, vérifier le refus d'un prochain
   appel projet. Une autre session du navigateur ou une simple fermeture de son
   onglet n'est pas la révocation de la session remise au client.

Cette procédure dépend de la compatibilité du client et du futur lanceur ; elle
ne vaut pas autorisation de lancer Gemini maintenant. Note/revue personnelles,
vérifications UI reportées, Google, IA et déploiement restent hors de cette étape.
