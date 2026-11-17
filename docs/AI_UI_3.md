# IA — sous-étape 3 : interface et sélection manuelle

17 novembre 2026, départ `aeba6daa3e375412767b9904224d13128b5287a1`, arbre propre.
Choix fonctionnels de l'utilisateur ; code, tests et rédaction assistés par Codex.
L'autorisation couvre cette UI, les tests hors réseau et le commit local, sans
push. Aucun fournisseur, clé réelle, installation, migration ou CI modifiés.

## Chemin des données et fichiers

- `src/templates/labs.html` : formulaire facultatif dans les disponibilités,
  avertissement avant envoi, textarea 1 000, statut live hors formulaire busy.
- `src/static/css/app.css` : textarea reprenant les styles et focus existants.
- `src/static/js/booking.mjs` : trim 1–1 000, soumission volontaire unique à
  `POST /api/labs/{id}/suggestion`, session/CSRF existants. Invalidation à chaque
  changement de besoin/contexte ou choix manuel ; une réponse périmée est ignorée.
  Erreurs fixes lisibles, aucun retry. Les noms et horaires sont rendus en texte.
- `src/static/js/labs.mjs` : import booking v2 ; HTML labs v3 évite les anciennes
  entrées de cache. Aucun mécanisme MIME ou serveur modifié.
- Le service valide dix candidats maximum puis relit la disponibilité. L'UI
  sélectionne la proposition sans réserver. Le bouton existant confirme via
  `POST /api/bookings` → `create_booking`, qui revérifie les règles courantes.
- `tests/ai_suggestion_ui.test.mjs` : 19 cas DOM/réseau simulés, dont doublons,
  erreurs, contexte obsolète, sécurité textuelle et absence de retry. Le helper
  `booking_ui_helpers.mjs` est partagé avec les anciens tests, assertions gardées.
- `tests/test_ai_confirmation.py` : cinq parcours HTTP avec CSRF réel, session,
  services et PostgreSQL ; faux client uniquement pour la suggestion. Succès ou
  refus après conflit poste/personnel, quota ou poste hors service, sans mutation.
- `tests/test_access.py`, `test_booking_page.py` : HTML, avertissement et cache.

## Résultats automatisés locaux

Commandes depuis la racine PowerShell :

```powershell
node --test tests/ai_suggestion_ui.test.mjs tests/booking_ui.test.mjs tests/labs_ui.test.mjs tests/test_runner.test.mjs
.\.venv\Scripts\python.exe tools/check_coverage.py --postgresql
node --test --experimental-test-coverage --test-coverage-include='src/**' --test-coverage-exclude='tests/**' --test-coverage-lines=80 tests/labs_ui.test.mjs tests/booking_ui.test.mjs tests/ai_suggestion_ui.test.mjs
```

19 nouveaux tests rouges avant implémentation (gestionnaires absents), puis
42 Node réussis. Ciblage Python confirmation/page/accès : 16 réussis.
Lanceur de couverture inchangé : 545 PostgreSQL réussis, un test désélectionné
spécifique SQLite, puis 9 TP1. Global lignes 1 765/1 865 = 94,64 %, branches
445/488 ; services 322/322 lignes et 108/108 branches = 100 %. Le 93,92 % du
tableau coverage combine lignes et branches, ce n'est pas le pourcentage des
lignes du seuil global. Inventaire et exclusions `.coveragerc` inchangés.
L'avertissement no-data-collected du parent unittest est connu : le rapport
combiné contient bien les lignes des sous-processus TP1.
Rapport local : `.local/coverage/7dc1085f4c9e4ef88620f8d07e612cac/coverage.json`.
JS : 41 tests, 97,71 % lignes / 95,59 % branches sur les seuls modules chargés
labs et booking. Ce n'est pas une couverture visuelle ou de tout le frontend.
La garde `test_guard_refuses_unmarked_or_wrong_database`, spécifique au chemin
de démonstration SQLite, est passée séparément sous tests.settings_sqlite_legacy.
Django check : zéro problème ; MCP : 12/12 ; ex2 : 32/32 ; diff --check : réussi
après correction d'une ligne vide. Revue indépendante : accents de nouveaux
paragraphes corrigés en UTF-8 et ligne vide supprimée ; aucun défaut fonctionnel
bloquant ni constat écarté. Résultats locaux, aucune exécution CI revendiquée.

