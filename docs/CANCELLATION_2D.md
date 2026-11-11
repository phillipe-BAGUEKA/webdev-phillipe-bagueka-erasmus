# Jalon 2D — annulation par le propriétaire

Périmètre consigné avant implémentation : état Git propre au commit
13fd34c01c3f06ef353ddf0fe353cedd701b870e. Service indépendant du transport,
tests PostgreSQL directs AC-25/26/27/28 et ordres concurrents maîtrisés.

Plan : refus d'abord et constat rouge, annulation transactionnelle avec ordre
utilisateur → poste → réservation, vérifications faisant autorité après verrous,
répétition sans mutation ; tests directs et concurrents avec la méthode de 2C ;
régression/couverture, revue indépendante puis commit local autorisé, sans push.
Les rôles ne donnent aucun droit d'annuler autrui ; aucun droit d'annulation
n'est retiré au propriétaire actif uniquement parce que son rôle a changé.

La première annulation exige maintenant < début ; une répétition autorisée ne
réapplique pas cette limite. Authentification et propriété restent obligatoires.
Le poste hors service n'empêche pas l'annulation. Aucun endpoint ni HTTP 200
implémenté : cette traduction reste future. Pas de migration, dépendance, CI,
seed, modification SQLite/5432, MCP ou IA. Regroupement définitif Slice 2 et
note d'architecture personnelle ouverts. Code et rédaction assistés par Codex.

## Contrat et garanties du service

`cancel_booking(actor, booking_id, *, clock=None) -> CancellationResult`.
Résultat immuable : booking_id, owner_id, workstation_id, starts_at, ends_at,
created_at et cancelled_at (non nul). Tous les instants retournés sont en UTC.
L'acteur est construit par un adaptateur authentifié de confiance, jamais depuis
un identifiant de propriétaire arbitraire fourni par le client.

Le service ouvre une transaction via la couche de données, verrouille et relit
l'utilisateur actif, consulte un simple indice de poste, verrouille le poste
puis la réservation. L'indice ne valide aucune propriété ni aucun état. Le
service relit ces derniers sous verrou avant de retourner un état ou d'écrire.
Un changement de poste entre indice et verrou provoque un refus sans prendre
un nouveau verrou dans un ordre différent. Une disparition est également refusée.

Pour une première annulation seulement, l'horloge Django ou la fonction injectée
est appelée après les trois verrous. Un instant conscient du fuseau est requis,
normalisé UTC puis comparé strictement au début. Le poste n'a pas besoin d'être
en service. Seul cancelled_at est mis à jour ; la ligne reste dans l'historique.
Une répétition autorisée ne lit pas l'horloge, n'écrit rien et retourne le même
état, même après le début. Aucun statut HTTP n'est attaché à ce contrat.

Erreurs réutilisées : AuthenticationRequired et InvalidBookingInput. Nouveaux
refus héritant de BookingError : BookingNotFound, NotBookingOwner,
CancellationTooLate et BookingChanged (indice de poste périmé). Les erreurs
d'infrastructure inattendues se propagent après rollback, sans devenir un refus
métier fabriqué. Aucune règle de création n'a été contournée ou changée.

Chemin : service → primitives de verrouillage existantes de données → lecture
et verrou de réservation → contrôle métier → UPDATE ORM limité à cancelled_at.
Aucune requête ORM dans le service. Les primitives utilisateur/poste restent
dans booking_creation.py et sont réutilisées ; aucune synchronisation de
production ajoutée uniquement pour les tests.

