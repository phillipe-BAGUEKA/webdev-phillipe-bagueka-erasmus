# Brouillon préparé avec Codex — à réviser par l’étudiant

Ce texte décrit le code actuel. Il n'est ni la note personnelle du Lab 03, ni une validation de compréhension. L'étudiant doit le confronter au code et le reformuler avant toute insertion éventuelle dans `SPEC.md`.

La page `src/templates/labs.html` contient la date, les créneaux, le résumé du choix et le bouton « Confirmer la réservation ». `src/static/js/booking.mjs` garde le créneau choisi dans `selected`. Un clic lance `mutate("create", selected)` : `POST /api/bookings` transporte l'identifiant du poste et les instants de début et de fin. La requête utilise le cookie de session du même site et l'en-tête `X-CSRFToken` tiré de la page rendue par Django.

`src/config/urls.py` mène à `src/routes/bookings.py`. L'authentification Django retrouve l'utilisateur à partir de la session ; `src/routes/session.py` le convertit en acteur. Le middleware CSRF vérifie la requête avant la vue. La route valide la forme JSON, puis `src/services/booking_creation.py` exige un étudiant actif, un créneau canonique futur, un poste en service, aucun chevauchement et un quota disponible. Ces règles ne connaissent pas HTTP.

Le service encadre les opérations avec `creation_transaction()` de `src/data/booking_creation.py`. La couche de données prend les verrous PostgreSQL dans l'ordre utilisateur puis poste, relit les données et insère une ligne `Booking` via l'ORM. Les contraintes de la base restent une protection finale. Après succès, la route renvoie 201 et un JSON ; JavaScript annonce la confirmation puis recharge l'historique et les disponibilités. Si la réponse réseau se perd, il déconseille de renvoyer automatiquement la mutation. `book_slot` dans `mcp-server/project_tools.py` entre dans le même service avec un acteur issu d'une session revérifiée.

Écart concret avec le schéma simplifié « route → service → données » : la transaction entoure plusieurs appels à la couche de données depuis le service, au lieu d'être une seule méthode de dépôt. Les décisions métier restent ainsi dans le service, et les verrous et écritures ORM dans `src/data/booking_creation.py`. Ce choix mérite une revue personnelle, notamment de l'ordre des verrous et du rollback.

Questions pour la révision orale :

1. Pourquoi la session ne remplace-t-elle pas la vérification CSRF ?
2. Pourquoi revérifier les règles après l'affichage d'un créneau libre ?
3. Que change l'ordre de verrouillage utilisateur puis poste ?
4. Que conclure si le navigateur perd la réponse du `POST` ?
