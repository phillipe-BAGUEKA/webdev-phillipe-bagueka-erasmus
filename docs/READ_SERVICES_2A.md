# Jalon 2A — services de lecture disponibles

## Perimetre consigne avant implementation

Autorisation : consultations seulement, sans mutation, service de creation ou
annulation, HTTP, UI, MCP, IA, migration, dependance ou CI. Etat initial Git propre.

Preuves partielles visees : AC-13 (jours/heures, debut futur), AC-14 (conversion
Europe/Sofia vers UTC hiver/ete) et AC-28 (historique propre avec etat du poste).
La disponibilite tient aussi compte d'AC-11, AC-17/18/19, AC-20/21 et AC-25 : etat
du poste, occupation, annulation, conflit personnel et quota futur global. Une
lecture ne garantit pas la creation : ces regles devront etre reverifiees dans
la future transaction de creation. Aucun nouvel AC, aucune renumerotation.

Les seuls etudiants peuvent recevoir des propositions reservables ; un acteur
personnel authentifie peut consulter son historique, mais ne recoit pas de
proposition reservable. Cela n'introduit pas un droit de gestion du personnel.

Plan : tests directs PostgreSQL et horloge explicite d'abord, constat rouge,
puis acces aux donnees et deux services sans ORM ; regressions et couverture
PostgreSQL ; revue independante ; commit local apres controles. Le regroupement
definitif Slice 2 et la note d'architecture personnelle restent ouverts.

## Contrats livres et testes directement

- list_available_slots(actor, laboratory_id, day, *, now=None) retourne une
  liste de AvailableSlot immuables : identifiant/nom du poste, starts_at/ends_at
  conscients du fuseau et normalises en UTC. Ordre : debut croissant, puis ID poste.
- list_personal_bookings(actor, *, now=None) retourne une liste de PersonalBooking
  immuables : identifiants, noms du poste/laboratoire, instants, annulation, etat
  actuel du poste et statut cancelled/future/in_progress/past. Ordre : debut
  decroissant, puis ID reservation decroissant (y compris les egalites de debut).
  Aucun owner_id client n'est accepte ; seul actor.user_id filtre les lignes.
- Les acteurs sont ceux du mecanisme authentifie existant, construits par les
  adaptateurs de confiance. Aucune des fonctions n'authentifie un objet venant
  directement d'un client ni ne depend d'une requete HTTP/MCP.
- AuthenticationRequired reste l'erreur d'acces existante ; InvalidReadInput
  refuse date/identifiant/horloge invalides ; LaboratoryNotFound refuse un
  laboratoire inconnu. Une liste vide n'est pas une erreur.
- now est une horloge injectable. En production, omission utilise l'horloge
  Django ; dans les tests, les instants sont tous controles.

## Repartition et limites

src/services/booking_reads.py applique les regles ; src/data/booking_reads.py
execute et materialise les projections ORM, y compris les comptages et jointures.
Aucun modele, QuerySet, objet HTTP ou message MCP ne traverse le contrat public.
Le quota compte toutes les reservations non annulees dont debut > maintenant,
tous laboratoires confondus, y compris les postes devenus hors service. Les
conflits personnels consultent aussi les autres laboratoires. Les plages sont
semi-ouvertes et les annulations ne bloquent aucune disponibilite.

Les lectures peuvent observer des changements concurrents entre leurs requetes.
Elles ne verrouillent rien et ne garantissent pas une future creation. Ce jalon
ne prouve ni mutation de reservation, ni protection concurrente du quota, ni
reponse HTTP, ni affichage navigateur. Aucune migration, dependance, CI ou donnee
de developpement n'est modifiee. SQLite et 5432 restent hors des operations.

## Preuves et limites au 11 novembre 2026

- Tests écrits avant les services : premier test AC-13/14 rouge avec
  ModuleNotFoundError, puis 13 tests initiaux réussis après implémentation.
- Tests complémentaires : validation des entrées, personnel, laboratoire vide
  ou absent, horloge par défaut contrôlée et refus d'un owner_id client.
- Première régression : 175 réussites, un échec de jeu de données, un test SQLite
  désélectionné. Le test d'horloge avait préparé une réservation étrangère qui
  occupait aussi le jour testé : 17 candidats au lieu des 18 attendus. La ligne
  étrangère est maintenant au lendemain, toujours détectable par le test de fuite.
  L'assertion métier et le service n'ont pas été affaiblis pour masquer cet échec.
- Tests directs finaux : 21/21 réussis sur PostgreSQL réel, 2,39 s.
- Couverture PostgreSQL avec le lanceur existant : 176 tests pytest réussis,
  un test SQLite désélectionné, aucun test ignoré (221,64 s), puis neuf tests TP1
  réussis (24,045 s). Le test désélectionné reste exclusivement
  test_guard_refuses_unmarked_or_wrong_database, déjà documenté au jalon 1B.
- Services : 103/103 lignes et 34/34 branches ; nouveau service : 78/78 lignes
  et 30/30 branches. Global Python : 901/978 lignes (92,13 %), branches
  218/248 (87,90 %), TP1 inclus. L'inventaire conserve 43 fichiers de production,
  les exclusions et les seuils ; aucun réglage de couverture n'est modifié.
- Rapport local ignoré :
  .local/coverage/056ed6d01e43403f9d62846fec47dcaf/coverage.json.
- Contrôles Django et dérive des migrations réussis. Aucune nouvelle migration.
- Revue indépendante : aucun constat bloquant/important ; documentation et
  traçabilité complétées. Tuples précisés, projections ORM matérialisées conservées.
- AC-13/14/28 et les règles de filtrage sont prouvés uniquement au niveau lecture.
  Aucun résultat HTTP/UI, concurrence, création ou annulation n'est déduit.
- La CI historique reste inchangée et non validée pour PostgreSQL. Le contrôle
  à 380 pixels reste reporté. Slice 2 et la note personnelle restent ouverts.
