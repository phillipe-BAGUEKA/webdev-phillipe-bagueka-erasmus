# Espace du personnel — Réservations

## Ouvrir l'écran

1. Démarrer l'application sur le PostgreSQL local dédié, depuis la racine.

   ```powershell
   .\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --settings=src.config.postgres --insecure --noreload
   ```

2. Ouvrir <http://127.0.0.1:8000/staff/bookings> et se connecter avec un compte
   local actif de rôle `personnel`. Depuis `/labs`, le lien **Espace du personnel**
   ouvre le même écran. Une session étudiante doit être fermée avant de changer de compte.

Pour préparer un nouveau compte de démonstration si nécessaire, ouvrir le shell
Django sur la base de développement dédiée.

```powershell
.\.venv\Scripts\python.exe manage.py shell --settings=src.config.postgres
```

```python
from django.contrib.auth import get_user_model
get_user_model().objects.create_user("personnel-demo@example.test", role="personnel")
exit()
```

Après la création, définir le mot de passe du nouveau compte à l'invite masquée.
Si cette adresse est déjà utilisée, conserver le compte et ses identifiants actuels.

```powershell
.\.venv\Scripts\python.exe manage.py changepassword personnel-demo@example.test --settings=src.config.postgres
```

L'écran affiche les réservations de la base de développement. La liste vide
est prévue si elle n'en contient aucune. Les essais AC-9 ont utilisé uniquement
des comptes synthétiques isolés.

## Contrat et preuve automatisée

`GET /api/staff/bookings` exige un acteur Django actif de rôle `personnel`. La
page redirige vers `/login?next=/staff/bookings` sans session active. L'API renvoie
alors 401 JSON. Un étudiant reçoit 403 sur les deux routes, même avec `is_staff`.
La route historique `GET /api/bookings` conserve son périmètre personnel.

L'API reçoit ses lignes du service `list_staff_bookings`. La couche de données
projette les noms du laboratoire et du poste, les instants, la date d'annulation
utilisée pour calculer l'état et l'identifiant numérique du propriétaire. Le tri
est décroissant par début, puis par identifiant de réservation. La réponse exprime
les instants en UTC, et l'écran les affiche en `Europe/Sofia`. L'adresse e-mail
des propriétaires reste hors de la réponse. L'API accepte uniquement GET.

Sur PostgreSQL de test, `tests/test_staff_bookings.py` prépare un membre du
personnel sans drapeau Django et deux étudiants ayant chacun une réservation.
Les assertions comparent les lignes avant/après, l'ordre des deux réservations
du personnel, la visibilité individuelle des étudiants, leurs refus d'accès,
l'absence de session et la désactivation du compte. Les tests vérifient aussi
l'état vide, le retour de connexion vers l'écran et le refus d'une écriture
sur l'API, avec et sans CSRF. Les tests DOM couvrent chargement, vide, succès,
erreur et réessai, sessions, ordre, horaires d'été/d'hiver et insertion sûre du texte.

## Observations Edge

Codex a suivi le lien **Espace du personnel** depuis `/labs`, sur le banc local
isolé `127.0.0.1:8012`. Les vraies routes, la session Django et les fichiers UI
ont utilisé deux réservations synthétiques en SQLite en mémoire pour l'essai
visuel. Les contraintes PostgreSQL sont vérifiées dans la suite distincte.
Le banc a été arrêté après le parcours et ses données ont été relâchées. Les
captures et mesures de Codex sont restées dans la conversation.

| Viewport CSS | Page `clientWidth/scrollWidth` | Liste `clientWidth/scrollWidth` | Observation |
| --- | --- | --- | --- |
| 380 × 430 | 380/380 | 298/298 | Horaires sur deux lignes, focus visible après Tab, deuxième réservation lisible après défilement vertical au clavier. |
| 768 × 430 | 768/768 | 494/494 | Horaires sur une ligne et focus visible sur la région. |
| 1 280 × 430 | 1280/1280 | 494/494 | Deux créneaux lisibles dans la région et focus visible. |

Les créneaux d'hiver `08:00–09:00` et d'été `16:00–17:00` ont été affichés avec
les postes, les états « À venir » et « Annulée » et les comptes nº 2 et nº 3.
À 380 px, un 503 synthétique a affiché un message lisible. Tab puis Entrée sur
**Réessayer** ont déclenché le chargement, puis le GET 200 et le retour des deux
lignes. Le focus est revenu sur le message de succès.

Le scénario réalisé vérifie AC-9. AC-5 reste partiel avec le seul refus local
direct, AC-40 avec le lien vers l'espace distinct, et AC-42 avec la consultation
sur les trois largeurs. La session Google, la gestion du catalogue, les autres
écrans et les mesures de déplacement pendant le chargement de ce nouvel écran
restent hors de ces preuves.

## Vérifications locales

La commande `tools/check_coverage.py --postgresql` a exécuté 552 cas PostgreSQL
et 9 tests Python TP1. Le garde SQLite désélectionné dans cette commande a réussi
séparément. Le résultat global est de 1 826/2 074 lignes (88,04 %) et 447/512
branches (87,30 %). Ce dénominateur inclut les deux bancs Python ignorés dans
`.local/`, détectés par la configuration existante. Les services atteignent
347/347 lignes et 110/110 branches. Le serveur TP1 est inclus dans la mesure.
Après cette mesure, la revue indépendante a demandé une preuve du tri par date
en plus du départage par identifiant. Le cas ajouté oppose l'ordre des dates à
celui des identifiants. Les 8 cas PostgreSQL AC-9 passent après cet ajout de test.

Les 51 tests Node passent, dont 9 pour ce module. La mesure locale incluant le
nouvel écran couvre 97,76 % des lignes et 95,78 % des branches des modules
JavaScript mesurés avec le seuil existant de 80 % des lignes.

Le contrôle Django, `git diff --check`, MCP TP1 (12/12) et ex2 (32/32) passent. Le vérificateur
ex3 indique 15/18. AC-9 est désormais reconnu dans les tests. Les trois motifs
restants concernent le lancement de `npm` sous Windows (`spawnSync npm ENOENT`),
les critères encore sans titre de test reconnu et la note d'architecture
personnelle. Aucune modification du vérificateur.

## Questions pour relire le code

- Où le rôle `personnel` est-il vérifié avant la lecture des réservations ?
- Comment `GET /api/bookings` conserve-t-il la portée du propriétaire connecté ?
- Où les créneaux transmis en UTC sont-ils affichés en `Europe/Sofia` ?
