# Suggestion IA — plan et suivi des trois sous-étapes

Date : 17 novembre 2026. Base : `19820723c5babd14d0425ee8b2d0e0abd882ddbb`,
arbre propre au début de cette préparation. Ce document est une proposition de
Codex fondée sur les décisions de l'utilisateur. Mise à jour : l'utilisateur a
approuvé uniquement la sous-étape 1, la borne 1–1 000 après trim, les filtres
laboratoire/date, l'ordre existant et les dix candidats distincts maximum. Son
service injectable est désormais construit ; voir `AI_SERVICE_1.md` pour les
preuves. La sous-étape 2 est ensuite autorisée : adaptateur, processus et API
sont construits et testés hors fournisseur (`AI_TRANSPORT_2.md`). UI ensuite
autorisée puis construite hors fournisseur (`AI_UI_3.md`) ; conditions Google
à résoudre avant usage réel. Les propositions initiales ci-dessous restent le
plan historique, les guides de chaque sous-étape précisent les preuves actuelles.
Aucun AC n'est réécrit ou renuméroté.

## Périmètre et origine des exigences

- **Professeur** : appel hors HTTP, délai et repli, sortie contrôlée avant
  affichage, faux client, description des données sortantes dans SPEC ; tests
  portant les AC exacts, couverture globale ≥ 80 %, états UI lisibles. Le Lab 03
  demande plan relu avant code, petits points de contrôle, tests de refus d'abord
  et preuves honnêtes. Ses sections « What you build » et celles du projet
  « When you build which part » permettent de construire le modèle séparément
  avant l'exercice 4. Elles ne rendent pas obligatoire un nouvel outil MCP IA.
- **Choix du projet déjà consignés** : texte, `gemini-3.5-flash-lite`, au plus dix
  couples poste/créneau, identifiant unique en sortie, aucune réservation par la
  suggestion, contrôle avant affichage puis à la confirmation ; attente
  fournisseur ≤ 5 s, aucune relance, sélection manuelle disponible ; AC-29 à AC-36.
  Le projet conserve son seuil supplémentaire de 100 % lignes/branches services.
- **Choix approuvés pour la sous-étape 1** : besoin de 1 à 1 000 caractères après
  trim, laboratoire/date sélectionnés et premiers dix candidats distincts dans
  l'ordre existant. **Recommandations encore à examiner** : REST Python standard
  dans un processus annulable et contrats HTTP des sous-étapes suivantes.

### Résumé des trois points de contrôle

Ce résumé constitue le plan d'exécution court ; les sections suivantes en sont
les précisions techniques demandées, à examiner avant toute construction.

| Sous-étape proposée | Livraison vérifiable avant la suivante | AC concernés |
| --- | --- | --- |
| 1. Service et faux client | Sélection bornée, validation, relecture, repli et aucune écriture | AC-29/30/32/33/35/36 ; partie service d'AC-31/34 |
| 2. Adaptateur et API | Un appel REST borné, endpoint session/CSRF, tests entièrement hors fournisseur | AC-29 à AC-36, preuves API partielles |
| 3. Écran existant | Demande explicite, suggestion identifiée, confirmation existante et preuves navigateur distinctes | AC-29 à AC-36 et parties pertinentes AC-41/42/43/44 |

Arrêt pour revue à chaque sous-étape. L'autorisation courante couvre la sous-étape
2 et son commit local : transport borné/API/tests hors réseau. Aucune installation,
migration, clé réelle, appel modèle, CI ou push ; sous-étape 3 non autorisée.
La note personnelle, la validation complète Gemini MCP et les UI reportées,
notamment 380 pixels, restent ouvertes ; cette préparation ne clôt pas le Lab 03.

## Sources relues et état du modèle

Sources consultées le **17 novembre 2026** ; les deux pages du cours ont échoué
avec l'outil Web, puis ont été lues avec `curl` en lecture seule :

