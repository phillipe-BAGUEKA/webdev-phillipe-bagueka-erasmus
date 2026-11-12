# Jalon 4 — parcours étudiant, Slice 2

État initial propre : 514b8ad618756c54d97eb31ec52d8cea865bd22c. Plan annoncé
avant construction : trois espaces sur /labs (catalogue, disponibilités, historique),
HTML/CSS et modules fetch, confirmation explicite, annulation et états accessibles.
API/services réutilisés, aucune règle métier déplacée dans le navigateur.

## Livré et regroupement Slice 2

Sur instruction utilisateur de finaliser le regroupement, le périmètre de
livraison Slice 2 rassemble AC-11 et AC-13 à AC-28 : disponibilités, création,
conflits/quota, concurrence, annulation et historique. AC-40 à AC-45 concernent
transversalement la présentation et l'accessibilité ; AC-46/49 les sessions.
Ce regroupement consigné par Codex ne vaut pas validation de chaque critère : preuves de services,
HTTP, DOM simulé et navigateur restent distinctes. Pas de nouveaux identifiants.

Sur /labs, choisir un laboratoire, une date puis « Afficher les créneaux ».
Les données affichées sont celles des API, en Europe/Sofia. Un clic sélectionne
un poste/créneau ; seul « Confirmer la réservation » déclenche le POST. Succès
201 : message visible, historique et disponibilités relus, sans rechargement.
L'historique affiche les quatre états et l'état actuel du poste ; le bouton
d'annulation est proposé pour une réservation à venir non annulée. Cette aide
d'affichage n'autorise rien : le serveur revérifie toutes les règles.

Mutations bloquées pendant une demande. Une interruption réseau ou réponse de
mutation illisible indique un résultat incertain, ne renvoie jamais le POST et
invite à consulter l'état actuel. Les refus métier sont affichés comme texte.
401 propose un lien de reconnexion, 403 demande une action explicite ; aucun
renvoi ou boucle de redirection automatique. Les lectures proposent le réessai.

Pas de Google, IA, MCP, espace du personnel, migration, nouvelle dépendance,
modification de CI, transfert SQLite ou création implicite de démonstration.
La palette et les espacements existants sont réutilisés. Présentation adaptable,
mais 380 pixels reste reporté jusqu'à une observation réelle.

## Vérifications et limites

```powershell
node --test tests/labs_ui.test.mjs tests/booking_ui.test.mjs
.\.venv\Scripts\python.exe -m pytest tests/test_booking_page.py tests/test_access.py --ds=tests.settings_postgres --reuse-db -v
.\.venv\Scripts\python.exe tools/check_coverage.py --postgresql
```

Les tests Node utilisent un DOM/réseau simulé, sans fournisseur. Ils ne prouvent
ni rendu, ni navigation clavier réelle, ni lecture par un lecteur d'écran.
Les tests Django vérifient le vrai HTML protégé/CSRF, le cache et les réponses
JavaScript des deux modules (principal et import). Les témoignages TP2 ne sont
pas attribués au nouveau parcours sans retour utilisateur.

Edge est accessible localement. Après autorisation supplémentaire explicite,
Codex a créé uniquement dans lab_booking_1a sur 5433 le laboratoire DEMO UI,
ses deux postes et student-ui@demo.example (étudiant actif, sans privilèges,
initialement sans mot de passe utilisable). Aucun compte/rôle/mot de passe
existant n'a été modifié. La saisie masquée du mot de passe et la connexion
Edge ont été effectuées par l'utilisateur selon sa confirmation. Les comptes
SQLite n'ont pas été transférés. Observations de Codex détaillées ci-dessous.

## Procédure de préparation relançable — exécutée une fois sur autorisation

À n'effectuer qu'après autorisation explicite de création des données, sur la
base de développement dédiée. Ouvrir le shell suivant, jamais le seed SQLite :

```powershell
.\.venv\Scripts\python.exe manage.py shell --settings=src.config.postgres
```

