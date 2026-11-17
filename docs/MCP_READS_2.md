# MCP — sous-étape 2 : consultations authentifiées

Preuves historiques de la sous-étape 2 : la sous-étape 3 ajoute ensuite les deux
mutations et leur couverture stdio/HTTP, sans répéter la rotation. État courant :
[MCP_MUTATIONS_3.md](MCP_MUTATIONS_3.md). Le client final reste non vérifié.

## Incident PostgreSQL : rotation réellement effectuée

Les preuves de la sous-étape 1 disaient explicitement « rotation non effectuée ».
Sur autorisation de l'utilisateur, le 17 novembre 2026, l'outil ciblé
`tools/rotate_postgres_test_password.py` a remplacé uniquement le mot de passe
du rôle `lab_booking_1a_test`, sur `127.0.0.1:5433`, base `test_lab_booking_1a`.
Valeur aléatoire générée en mémoire ; aucune valeur dans les arguments, sorties
ou journaux. Le rôle change son propre mot de passe, sans compte bootstrap.
Instance/port/base/rôle et absence de journalisation SQL vérifiés avant DDL ;
un vérificateur SCRAM est calculé côté client. Aucun réglage serveur n'est modifié.

Résultat réellement observé : nouvelle connexion réussie, ancienne valeur
explicitement refusée pour authentification, ACL Windows du profil identiques
avant/après. Le profil `.local/postgres-1a-test.json` est mis à jour en place ;
ses autres champs sont conservés. Reçu sans secret :
`.local/postgres-test-password-rotation.json`. Tous deux ignorés et non suivis.
Ne pas relancer la rotation : la présence de ce reçu la bloque volontairement.
Aucun changement du rôle dev, des comptes étudiants, de la base dev ou de 5432.

`pytest.ini` utilise maintenant `--tb=short` par défaut pour éviter les arguments
de connexion dans les longues traces pytest. Un sous-processus pytest fait
échouer un vrai `psycopg.connect` avec identifiants factices, sur un port local
réservé sans serveur : le détail de l'erreur reste visible, sa valeur factice
n'apparaît pas par défaut. Le même test avec `--tb=long` retrouve cette valeur
dans la sortie capturée seulement en mémoire : preuve que le test détecte la
régression de configuration, sans jamais imprimer la valeur. Aucune base active
n'est contactée pour cet échec. Tests complémentaires : erreur de pilote
expurgée dans le CLI de rotation et à la frontière MCP ; rotation simulée sans
contact réel avec PostgreSQL. Cela ne garantit pas la sécurité d'un utilisateur
qui impose ensuite des traces longues, des dumps d'environnement ou du debug SQL.

## Contrats livrés

Commande depuis la racine :

```powershell
.\.venv\Scripts\python.exe mcp-server/server.py --project
```

Cette commande utilise le profil de développement existant ; elle n'a pas été
essayée avec une vraie clé ou le client MCP final. Les tests imposent les réglages
PostgreSQL de test au sous-processus et lui passent une session synthétique par
`LAB_BOOKING_MCP_SESSION`, jamais par argument. Aucun lanceur manuel n'est ajouté.

| Outil | Entrées exactes | Sortie |
| --- | --- | --- |
| `list_free_slots` | `laboratory_id` entier positif, `date` YYYY-MM-DD (jour Europe/Sofia) | `{slots:[...]}` : poste id/nom et début/fin UTC Z, dans l'ordre du service. Aucun propriétaire ou détail de réservation d'autrui. |
| `my_bookings` | `{}` (arguments absents acceptés) | `{bookings:[...]}` : historique personnel, dates UTC, état actuel du poste et statut ; ordre début/id décroissants. |

Objets d'entrée fermés ; `user_id`, `owner_id`, champs supplémentaires, booléens
à la place d'identifiants et dates invalides refusés. Les descriptions dépassent
vingt caractères ; annotation `readOnlyHint` seulement informative. Pas de
`book_slot` ni `cancel_booking`. Le mode projet expose donc **quatre** outils ;
le mode par défaut garde ses deux outils TP1 et son autonomie sans Django.

À chaque appel projet : `project_tools.call_tool` → `project_runtime.current_actor`
→ authentification de session Django → `booking_reads.list_available_slots` ou
`list_personal_bookings` → couche de données/ORM. Aucun ORM, SQL, accès direct aux
données ou requête HTTP dans le gestionnaire MCP. Les règles métier et les
permissions restent dans les services existants, non modifiés.

