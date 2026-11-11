# Jalon 2C — créations concurrentes PostgreSQL

État initial propre : c2f2673164622dc8e1d01fea7e80841d9c07c4c3.
Périmètre autorisé : tests directs des trois scénarios AC-22/23/24 avec des
connexions distinctes et le service public de 2B. Aucun parcours HTTP ou écran.
Instrumentation uniquement dans les tests, sans mécanisme de production ajouté.

## Protocole prévu et bornes

Les fixtures sont créées en autocommit avec pytest django_db(transaction=True),
sans transaction englobante cachant les lignes aux autres connexions. Chaque
thread ouvre sa propre connexion Django et confirme le nom de la base de test
dédiée et le port 5433 avant toute mutation. Les deux threads vérifient les
données initiales visibles et fournissent leurs pg_backend_pid ; l'observateur
principal possède un troisième PID distinct.

Le premier appel du service conserve un véritable verrou, puis un Event le
maintient en transaction. Le second appel commence et tente le même verrou.
L'observateur exige que pg_blocking_pids(second) contienne le premier PID et que
pg_stat_activity indique Lock sur le SELECT FOR UPDATE de la table attendue.
Ce n'est qu'après cette preuve que l'Event libère le premier appel. Aucun
rendez-vous n'oblige le second à franchir le verrou déjà détenu par le premier.

AC-22 attend sur le poste ; AC-23 et AC-24 attendent sur l'utilisateur. Les deux
derniers scénarios vérifient ainsi la relecture après sérialisation par compte.
Les attentes Events/futures sont limitées à 15 s, l'observation à 5 s, les
attentes SQL à 10 s (verrou) / 12 s (instruction). Le sondage de l'état PostgreSQL
utilise Event.wait(0.01), sans déduire une concurrence du temps écoulé. Les
exceptions des futures sont récupérées, les connexions fermées dans finally et
le verrou toujours libéré, y compris après échec d'une assertion.

## Scénarios à exécuter

- AC-22 : même poste et même créneau, deux étudiants ; création puis
  WorkstationConflict ; une ligne finale.
- AC-23 : même étudiant, deux postes et même créneau ; création puis
  PersonalConflict ; une ligne finale.
- AC-24 : deux réservations initiales, puis deux créneaux consécutifs distincts
  sur deux postes. Aucun des quatre intervalles ne chevauche un autre ; création
  puis QuotaExceeded ; trois lignes finales et deux lignes initiales intactes.

