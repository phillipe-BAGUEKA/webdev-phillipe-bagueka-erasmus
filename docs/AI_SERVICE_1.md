# IA — sous-étape 1 : service injectable seulement

Ce bilan historique reste conservé. La sous-étape 2 ajoute transport borné et
API, toujours sans interface ni fournisseur réel : voir `AI_TRANSPORT_2.md`.

Le 17 novembre 2026, l'utilisateur a approuvé le besoin textuel de 1 à 1 000
caractères après trim, le laboratoire et la date sélectionnés, les dix candidats
distincts maximum dans l'ordre existant, zéro appel sans candidat et aucune
réservation par une suggestion. Implémentation et premières formulations de
tests produites par Codex ; aucune compréhension ou note personnelle présumée.
Le plan antérieur reste dans `AI_SUGGESTION_PLAN.md`, avec son statut actualisé.

## Contrat livré et chemin des données

`suggest_slot(actor, laboratory_id, day, need, *, client, clock, timer)` dans
`src/services/ai_suggestion.py`. `clock` fournit l'instant métier conscient du
fuseau ; `timer` une horloge monotone pour l'attente du client. Les deux sont
injectables et ont des valeurs par défaut. Le contrat ne dépend ni de HTTP ni de
MCP. L'acteur vient d'un adaptateur authentifié, jamais d'un identifiant client.

1. `require_authenticated` puis `src/data/users.py:account_state` relisent rôle
   et activité, sans mot de passe, transaction ni verrou. L'acteur doit rester
   étudiant actif ; erreurs existantes AuthenticationRequired/StudentRequired.
2. Besoin chaîne, trim, 1–1 000 caractères, NUL refusé, aucune troncature.
   `InvalidSuggestionInput` pour un besoin invalide ; validation laboratoire/
   date/horloge déléguée aux lectures existantes (InvalidReadInput et
   LaboratoryNotFound). Aucun nouvel horaire ou horizon ajouté.
3. `list_available_slots` réutilise service → données → ORM. Conserver son ordre,
   dédupliquer les couples poste/début/fin, retenir dix maximum, leur attribuer
   `c1`…`c10` uniquement en mémoire. Le service conserve la correspondance avec
   l'identité applicative ; le modèle ne fournit ni poste ni horaire arbitraire.
4. Une seule invocation de `SuggestionClient.select_candidate(need, candidates,
   deadline=…)`. Le tuple de candidats immuables contient seulement identifiant
   temporaire, nom du poste, début et fin UTC ; aucun acteur, identifiant
   utilisateur, e-mail, session ou historique. Aucune caractéristique matérielle
   ajoutée. Le texte libre peut toutefois contenir lui-même des données
   personnelles : validation de longueur ne signifie pas anonymisation.
5. Objet décodé exact `{"candidate_id": "cN"}`, unique champ, type chaîne exact,
   identifiant appartenant à cet appel. Autres formes/types/champs refusés.
   Le futur décodeur devra refuser les clés JSON dupliquées et les réponses
   tronquées : le service ne peut pas retrouver des doublons déjà perdus lors
   d'un décodage. Aucun texte brut du client affiché ou journalisé.
6. Après réponse valide, relire le compte, l'heure et toutes les disponibilités.
   Chercher le même poste/créneau dans cette liste entière ; ne pas refaire une
   sélection limitée à dix qui pourrait évincer un candidat toujours valable.
   Renvoyer les valeurs applicatives actuelles, y compris le nom actualisé.

`SuggestionResult` :

| status | candidate | reason |
| --- | --- | --- |
| suggested | AvailableSlot relu depuis l'application | None |
| no_candidates | None | None |
| unavailable | None | not_configured, timeout, quota, provider_error, invalid_output ou candidate_unavailable |

`client=None` produit `not_configured`, sans appel. Les erreurs typées
ClientUnavailable et ClientQuotaExceeded se traduisent en motifs stables ;
TimeoutError en timeout. Les exceptions provenant de l'invocation du client sont
sanitisées en provider_error, sans leur message. Les erreurs de base ou de
lecture ne sont pas absorbées comme erreurs fournisseur. Le repli est un état
explicite pour la future sélection manuelle, jamais une « suggestion IA réussie ».

## Budget, concurrence et portée des preuves

Le service passe une échéance monotone de cinq secondes et refuse une réponse
reçue à l'échéance ou après. Il ne relance pas. **Il n'interrompt pas une fonction
injectée bloquante** : le futur transport devra respecter cette échéance,
nettoyage compris. Pas de processus, socket, clé, fournisseur ou thread livré
ici, donc aucune durée réseau réelle ni AC-36 complet revendiqué.