## Observations Edge réellement effectuées par Codex

L'utilisateur a lancé le serveur normal et confirmé sa connexion. Codex a
observé sur `http://127.0.0.1:8000/labs`, compte de démonstration conservé :
avertissement, besoin/date, chargement puis « La suggestion IA est désactivée
ou non configurée. Choisis manuellement. ». Ensuite 20 créneaux du 18 novembre,
choix du Poste A 08:00–09:00 et panneau de confirmation. Aucun clic de création
sur cette base ; les deux anciennes entrées annulées sont restées visibles.
Ces observations ne sont pas attribuées à l'utilisateur ; aucun statut HTTP
n'est déduit de la seule vue de la page.

Sur `http://127.0.0.1:8011/labs`, bannière **SIMULATION LOCALE**, PostgreSQL de
test et faux client : suggestion Poste A du 18 novembre 08:00–09:00, historique
vide avant clic ; confirmation explicite puis « Réservation confirmée » et
une entrée À venir. Ensuite messages délai dépassé, réponse invalide et quota
simulés ; samedi 21 novembre sans candidat ; session de test révoquée et message
de reconnexion. Le mode du fichier de scénario a été changé entre demandes
volontaires ; la bannière indique le mode au chargement de la page.
Ni le délai réseau réel ni Google n'ont été essayés. Pas de capture archivée.
Les tests DOM couvrent aussi panne réseau et réponse obsolète ; ces deux cas
ne sont pas présentés comme de nouvelles observations Edge.

## Reproduire la simulation isolée uniquement

`tests/browser_ai_demo.py` est un dispositif de test explicite, jamais importé
par le lancement normal et sans option de faux succès dans la configuration
applicative. Il refuse toute identité autre que la base `test_lab_booking_1a`,
rôle `lab_booking_1a_test`, port 5433. Ne pas lancer pytest simultanément.
Il crée ses seules lignes isolées avec compte à mot de passe inutilisable ;
cookies distincts pour préserver les sessions du développement même hôte.
CSRF et services réels restent actifs. Pas de clé ni d'accès fournisseur.

Après les tests, choisir des chemins de cas/arrêt **neufs** sous `.local/` et
un port libre, puis dans un terminal :

```powershell
Set-Content .local/ai-ui-case-new.txt success -Encoding utf8
.\.venv\Scripts\python.exe -m tests.browser_ai_demo --case-file .local/ai-ui-case-new.txt --stop-file .local/ai-ui-stop-new.flag --port 8011
```

Ouvrir `http://127.0.0.1:8011/__test__/enter`. Choisir uniquement le laboratoire
SIMULATION, date préremplie, besoin générique. Les modes sont success, disabled,
timeout, quota, invalid, error, empty et expired. Modifier le fichier puis
recharger pour actualiser la bannière ; empty préremplit un samedi. Revenir à
`/__test__/enter` après une session révoquée. Aucune véritable clé ne doit être
saisie. Pour arrêter depuis un second terminal :

```powershell
New-Item -ItemType File .local/ai-ui-stop-new.flag
```

Attendre « SIMULATION STOPPED; own test rows cleaned. ». Ce message a été
effectivement obtenu après l'essai ; serveur arrêté, seules ses lignes nettoyées.
Pour le serveur normal `--noreload`, Ctrl+C puis relancer la commande PostgreSQL
d'AGENTS.md après tout changement de code ; aucune activation IA nécessaire.

## Limites

AC-29 à AC-36 : preuves service/API/DOM et rendu simulé distingués dans SPEC.
Pas de qualité réelle de recommandation, modèle ou conditions Google validés.
Le texte libre peut contenir des données personnelles malgré l'avertissement.
Aucune réservation avant confirmation, aucune garantie issue d'une ancienne
disponibilité. Délai fournisseur testé auparavant par processus locaux ; pas
de promesse d'affichage navigateur en cinq secondes. 380 pixels, autres contrôles
UI complets, note personnelle et validation finale Gemini restent ouverts.
Lab 03 non clos, aucune CI distante ni publication annoncée à cette sous-étape.