Horloge commune contrôlée : 2030-01-07 05:00 UTC. Créneaux des demandes :
07:00 UTC et, pour la seconde demande AC-24, 08:00 UTC. Les deux lignes initiales
du quota sont à 10:00 et 12:00 UTC. Toutes sont dans les horaires Europe/Sofia.
Les tests ne font jamais appel à l'heure réelle pour décider la réservation.

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_booking_concurrency.py --ds=tests.settings_postgres --reuse-db -v -s
.\.venv\Scripts\python.exe tools/check_coverage.py --postgresql
```

Regroupement définitif Slice 2 et note
d'architecture personnelle toujours ouverts. Rédaction et tests assistés par
Codex, sans attribution à une rédaction personnelle de l'étudiant.

## Premières observations et preuve de détection

Premier lancement : 3 tests réussis en 4,18 s. AC-22 : PID 16696/25064,
création/WorkstationConflict, une réservation. AC-23 : PID 33572/6552,
création/PersonalConflict, une réservation. AC-24 : PID 33068/25016,
création/QuotaExceeded, trois réservations. Dans chaque cas, l'attente de verrou
a été observée avant de libérer le premier appel, puis les deux futures terminées.

Mutation temporaire autorisée : le seuil de la seule condition de quota du
service a été remplacé de 3 à 3000, sans toucher aux contraintes. Le test AC-24
a alors observé deux créations, quatre lignes finales et un échec `assert 4 == 3`.
PIDs distincts 39972/30392, attente PostgreSQL toujours démontrée ; il ne s'agit
donc ni d'une erreur SQL ni d'un test séquentiel déguisé. Pytest : un échec et
deux désélections de ciblage, en 2,36 s. Journal local ignoré :
`.local/quota-mutation-2c.txt`.

Le code original a été rétabli dans finally et comparé octet par octet ; SHA-256
du service restauré :
`1df4c49d5b852b5e7d2c3d4184008ac582aa49ba3a4d5d834a6b65a2ffaf676b`.
Aucune modification de production, migration ou règle n'est conservée. Les
contraintes PostgreSQL ne suffisent donc pas à faire réussir le scénario quota.

## Vérification après restauration exacte

Les trois scénarios ont de nouveau réussi en 3,77 s sur le code original :

| Critère | PIDs des demandes | Attente observée | Résultats | Réservations finales |
| --- | --- | --- | --- | --- |
| AC-22 | 35268 / 42832 | Poste détenu par la première demande | CreatedBooking / WorkstationConflict | 1 |
| AC-23 | 37340 / 33196 | Utilisateur détenu par la première demande | CreatedBooking / PersonalConflict | 1 |
| AC-24 | 10104 / 35704 | Utilisateur détenu par la première demande | CreatedBooking / QuotaExceeded | 3, dont les 2 initiales intactes |

Les PIDs sont les observations de cette exécution locale, pas des identifiants
à réutiliser. Chaque succès a été comparé à la ligne enregistrée (propriétaire,
poste, dates, absence d'annulation) ; le refus n'ajoute aucune autre ligne.
Journal local ignoré : `.local/concurrency-2c-final.txt`. PowerShell a enveloppé
le message stderr habituel « Using existing test database » en NativeCommandError
dans cette redirection ; le code de sortie pytest est bien 0 et les trois cas
sont PASSED. Aucune exception de thread, erreur SQL ou expiration n'est acceptée
comme refus métier.

Les contrôles documentaires ex2 passent 32/32 ; git diff --check est sans erreur.
SQLite, son marqueur, la migration initiale et le service restauré ont les mêmes
empreintes qu'avant le jalon. Aucun changement de production, migration,
dépendance, configuration de couverture ou CI n'est conservé.

Revue indépendante en lecture seule par l'agent personnalisé reviewer : aucun
constat bloquant ou important, aucun correctif demandé ni constat écarté. La
preuve d'attente PostgreSQL, l'isolation des données, les résultats et les bornes
ont été examinés. Cette revue ne remplace pas une preuve de tous les
entrelacements possibles. Arrêt avant 2D, aucun push.

## Régression et couverture finales PostgreSQL

Le lanceur inchangé `tools/check_coverage.py --postgresql` a terminé avec succès :

- 234 tests pytest réussis, un désélectionné, aucun ignoré, en 220,34 s ;
- 9 tests unittest TP1 réussis en 13,697 s ;
- services : 168/168 lignes et 56/56 branches, soit 100 % chacune ;
- global Python, TP1 inclus : 1009/1086 lignes (92,91 %) ;
- branches globales : 246/276 (89,13 %) ;
- inventaire inchangé de 45 fichiers de production, aucun absent.

La seule désélection est le test historique
`test_guard_refuses_unmarked_or_wrong_database`, dont l'assertion d'acceptation
spécifique à SQLite reste inchangée et a été exécutée sur SQLite en 1A. Aucun
autre test pertinent désélectionné pour réussir. La mesure de 2C est PostgreSQL,
pas SQLite. Les seuils restent 100 % lignes/branches des services et au moins
80 % des lignes globales. Exclusions inchangées : tests, dépendances et dossiers
générés/locaux ; réglages, migrations, outils et serveur TP1 sont inclus.

Rapport local ignoré :
`.local/coverage/c363ddc75c094bb5bf5b09acafba30ab/coverage.json`.
Journal brut : `.local/coverage-2c-final.txt`. Aucun résultat CI distant déclaré.
Le contrôle à 380 pixels reste reporté. Aucune donnée de développement ni SQLite
n'a été modifiée ; aucun fichier sensible ou temporaire n'est destiné au commit.