1. [Lab 03](https://webdev-course.tu-sofia.workers.dev/en/resources/exercises/3/)
   : « Goal », « Steps » (plan, checkpoints, tests et contrôles), « What you
   build », « Working with the agent ». La note personnelle demandée reste à
   écrire par l'étudiant. Pas de migration artificielle pour cette suggestion :
   elle réutilise le schéma de réservation livré ; l'exigence de migration du
   parcours vertical est déjà distincte de cet ajout sans persistance.
2. [Projet](https://webdev-course.tu-sofia.workers.dev/en/guides/project/)
   : « The requirements, exactly » ; « 3. A feature that uses a model » ;
   « 5. A UI somebody would use » ; « 7. Tests that trace, and 80% coverage » ;
   « Lab booking » ; « When you build which part » ; « Free tiers… ».
3. [Fiche Google](https://aistudio.google.com/docs/models/gemini-3.5-flash-lite)
   et [retraits](https://aistudio.google.com/docs/deprecations) : identifiant stable
   présent, entrée/sortie textuelles et sorties structurées prises en charge,
   aucune date de retrait annoncée. Aucun remplacement proposé : le modèle reste
   adapté à cette sélection restreinte. **Accès du compte non testé.**
4. [Tarification — Gemini 3.5 Flash-Lite](https://aistudio.google.com/docs/pricing#gemini-3.5-flash-lite)
   : entrées/sorties standard gratuites annoncées ; pas une promesse d'accès
   illimité. [Quotas](https://aistudio.google.com/docs/rate-limits) : par projet,
   limites selon modèle/niveau, accès parfois soumis à vérification. Aucun quota
   effectif, coût réel ou disponibilité de notre compte n'a été mesuré.
5. [Conditions Google](https://aistudio.google.com/docs/terms#use-restrictions)
   : restriction aux Paid Services pour la mise à disposition de clients API à
   des utilisateurs EEE/Suisse/Royaume-Uni. La rubrique données précise aussi
   une exception régionale au régime général d'utilisation des données gratuites.
   Le tarif gratuit ne suffit donc pas à conclure que notre site pour étudiants
   en Bulgarie peut employer ce niveau. **Point à clarifier avant tout usage
   réel**, sans activer de facturation. Les tests avec faux client restent
   possibles. Si cette restriction empêche le choix, présenter à l'utilisateur
   une alternative locale ou un autre fournisseur autorisé, avec examen explicite
   de SPEC et AC-31 ; aucun changement silencieux de modèle.
6. [Sorties structurées](https://aistudio.google.com/docs/structured-output)
   (« Best practices », « Limitations ») et [generateContent](https://aistudio.google.com/api-reference/generate-content)
   : JSON Schema supporté en partie, validation applicative toujours nécessaire.
   Proposition REST : `generationConfig.responseMimeType=application/json`,
   `responseJsonSchema` pour un objet avec un seul champ `candidate_id`, chaîne
   et enum des identifiants réellement envoyés ; `candidateCount=1`. Pas de
   recherche, fichiers, outils, conversation ou appels supplémentaires.
7. [SDK Python Google, types](https://github.com/googleapis/python-genai/blob/main/google/genai/types.py)
   : `HttpOptions.timeout` en millisecondes ; `HttpRetryOptions.attempts` inclut
   l'essai initial, défaut documenté 5, 0/1 sans relance. Source main consultée,
   pas une version installée ou figée. Un SDK par défaut n'est donc pas acceptable
   pour notre règle. Recommandation : pas de SDK ni nouvelle dépendance ; REST
   avec la bibliothèque standard. [urllib Python 3.13](https://docs.python.org/3.13/library/urllib.request.html)
   borne des opérations bloquantes, **pas une durée totale de cinq secondes**.

## 1 — Service de suggestion, validation et faux client

**Fichiers proposés** : `src/services/ai_suggestion.py` (orchestration et contrats),
`src/data/ai_suggestions.py` (seulement relecture de l'acteur courant par ORM si
aucune projection existante ne convient), `tests/test_ai_suggestion.py`.
Réutiliser `src/services/booking_reads.py:list_available_slots` et ses projections
`AvailableSlot` ; aucune requête ORM dans le service. Aucun changement de modèle,
migration, caractéristique matérielle ou nouvel horaire.

**Contrat proposé** :
`suggest_slot(actor, laboratory_id, day, need, *, client, clock)`.
L'horloge métier fournit l'instant UTC ; l'échéance utilise une source monotone
distincte, injectable pour les tests, jamais une soustraction d'heures civiles.
Acteur issu de l'adaptateur authentifié, jamais du JSON. Le service refuse un
acteur absent/inactif ou non étudiant, en réutilisant AuthenticationRequired et
StudentRequired. Identifiant entier positif (pas booléen), date calendaire,
besoin de type chaîne, espaces externes retirés ; refuser vide/blanc, NUL et
plus de 1 000 caractères Unicode après ce retrait, sans tronquer. Même règle
côté serveur, `maxlength` seulement comme aide côté navigateur. Pas d'analyse
prétendant nettoyer le texte ou en extraire de nouveaux filtres métier.

Le laboratoire et la date sélectionnés sont les filtres explicites. Appeler
`list_available_slots` avec horloge contrôlable : horaires Sofia, début futur,
état du poste, occupation, conflit personnel et quota restent ceux du service
existant. Dédupliquer par `(workstation_id, starts_at, ends_at)`, ordonner par
début UTC puis identifiant poste, prendre les dix premiers (ou moins). Attribuer
des identifiants temporaires `c1`…`c10` propres à cet appel, sans stockage.
Zéro candidat → résultat `no_candidates`, zéro appel, même sans clé.

Le faux ou vrai client reçoit seulement `need`, les candidats minimaux
`{candidate_id, workstation_name, starts_at, ends_at}` et une échéance monotone ;
les heures UTC sont explicites et le contexte indique Europe/Sofia. Aucun Actor,
e-mail, identifiant utilisateur, session, historique ni réservation d'autrui.
Les instructions fixes demandent une sélection parmi ces données et traitent le
besoin comme contenu non fiable. Pas de promesse sur le calme, le matériel ou
l'adéquation à un besoin non décrit dans nos modèles. L'ordre peut favoriser les
premiers postes/créneaux ; ce sous-ensemble n'est pas une recherche optimale.

**Client injectable** : `select_candidate(need, candidates, *, deadline)` retourne
un objet JSON décodé non fiable, ou une erreur fournisseur typée sans contenu
sensible. Valider objet exact, champ unique `candidate_id`, chaîne non vide et
appartenance à la liste ; refuser prose, listes, booléens, champs supplémentaires,
JSON ambigu/dupliqué et sortie tronquée. Ne jamais afficher un texte du modèle.
Relire l'acteur actif/étudiant, l'heure et `list_available_slots` après l'attente ;
retrouver le même couple dans les résultats complets actualisés (pas seulement
dans leur nouvelle tranche de dix). S'il n'est plus admissible, refuser la
suggestion ; ne pas choisir arbitrairement un autre candidat ni rappeler le modèle.
Le nom et les heures affichés viennent de cette relecture applicative.

Résultat sans HTTP : `SuggestionResult(status, candidate=None, reason=None)` ;
`status` vaut `suggested`, `no_candidates` ou `unavailable`. Une suggestion valide
porte seulement le poste et le créneau applicatifs, pas une autorisation de créer.
Erreurs de saisie/auth/ressource restent des exceptions métier ; motifs de repli
stables : `not_configured`, `timeout`, `quota`, `provider_error`, `invalid_output`,
`candidate_unavailable`. Pas d'exception brute transmise à l'utilisateur.

**Tests d'abord**, AC exacts dans les titres : 3/10/>10, doublons/ordre stable,
aucun candidat (AC-29/30), payload sans identité/historique (AC-31), suggestion
unique sans mutation (AC-32), toutes sorties refusées et disponibilité/quota/
rôle changés pendant l'appel (AC-33), clé absente et erreurs (AC-35), deadline
et zéro relance avec horloge monotone injectée (AC-36). Vérifier base inchangée,
appel unique, permissions et absence de transaction/verrou pendant le faux appel.
AC-34 est seulement préparé ici : la confirmation viendra par le service existant.

## 2 — Adaptateur fournisseur et API protégée

**Fichiers proposés** : `src/integrations/__init__.py`, `src/integrations/gemini.py`
(unique point d'appel fournisseur, transport et petit worker isolé),
`src/routes/ai_suggestion.py`, `src/config/urls.py`, configuration non secrète
dans `src/config/base.py` si nécessaire ; adapter les helpers d'erreurs JSON et
CSRF de `src/routes/booking_http.py`/`src/routes/pages.py` sans les affaiblir.
Tests : `tests/test_gemini_adapter.py`, `tests/test_ai_suggestion_api.py`.

REST non streaming vers
`https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent`.
Lire exclusivement `GEMINI_API_KEY` de l'environnement de l'application future,
sans rechercher/réutiliser les fichiers Gemini CLI. Clé absente : aucun réseau.
En-tête `x-goog-api-key`, jamais paramètre URL. Transport HTTPS avec vérification
TLS, pas de redirection ni retry/challenge automatique, une seule tentative
applicative même sur 429/5xx. Aucun `countTokens`, découverte modèle ou réparation
de JSON par second appel. Rejeter réponse non JSON, blocage sécurité, absence de
contenu, plusieurs réponses inattendues ou sortie incomplète ; borner la lecture
à 64 Kio et la génération à un petit plafond (proposition 128 tokens, tronquage
traité comme échec). Valider de nouveau le contenu dans le service.

**Budget réel** : échéance `monotonic()+5` avant démarrage du travail fournisseur,
incluant lancement, envoi et lecture. Une requête ne conserve aucune transaction
ni verrou pendant cette phase ; vérifier aussi `ATOMIC_REQUESTS=False`. Un simple
thread avec `future.result(timeout=5)` ou timeout socket ne suffit pas. Proposition
sans dépendance : worker Python via le même interpréteur, sans initialisation
Django/connexion DB, stdin/stdout privés en mémoire pour les données. Environnement
enfant minimal et clé dédiée uniquement en mémoire, aucun profil/session transmis,
aucun argument sensible, stderr neutralisé/sanitizé. **Le nettoyage fait partie
des cinq secondes**, pas d'un délai ajouté après expiration : réserver une marge
dans ce même budget (proposition 500 ms, donc attente du résultat au plus 4,5 s,
moins le temps déjà consommé au lancement). Au seuil de terminaison, fermer le
canal, terminer le worker et borner toute attente de fin au reste de l'échéance
globale. Aucun `wait`/`communicate` supplémentaire après celle-ci, aucun résultat
tardif utilisé ni nouvelle tentative. Le test de durée murale doit inclure le
cas d'un nettoyage lent et prouver que le retour de repli n'est pas retardé par
ce nettoyage ; si la terminaison et la récupération des ressources ne peuvent
pas respecter ce contrat, cette conception doit être revue avant livraison.
Ne pas utiliser un
gestionnaire de contexte qui attendrait indéfiniment la fin du worker. Le timeout
interne reçoit au plus le budget restant. Le budget porte sur l'attente fournisseur,
pas les lectures DB ni le transit navigateur ; ni ordonnancement OS temps réel ni
arrêt garanti du calcul déjà reçu par Google ne sont promis.

Tester d'abord le worker bloqué, sa terminaison et la libération des ressources
sous Windows/Linux avec un worker factice, sans requête réseau. Tester le transport
par réponses simulées : URL/en-têtes/schéma, 429, 5xx, DNS/TLS simulés, redirection,
réponse lente ou trop grosse, aucune seconde tentative. Horloge contrôlée pour
l'échéance, plus un test borné du mécanisme de processus ; pas seulement un mock
qui déclare respecter cinq secondes. Si ce mécanisme ne prouve pas le budget,
arrêter cette sous-étape et revoir le transport ; ne pas annoncer AC-36 satisfait.

**Route proposée** : `POST /api/labs/{id}/suggestion`, JSON exact
`{"date":"YYYY-MM-DD","need":"…"}` ; session Django ordinaire et CSRF même si
aucune réservation n'est créée, car la demande peut consommer un quota fournisseur.
Pas de candidat ou d'identité fourni par le navigateur. Réponse 200 :
`{"status":"suggested","candidate":{…}}` ou
`{"status":"no_candidates","candidate":null,"message":"…"}`.
Refus : 401 session, 403 personnel/CSRF (tests distingués), 404 laboratoire,
422 saisie, 400 JSON, 405 méthode, 415 type, 409 candidat périmé,
503 clé absente/quota/panne, 504 délai, 502 sortie invalide ; ces échecs retournent
un code applicatif et une phrase lisible, jamais le corps brut fournisseur.
Erreurs internes 500 sans détail sensible. Réponses sans cache. La route parse,
obtient l'acteur, injecte le client, appelle le service et sérialise : ni ORM ni
appel fournisseur direct. Aucun stockage du besoin ou de la réponse dans la session.

Tests HTTP hors réseau AC-29 à AC-36 selon le comportement réellement prouvé :
session absente/inactive, personnel, vraie vérification CSRF, corps malformé ou
trop long, zéro appel pour refus/absence de candidat/clé ; mêmes résultats que
le service, erreurs lisibles et base inchangée. Tester des valeurs factices
sensibles dans les exceptions et s'assurer qu'aucune sortie/log ne les contient.
Ne journaliser ni besoin, ni clé, ni prompt, ni réponse brute ; seulement code
d'échec fixe, durée et compteur si utile. Pas de debug HTTP du client.

## 3 — Interface existante, confirmation et preuves

**Fichiers proposés** : `src/templates/labs.html`, `src/static/js/booking.mjs`
(petit module `ai_suggestion.mjs` si cela garde les responsabilités lisibles),
CSS existant `src/static/css/` si nécessaire, `tests/booking_ui.test.mjs` et
`tests/ai_suggestion_ui.test.mjs` ; guide futur des essais, README/USAGE/journal,
traçabilité et état factuel dans SPEC. Aucun nouvel écran/catalogue fictif.

Dans les disponibilités du laboratoire et de la date choisis : libellé explicite,
besoin borné, avertissement avant envoi (« Ne saisis pas de données personnelles
ou confidentielles ; ton besoin est transmis à Google »). Aucun appel à la saisie,
au chargement, au changement de date ou au simple affichage des disponibilités :
seul « Demander une suggestion IA » déclenche le POST avec session/CSRF.
États attente, suggestion identifiée comme IA, aucun candidat et échec explicite ;
le choix manuel reste accessible et n'est jamais nommé succès IA.

Verrou de demande JS posé avant le premier `await`, bouton désactivé en vol,
une action → au plus un fetch, aucune relance automatique ou bouton de retry qui
s'enclenche seul. Changement de laboratoire/date/besoin ou sélection manuelle
invalide la suggestion et les réponses tardives via un numéro de génération ;
elle ne doit pas écraser une sélection récente. Ne pas prétendre dédupliquer
globalement plusieurs onglets ou des demandes indépendantes : aucun tel contrat
exactly-once, quota IA ou table d'idempotence n'est ajouté par ce plan.

La suggestion sélectionne un seul couple dans le panneau existant ; seul le
bouton distinct « Confirmer la réservation » envoie le POST existant
`/api/bookings` vers `create_booking`. Aucune confiance dans `candidate_id` pour
autoriser la création. Ce service revérifie transactionnellement acteur actif,
rôle, poste, heure, conflits et quota avec ses verrous actuels. Aucun nouvel appel
IA à la confirmation ; refus lisible si le monde a changé, données inchangées.
Préserver les protections contre doubles POST et résultat réseau incertain.

Tests DOM/fetch : AC-31 avertissement, AC-32 affichage depuis les champs reçus
avec `textContent`, AC-30/33/35/36 états/repli, absence d'appel spontané/double,
réponse obsolète ignorée, 401/403, choix manuel après échec. AC-34 : faux client
pour suggestion puis véritable API de création sur PostgreSQL de test, succès
unique et refus après poste occupé/hors service, quota ou conflit personnel.
Vérifications navigateur séparées avec démo autorisée, fournisseur simulé par
injection réservée aux tests (jamais une suggestion faussement présentée comme
réel appel Google), clavier/focus, erreurs, contraste et états. Aucune preuve
visuelle ni appel réel n'est déduit des tests DOM. 380 pixels reste reporté tant
qu'aucun nouvel essai n'a été autorisé et observé.

## Vérifications futures et décisions à prendre

- Aucune dépendance ni migration prévue dans les trois étapes. Le transport et
  son worker font partie de l'inventaire de production et de la couverture,
  y compris les subprocessus ; aucune exclusion ajoutée. Conserver `npm test`,
  les contrôles TP1, Node et `node checks/ex2.mjs` ; utiliser la couverture
  `.\.venv\Scripts\python.exe tools/check_coverage.py --postgresql`.
  Seuils inchangés : services 100 % lignes/branches, global Python ≥ 80 %, TP1
  inclus. Futurs tests sans accès fournisseur même si une clé existe dans
  l'environnement ; configuration de test explicitement factice.
- `node checks/ex3.mjs` restera un diagnostic de structure, pas une cible à
  tromper. Relier les nouveaux tests aux vrais AC et conserver les exigences
  encore absentes ; ne pas remplir la note personnelle ou déclarer l'IA livrée
  grâce à une chaîne de caractères reconnue par le vérificateur.
- **Sous-étape 1 approuvée et construite** : borne de 1 000 caractères,
  laboratoire/date sélectionnés, dix premiers slots distincts et service fake.
  **Sous-étape 2 autorisée et construite ensuite** : adaptateur REST isolé,
  marge de nettoyage incluse et contrats API ; détails et preuves dans
  `AI_TRANSPORT_2.md`. **Avant la suivante** : validation du travail livré puis
  autorisation de l'interface, sans présenter celle-ci comme acquise.
- **Avant un essai fournisseur seulement** : conditions EEE et niveau gratuit,
  accès effectif/quotas du compte, remise autorisée d'une clé applicative sans
  lecture de secrets existants et autorisation explicite d'appel. Aucun de ces
  points n'empêche les deux premières étapes avec faux client après validation.
- Aucun nouvel outil MCP, Google OIDC, personnel, déploiement ou changement CI
  dans ce plan. La revue indépendante de ce plan ne remplace pas sa validation
  par l'utilisateur ni la future revue du code.

Revue indépendante du plan : aucun blocage, un risque retenu sur le temps de
nettoyage du worker après expiration. Proposition corrigée ci-dessus : réserver
ce temps **dans** les cinq secondes, avec test incluant un nettoyage lent. La
marge et la faisabilité restaient à valider à cette revue du plan. Les mesures
locales obtenues ensuite en sous-étape 2 sont dans `AI_TRANSPORT_2.md` ; elles
ne constituent pas une preuve d'accès au fournisseur ou de rendu navigateur.