Les réponses ont un objet `structuredContent` et le même objet JSON dans
`content[0].text`. Succès avec `isError:false`, y compris liste vide. Refus avec
`isError:true` et `{error:{code,message}}` : `AuthenticationRequired`,
`InvalidToolInput`, `InvalidReadInput`, `LaboratoryNotFound`, ou `InternalError`
pour une panne inattendue. Messages expurgés, pas de trace ni de détail pilote.
Les erreurs JSON-RPC TP1 restent distinctes. stdout contient seulement le protocole.

## Vérifications

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_mcp_reads.py tests/test_project_mcp.py tests/test_mcp_session_auth.py tests/test_secret_error_safety.py --ds=tests.settings_postgres --reuse-db -q
.\.venv\Scripts\python.exe tools/check_coverage.py --postgresql
node mcp-server/check.mjs -- .\.venv\Scripts\python.exe mcp-server/server.py
node checks/ex2.mjs
git diff --check
```

Échec initial pertinent : le test stdio attend les quatre noms et échoue sur
l'absence des deux lectures ; aucune assertion n'a été retirée pour les ajouter.
Les premières vérifications ciblées passent (46 tests), puis les tests sont
complétés avec la comparaison aux services directs et les erreurs synthétiques.

Mesure finale après revue par le lanceur PostgreSQL existant : **369 tests réussis,
1 désélectionné**, puis **9 tests TP1 réussis**. Le test désélectionné,
`test_guard_refuses_unmarked_or_wrong_database`, conserve son assertion SQLite
et réussit séparément avec `tests.settings_sqlite_legacy` (**1 réussi**).
**23 tests Node**, MCP TP1 **12/12**, ex2 **32/32** ; contrôle Django et
`git diff --check` réussis. Résultats locaux, aucune nouvelle exécution CI présumée.

Couverture Python PostgreSQL : services **227/227 lignes et 76/76 branches**
(100 % chacune), global **1405/1491 lignes (94,23 %)** et **326/362 branches
(90,06 %)**. Le nouvel adaptateur `project_tools.py` atteint **57/57 lignes et
14/14 branches**. TP1 et l'outil de rotation sont inclus dans l'inventaire ;
aucun seuil ou exclusion changé. Rapport ignoré :
`.local/coverage/f33f2ba1e98247a7af487d4abe214cac/coverage.json`.
L'avertissement coverage du sous-processus TP1 `-S` reste attendu : celui-ci
prouve l'autonomie sans site-packages ; les autres sous-processus mesurent TP1.

Preuves des tests : vraies connexions PostgreSQL et sessions Django synthétiques,
fixtures commitées avant le sous-processus, horloge fixe du 7 janvier 2030 dans
les deux processus. initialize, notification sans réponse et tools/list/call
réels ; attentes bornées, processus et flux fermés même en échec. Session absente,
inconnue et révoquée entre deux appels au même processus ; historique du seul
propriétaire, erreurs d'entrée, laboratoire absent, listes vides, état annulé
conservé et poste hors service. Comparaison avec les services et les GET HTTP
correspondants. Empreinte des lignes Booking/Session avant/après les consultations
pour prouver l'absence de mutation sans afficher leurs clés dans les assertions.
La préparation des fixtures modifie seulement la base de test, jamais la démo.

Revue indépendante en lecture seule : deux constats retenus, aucun écarté.
Le test d'incident initial simulait seulement une exception générique ; il passe
désormais par le pilote psycopg réel avec la preuve contraire en traces longues.
L'adaptateur refuse explicitement un nom inconnu plutôt que de le traiter comme
une consultation de disponibilités. Ce refus interne est testé sans appel au
service ; le protocole garde son erreur JSON-RPC existante pour un outil inconnu.
Après ces corrections : **50 tests ciblés réussis** ; couverture complète relancée.

AC-37/38/39 restent **partiels** : seulement deux outils projet et leur parité en
lecture. Les mutations et le parcours avec le client final restent non vérifiés.
La rotation et les preuves automatisées ne valident ni remise manuelle, ni OAuth,
ni utilisation par Gemini. Aucune nouvelle dépendance, migration ou CI modifiée.
Note/revue personnelles, UI reportée, IA, Google et déploiement restent ouverts.