Le service n'ouvre aucune transaction et n'acquiert aucun verrou. Un test
PostgreSQL en autocommit (hors transaction enveloppante pytest) inspecte cet
état pendant l'appel. Les futurs appelants doivent eux aussi rester hors
transaction pendant l'attente. La lecture finale est provisoire : la suggestion
ne réserve rien ; après confirmation explicite future, `create_booking`
revérifiera toutes les règles transactionnellement. Aucun test de nouvelle
concurrence ou parcours HTTP/UI IA à cette étape.

## Tests et traçabilité

Commande ciblée PowerShell à la racine :

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_ai_suggestion.py --ds=tests.settings_postgres --reuse-db -q
```

`tests/test_ai_suggestion.py` utilise uniquement utilisateurs, postes et réservations
isolés de test PostgreSQL (aucune session personnelle). Les clients
sont des objets Python factices, sans accès réseau ni lecture de clé.

- AC-29 : validation/permissions, trois candidats et > dix, ordre et dédoublonnage.
- AC-30 : zéro candidat → zéro appel, état vide sans mutation ; UI à construire.
- AC-31 : payload minimal ; avertissement UI et sélection du modèle réel futurs.
- AC-32 : candidat unique depuis les données et absence de mutation ; UI future.
- AC-33 : sorties invalides et données devenues indisponibles, acteur relu ;
  aucune explication visuelle testée.
- AC-34 : création/confirmation inchangées et non intégrées à la suggestion ;
  aucun test ajouté ne revendique ce parcours.
- AC-35 : client absent et erreurs simulées, pas de retry ; aucune clé lue et
  aucun adaptateur de configuration/fournisseur ou repli UI livré.
- AC-36 : échéance/timeout simulés, réponse tardive rejetée ; transport non prouvé.

Premier lancement avant implémentation : test de refus AC-29-anonymous échoue
avec ModuleNotFoundError pour le service manquant. Après implémentation, une
erreur de préparation du test « trois candidats » a été corrigée : à 13:00 UTC
en hiver, seuls deux créneaux restent strictement futurs ; à 12:00 UTC, il en
reste trois. L'assertion de trois candidats et la règle métier sont conservées.

## Résultats effectivement obtenus

- Tests directs ci-dessus : **51 réussis**.
- `.\.venv\Scripts\python.exe tools/check_coverage.py --postgresql` :
  **462 réussis, 1 désélectionné**, puis **9 tests TP1 réussis**. Le seul test
  désélectionné est `test_guard_refuses_unmarked_or_wrong_database`, propre au
  garde SQLite historique ; son lancement séparé avec
  `--ds=tests.settings_sqlite_legacy` réussit **1 test**. Les tests concurrents
  et stdio MCP existants font partie de cette régression PostgreSQL.
- Mesure locale Windows/PostgreSQL : services **319/319 lignes, 108/108 branches**,
  soit **100 %** pour chacun ; nouveau service **92/92 et 32/32**. Global Python
  **1 532/1 618 lignes (94,68 %)** et **374/410 branches (91,22 %)**, TP1 inclus.
  Rapport local ignoré :
  `.local/coverage/b2c0c78297e145d59aefee34ab9ec312/coverage.json`.
  Inventaire, seuils et exclusions inchangés ; aucune mesure globale SQLite
  supplémentaire. Le warning « no-data-collected » du parent unittest exclu
  ne supprime pas les données des serveurs enfants, présentes dans le rapport.
- `node --test tests/labs_ui.test.mjs tests/booking_ui.test.mjs tests/test_runner.test.mjs` :
  **23 réussis** ; contrôle MCP TP1 **12/12** ; ex2 **32/32** ; contrôle Django
  `--settings=tests.settings` sans erreur ; `git diff --check` propre.
- Premiers lancements sandbox : la couverture s'est arrêtée à **425 réussis,
  37 erreurs de préparation, 1 désélectionné**, à cause du répertoire temporaire
  pytest inaccessible. Les tests Node/MCP ont eu `spawn EPERM`. Les mêmes
  commandes relancées hors sandbox réussissent ; aucun test/contrôle affaibli.
- Revue indépendante personnalisée en lecture seule : aucun problème bloquant
  ou important. Une ambiguïté du README a été retenue/corrigée : seule
  l'intégration complète reste future, le service injectable est livré. Aucun
  constat écarté ; les limites de transport/HTTP/UI restent explicites.

Voir également l'entrée correspondante dans AGENT_LOG.md.
Les conditions Google EEE, l'accès effectif, le client réseau, la route, l'écran,
la note personnelle et les UI reportées restent ouverts. Aucun push à ce jalon.