Puis exécuter ce bloc Python dans le shell (ou via exec d'un bloc multi-ligne) :

```python
from django.db import connection, transaction
from src.data.models import Laboratory, User, Workstation

assert connection.vendor == "postgresql"
with connection.cursor() as cursor:
    cursor.execute("SELECT current_database(), inet_server_port(), current_user")
    assert cursor.fetchone() == ("lab_booking_1a", 5433, "lab_booking_1a_dev")
with transaction.atomic():
    user = User.objects.only("pk", "role", "is_active", "is_staff", "is_superuser").filter(email__iexact="student-ui@demo.example").first()
    if user is not None:
        assert user.role == "student" and user.is_active
        assert not user.is_staff and not user.is_superuser
    else:
        user = User.objects.create_user("student-ui@demo.example")
        print("Compte neuf sans mot de passe utilisable : définir son mot de passe localement.")
    lab, _ = Laboratory.objects.get_or_create(name="DEMO UI - Laboratory")
    for name in ("DEMO UI - Poste A", "DEMO UI - Poste B"):
        station, _ = Workstation.objects.get_or_create(laboratory=lab, name=name)
        assert station.is_operational
```

Relançable : aucun compte/laboratoire/poste correspondant dupliqué, aucune
modification d'un compte ou poste existant ; une incompatibilité annule la
transaction. Aucun hash, session ou mot de passe SQLite transféré. Ne définir
un mot de passe que pour le compte **neuf** signalé, dans le terminal local :

```powershell
.\.venv\Scripts\python.exe manage.py changepassword student-ui@demo.example --settings=src.config.postgres
```

Saisie masquée, aucune valeur dans les arguments ou journaux. Ne pas répéter
cette commande pour un compte existant. Aucune de ces étapes n'a été exécutée
par Codex pour le mot de passe : seule la préparation des données a été exécutée
sur autorisation. La commande de mot de passe reste une intervention utilisateur.

## Parcours navigateur reproductible

Arrêter son serveur avec Ctrl+C puis relancer pour charger le nouveau code :

```powershell
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --settings=src.config.postgres --insecure --noreload
```

1. Ouvrir http://127.0.0.1:8000/login, se connecter au compte PostgreSQL préparé.
2. Sur /labs, choisir le laboratoire puis une date ouvrée future ; constater
   les horaires Europe/Sofia. Tester aussi le vide avec un week-end.
3. Choisir un poste : aucune réservation avant confirmation. Confirmer une fois,
   vérifier le succès et la présence dans Mes réservations sans recharger.
4. Annuler : constater le statut Annulée et la disponibilité libérée, sans recharger.
5. Refaire le parcours au clavier et contrôler focus/messages/états d'erreur.
   Le contrôle à 380 pixels reste séparé et reporté.

## Pour ta note d'architecture personnelle

Chemins : templates/labs.html → static/js/labs.mjs et booking.mjs → routes/bookings.py
et booking_http.py → services/booking_reads.py, booking_creation.py,
booking_cancellation.py → data/booking_reads.py, booking_creation.py,
booking_cancellation.py → PostgreSQL. Préfixer par src/ dans le dépôt.

Questions utiles, à traiter à la fin du projet comme convenu : pourquoi le choix
d'un créneau ne suffit-il pas à l'autoriser ? Pourquoi une erreur réseau après
POST ne justifie-t-elle pas une relance ? Comment l'annulation libère-t-elle le
quota et le poste sans supprimer l'historique ? La note n'est pas rédigée ici.
Code, tests et documentation assistés par Codex ; aucune validation personnelle
de compréhension ou approbation professorale n'est présumée.

## Mesures et revue réellement effectuées

- Régression PostgreSQL via le lanceur inchangé : 319 pytest réussis, un test
  désélectionné, aucun ignoré, en 97,49 s ; 9 tests TP1 réussis en 6,488 s.
- Services : 220/220 lignes et 74/74 branches (100 % chacune). Global Python,
  TP1 inclus : 1206/1283 lignes (94,00 %), 290/320 branches (90,625 %).
- Inventaire inchangé : 49 fichiers de production Python, aucun absent. Réglages,
  migrations et outils inclus ; exclusions inchangées : tests, dépendances,
  fichiers générés/locaux. Seuils inchangés, aucune mesure SQLite de ce jalon.
- Seule désélection : test_guard_refuses_unmarked_or_wrong_database, assertion
  d'acceptation propre à la cible SQLite historique, inchangée et exécutée en 1A.
- 22 tests Node réussis ; modules chargés labs.mjs et booking.mjs : 98,18 % des
  lignes, nouveau contrôleur 100 %, catalogue 93,02 %. Ce n'est pas la couverture
  de tout le frontend ni du navigateur ; le seuil existant de 80 % est conservé.
- La première mesure JS a échoué (57,34 %) : les tests chargeaient le même fichier
  via deux URL, avec/sans query de version, et Node reportait l'instance inutilisée.
  Les tests importent maintenant exactement l'URL versionnée du navigateur. Aucun
  fichier de production exclu, aucun seuil abaissé pour réussir.
- Premier lancement Node bloqué par spawn EPERM en sandbox, relance autorisée.
- Revue indépendante en lecture seule : aucun problème bloquant ou important.
  Amélioration retenue : après 401, bloquer aussi le bouton de relecture d'historique.
  Le regroupement est finalisé comme périmètre de livraison sur instruction de
  l'utilisateur, sans prétendre une validation de chaque critère ni sa rédaction.

Rapports locaux ignorés : .local/coverage-ui-4.txt,
.local/coverage/ae6753610bc846d49bd53f3789b65ff4/coverage.json et
.local/js-ui-coverage.txt. Les résultats navigateur ci-dessous sont indépendants
de ces chiffres ; aucune réussite visuelle n'est déduite des tests.

Vérifications finales avant la connexion : syntaxe des deux modules JavaScript,
contrôle Django et git diff --check réussis ; ex2 32/32. Dernière répétition
ciblée du HTML protégé/MIME : 11 réussites en 7,33 s. SQLite, marqueur et migration
initiale inchangés ; aucune modification des services, routes/API Python,
migrations, dépendances, CI, exclusions ou seuils. Profils/bases/.venv non suivis.
Le commit local clôt uniquement ce jalon ; aucun push effectué.

## Parcours réellement observé dans Edge — 12 novembre 2026

L'utilisateur a confirmé sa connexion avec student-ui@demo.example, le
laboratoire visible et l'historique vide. Codex a ensuite observé et manipulé
la fenêtre Edge de cette même session sur http://127.0.0.1:8000/labs :

1. DEMO UI - Laboratory et historique vide visibles. Sélection de la date
   du vendredi 13 novembre 2026 dans le calendrier : 20 créneaux proposés,
   dix par poste A/B, affichés en Europe/Sofia.
2. Sélection du poste A, 08:00–09:00 : confirmation explicite affichée et
   historique encore vide avant validation.
3. Confirmation unique : message de succès, une entrée « À venir » pour ce
   poste/créneau et 18 créneaux disponibles, sans rechargement manuel.
   Interprétation : le chevauchement personnel rend indisponible cette heure
   sur les deux postes ; le résultat visible est cohérent avec cette règle.
4. Annulation unique : message « Réservation annulée ; elle reste dans ton
   historique. », toujours une entrée, désormais « Annulée · Poste en service »,
   et retour à 20 créneaux. La réservation de démonstration reste annulée ;
   aucune suppression ou restauration de données n'a été effectuée.

Accès direct aux onglets indisponible (hôte navigateur inaccessible) : recours
aux observations natives de la fenêtre Edge, après mise au premier plan par
l'utilisateur. La saisie automatisée du champ date n'a pas fonctionné ; le
calendrier natif a permis la sélection. Aucun défaut applicatif n'en est déduit.
Les états ont été lus dans l'arbre accessible et le rendu observé pendant le
parcours. Aucun statut réseau ou Console n'a été relevé pour ces mutations.
Les captures affichées par l'outil ne sont pas archivées dans le dépôt.

À la fin du premier essai restaient non effectués dans ce navigateur : week-end/vide, erreurs/refus,
incertitude réseau, parcours complet au clavier, contraste et contrôles de
largeur. Le contrôle à 380 pixels reste explicitement reporté. Les observations
clavier TP2 ne sont pas étendues au nouveau parcours. Aucun coût ou nombre de
tokens Codex disponible ; aucun appel fournisseur.

L'utilisateur autorise désormais les commits et push normaux ainsi que
l'alignement CI PostgreSQL pour la finalisation TP3, après vérifications. Cette
autorisation ne transforme ni le présent jalon ni une future CI verte en clôture
complète : note d'architecture personnelle, preuves UI restantes et exigences à
confirmer avec le professeur restent distinctes. Pas de publication prématurée.

Complément de finalisation du 12 novembre : parcours réservation/annulation au
clavier, erreur réseau/réessai et mesure de contraste observés et détaillés dans
SLICE2_FINALIZATION.md. Une seconde réservation de démonstration y a été créée
puis annulée, sans supprimer la première. Les autres limites y restent explicites.