## Commandes et preuves ciblées

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_booking_cancellation.py tests/test_cancellation_concurrency.py tests/test_booking_concurrency.py --ds=tests.settings_postgres --reuse-db -v -s
.\.venv\Scripts\python.exe tools/check_coverage.py --postgresql
```

Rouge avant code : le premier refus AC-25 échoue avec ModuleNotFoundError, le
service n'existant pas encore. Première série directe : 19 réussites en 2,34 s.
Série étendue : 35 réussites en 8,69 s, dont 27 tests directs, cinq scénarios
concurrents 2D et les trois régressions AC-22/23/24 de 2C. Les assertions
vérifient aussi la conservation de l'historique, l'absence de mutation en cas de
refus, les changements après indice non fiable, le rollback d'une erreur
d'écriture simulée et l'horloge relue après les trois verrous. Deux assertions
supplémentaires de disponibilité après annulation, poste en/hors service, sont
également incluses dans la régression complète suivante.

## Ordres concurrents réellement observés

Le protocole de 2C est extrait dans tests/concurrency_helpers.py et réutilisé
par les deux jalons : données initiales en autocommit sur test_lab_booking_1a,
port 5433, deux connexions de travailleurs et un observateur, trois PID
distincts. Le premier appel conserve un vrai verrou ; pg_blocking_pids et
pg_stat_activity (Lock et SELECT FOR UPDATE) doivent montrer l'attente du second
avant libération. Même bornes : observation 5 s, verrou SQL 10 s, instruction
12 s, Events/futures 15 s ; exceptions récupérées et connexions fermées dans
finally. Aucun rendez-vous n'exige de traverser un verrou détenu par le pair.

| Ordre forcé | PIDs des demandes | Résultats et état final |
| --- | --- | --- |
| Deux annulations, attente utilisateur | 11524 / 14328 | Deux résultats égaux, un seul UPDATE, une ligne annulée à 05:00 UTC |
| Annulation puis création, quota | 37856 / 23300 | Deux succès ; 4 lignes dont 3 non annulées |
| Création puis annulation, quota | 25824 / 38412 | QuotaExceeded puis annulation ; 3 lignes dont 2 non annulées |
| Annulation puis création, même poste/créneau | 39832 / 31272 | Deux succès ; 2 lignes dont 1 non annulée |
| Création puis annulation, même poste/créneau | 30316 / 6160 | WorkstationConflict puis annulation ; 1 ligne annulée |

Horloge contrôlée : 2030-01-07 05:00 UTC ; réservation annulée 07:00–08:00 UTC.
La seconde annulation propose 05:01 mais ne remplace jamais le timestamp 05:00.
Pour le quota, deux autres réservations sont à 09:00 et 11:00 UTC et la nouvelle
demande à 08:00 UTC sur un autre poste : aucun chevauchement n'explique le refus.
Une création refusée avant la libération ne fait l'objet d'aucune relance
automatique. Dans le scénario poste, le créateur est un autre étudiant.

Journal local ignoré : `.local/cancellation-2d-tests.txt`. Ces observations
n'établissent pas une garantie universelle de concurrence. Aucun parcours HTTP,
navigateur, test mobile ou CI distante n'est déclaré validé.

Revue indépendante par l'agent personnalisé reviewer, en lecture seule : aucun
constat bloquant ou important. Vérifiés notamment l'ordre de verrouillage,
l'indice non autoritaire, les contrôles avant idempotence, le rollback et les
cinq scénarios concurrents. Aucun correctif demandé ni constat écarté. Cette
revue ne constitue pas une preuve de tous les entrelacements possibles.

## Régression finale et couverture PostgreSQL

Le lanceur existant `tools/check_coverage.py --postgresql` réussit sans adaptation :

- 266 tests pytest réussis, un désélectionné, aucun ignoré, en 243,03 s ;
- 9 tests TP1 réussis en 11,495 s ; les trois scénarios 2C restent réussis ;
- services : 220/220 lignes et 74/74 branches (100 % chacune) ;
- nouveau service d'annulation : 52/52 lignes et 18/18 branches ;
- nouvel accès aux données : 28/28 lignes et 2/2 branches ;
- global Python, TP1 inclus : 1089/1166 lignes (93,40 %) ;
- branches globales : 266/296 (89,86 %) ;
- inventaire : 47 fichiers de production, aucun absent.

Seuils inchangés : services 100 % lignes et branches, global au moins 80 % lignes.
Exclusions inchangées : tests, dépendances et répertoires générés/locaux. Réglages,
outils, migrations et serveur TP1 restent inclus. La seule désélection est
`test_guard_refuses_unmarked_or_wrong_database`, dont l'assertion d'acceptation
historique est spécifique à SQLite et reste inchangée, exécutée en 1A sur ce
moteur. Aucune mesure SQLite de 2D et aucun autre test pertinent ignoré.

Rapport ignoré : `.local/coverage/b9b69e05ff13468a949d09869f47d11f/coverage.json`.
Sortie brute ignorée : `.local/coverage-2d-final.txt`. Les deux assertions de
disponibilité après annulation sont incluses dans cette mesure réussie.
Contrôle Django avec tests.settings_postgres : aucun problème ; ex2 : 32/32 ;
git diff --check : aucune erreur. Aucune migration appliquée ou ajoutée.

Empreintes SQLite, marqueur, migration initiale et service de création conservées.
Profils privés, journaux bruts, base locale et .venv ignorés et non suivis. Aucun
secret lu pour le compte rendu ni affiché. Contrôle à 380 pixels toujours reporté,
pas de validation navigateur ou CI distante ajoutée. Arrêt avant API HTTP et
regroupement définitif Slice 2 ; aucun push.
