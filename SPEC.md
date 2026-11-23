# Lab booking

<!-- Exercise 2. Write the non-goals first. Every acceptance criterion must be checkable in under a minute.
     Keep these headings exactly as they are: the self-checks look for them by name.
     The full target is on the course site under Resources → The course project. -->

## Project option
<!-- One line: lab booking, study groups, club events, or the own project the lecturer approved. -->
Lab booking.

## Goals

Ces objectifs décrivent le projet final. La première tranche reste limitée à la connexion locale, la déconnexion et la consultation d’une liste protégée des laboratoires provenant de la base de données.

- Objectif étudiant : un étudiant connecté peut consulter les laboratoires et les postes disponibles pour une date et un créneau, choisir un poste et le réserver si aucune réservation non annulée existante ne chevauche ce créneau sur ce poste, et si les autres règles métier sont satisfaites. Il peut ensuite consulter ses propres réservations et annuler une réservation à venir qui lui appartient. Il ne peut pas modifier ou annuler celles d’un autre utilisateur.
- Objectif personnel : un membre du personnel autorisé peut créer et mettre à jour les laboratoires et leurs postes, consulter les réservations et indiquer qu’un poste est temporairement indisponible, puis le remettre en service.

## Non-goals

- Aucune réservation payante : l’utilisation des postes est gratuite. Le projet ne comprend ni paiement en ligne, ni abonnement payant, ni facturation.
- Aucune application mobile native Android ou iOS : nous développons un site web qui reste utilisable sur téléphone.
- Aucune notification automatique liée aux réservations par e-mail, SMS ou push : l’utilisateur consulte ses réservations et leur état dans le site. Cette exclusion ne concerne pas les mécanismes d’authentification.

## Constraints

- Use Django 5.2 LTS with HTML, CSS and plain JavaScript calling the REST API through fetch.
- Use SQLite for slice 1: local sign-in, sign-out and the protected laboratories list. Move to PostgreSQL for the booking slice so database constraints and simultaneous bookings are tested on the target database.
- Define a user model suitable for email sign-in from the first migrations, reusing Django's password and session mechanisms.
- Keep business permissions in services shared by HTTP routes and MCP tools.

### Business rules

Comportements attendus pour le projet final, à préciser dans les critères d’acceptation ; ils ne sont pas encore implémentés ni testés.

- L’indisponibilité temporaire d’un poste est un état « en service / hors service », sans calendrier de maintenance à programmer.
- Un poste hors service n’accepte aucune nouvelle réservation.
- Les réservations déjà enregistrées restent visibles et signalent l’indisponibilité du poste. Elles ne sont ni annulées ni déplacées automatiquement.

#### Time slots

- Une réservation concerne un poste et un créneau prédéfini d’une heure, commençant à une heure entière. L’utilisateur sélectionne un créneau proposé et ne saisit pas librement les heures de début et de fin.
- Les créneaux sont proposés du lundi au vendredi, de 08:00 à 18:00 dans le fuseau Europe/Sofia : le premier est 08:00–09:00 et le dernier 17:00–18:00.
- Ces horaires sont une convention du projet commune aux laboratoires, et non les horaires officiels de TU Sofia. Le projet ne prévoit ni calendrier des jours fériés ni horaires personnalisés par laboratoire.
- Un créneau déjà commencé ou passé ne peut pas être réservé. Le serveur doit vérifier que son début est strictement postérieur à l’instant courant lors de la réservation ; la sélection proposée dans l’interface ne suffit pas à garantir cette règle.
- Les dates et heures doivent gérer le fuseau horaire. Le stockage et les échanges utilisent une référence UTC, avec conversion vers Europe/Sofia pour l’affichage ; aucun décalage UTC fixe ne doit être utilisé.
- Les intervalles suivent la convention [début, fin) : le début est inclus et la fin est exclue. Deux réservations consécutives d’un même poste sont donc compatibles, par exemple 09:00–10:00 et 10:00–11:00, sans intervalle de préparation.

#### Cancellation

Décision explicite de l'utilisateur pour les jalons suivants : une nouvelle
demande d'annulation de sa propre réservation déjà annulée répondra HTTP 200
avec son état actuel, sans nouvelle mutation. Le propriétaire doit toujours être
contrôlé. Le modèle seul n'implémente ni cette règle métier ni sa réponse HTTP.

- Un étudiant peut annuler uniquement ses propres réservations, strictement avant leur début : maintenant < début_du_créneau. Aucun délai supplémentaire n’est imposé ; pour un créneau débutant à 10:00, l’annulation est autorisée avant 10:00 et refusée à partir de 10:00.
- Cette possibilité d’annulation reste valable si le poste a été déclaré hors service.
- Une réservation annulée reste conservée comme telle dans l’historique. Elle ne bloque plus le créneau et ne compte plus dans le quota. Le poste redevient réservable si toutes les autres conditions sont satisfaites, notamment son état « en service ».

#### Per-student limits

Décision explicite de l'utilisateur : seuls les étudiants peuvent créer des
réservations, sans privilège implicite pour le personnel. Ce contrôle sera ajouté
dans les services partagés à un jalon ultérieur ; il n'est pas assuré par le schéma.

- Un étudiant peut détenir au maximum trois réservations à venir et non annulées, tous laboratoires et postes confondus. « À venir » signifie que le début est strictement postérieur à l’instant courant ; les réservations annulées, en cours ou passées ne comptent pas dans ce quota.
- Une quatrième réservation future est refusée avec un message compréhensible et sans création d’une nouvelle réservation.
- Une réservation future sur un poste devenu hors service continue de compter dans le quota tant que l’étudiant ne l’a pas annulée.
- Un étudiant ne peut pas détenir deux réservations non annulées qui se chevauchent, même sur des postes différents ou dans des laboratoires différents.
- Deux créneaux consécutifs restent autorisés, par exemple 09:00–10:00 puis 10:00–11:00, dans la limite du quota.

#### Shared enforcement and concurrent requests

- Ces règles doivent être appliquées dans les services partagés par HTTP et MCP.
- La tranche de réservation sur PostgreSQL doit vérifier ces règles lors de créations simultanées : aucun double usage d’un même poste, aucun chevauchement pour un même étudiant et aucun dépassement du quota. Les trois scénarios de services sont désormais vérifiés au jalon 2C ; cela ne prouve pas tous les entrelacements ou les parcours HTTP simultanés.

### Slice 2 — regroupement de livraison finalisé au jalon 4

Disponibilités, création pour soi, historique et annulation propriétaire sont
exposés par HTTP sur PostgreSQL, en complément des services existants. Périmètre
référencé : AC-11 et AC-13 à AC-28, avec AC-46/49 pour les preuves de session
applicables. Sur instruction de finaliser le regroupement, Slice 2 rassemble
AC-11 et AC-13 à AC-28 ; les AC-40 à AC-45 sont transversaux à l'interface et
AC-46/49 à la session. Le regroupement de livraison est consigné ici, sans
inventer la validation des critères ni une rédaction personnelle de l'étudiant.
Aucun critère approuvé n'est réécrit ou renuméroté.

| Route | Contrat |
| --- | --- |
| GET /api/labs/{id}/availability?date=YYYY-MM-DD | 200, slots réservables pour la session ; aucun propriétaire ni historique d'autrui |
| GET /api/bookings | 200, bookings de la seule session, historique compris |
| POST /api/bookings | JSON exact workstation_id, starts_at, ends_at ; 201, booking créé pour l'acteur |
| POST /api/bookings/{id}/cancel | JSON {} ; 200, booking annulé ou état existant sans nouvelle mutation |

Dates ISO 8601 conscientes du fuseau, sérialisation UTC suffixe Z, champs
explicitement sélectionnés. Toute donnée propriétaire du client est refusée,
jamais utilisée. Erreurs JSON stables {"error": "message"} : 401 authentification,
403 autorisation/CSRF, 404 ressource inexistante, 409 conflit/quota/hors service/
annulation tardive/BookingChanged, 422 forme ou créneau invalide (début non futur
compris), 400 JSON mal formé, 405 méthode avec Allow, 415 Content-Type non pris
en charge, 500 erreur interne sans détail sensible. Les mutations exigent
application/json et le CSRF Django ; celui-ci peut refuser avant la vue. Les
statuts de service sont traduits uniquement dans l'adaptateur HTTP.

Contrats détaillés : docs/HTTP_API_3.md. L'interface de réservation et d'historique
est livrée au jalon 4, docs/STUDENT_UI_4.md ; aucun succès navigateur n'est
déduit des tests HTTP/DOM simulé. La section Architecture reste à rédiger personnellement
par l'étudiant ; elle n'est pas remplie par les assistants.

## The model feature
<!-- Which model, which modality, and what it does for a user.
     Name three things or the check fails: the input it receives, the output it produces,
     and what happens when the model is slow, rate-limited or wrong. -->
- Model: Gemini 3.5 Flash-Lite, identifiant `gemini-3.5-flash-lite`, pour une utilisation textuelle de suggestion d’un poste et d’un créneau. Ce choix vise une sélection limitée et structurée, avec une faible latence et un coût limité. Il s’agit d’une décision à implémenter après la première tranche, pas d’une intégration existante.
- Input: le besoin saisi par l’étudiant et les caractéristiques utiles d’une liste d’au maximum dix candidats réservables fournie par le serveur. Un candidat représente un couple précis « poste + créneau » et doit respecter les règles et filtres applicables. Si moins de dix candidats sont disponibles, transmettre uniquement ceux disponibles ; si aucun candidat n’est disponible, ne pas appeler le modèle. Ne pas ajouter l’identité ni l’historique des utilisateurs. Un avertissement demande de ne pas saisir de données personnelles ; il ne garantit pas leur absence dans le texte libre transmis au fournisseur.
- Output: l’identifiant d’un seul candidat. Le serveur doit vérifier son appartenance à la liste fournie et sa disponibilité avant affichage, puis construire l’affichage depuis les données de l’application. Une suggestion ne crée aucune réservation. Après confirmation de l’étudiant, le service de réservation doit revérifier toutes les règles avant toute création.
- When it fails: clé absente, délai dépassé, quota, erreur du fournisseur ou sortie invalide entraînent un message explicite ; la sélection manuelle reste disponible. L’appel doit durer au maximum cinq secondes, sans relance automatique, y compris une relance implicite du client. Les tests utilisent un faux client pour couvrir les succès et les échecs sans appeler le modèle réel.

Le plafond de dix candidats est un choix de conception pour borner les données transmises. Il ne garantit ni la qualité de la recommandation ni un temps de réponse du modèle. Le délai maximal de cinq secondes est une limite d’attente de l’application, avec repli en cas de dépassement. Les règles doivent toujours être revérifiées au moment de réserver après la suggestion et la confirmation de l’utilisateur.

Sources officielles consultées le 3 novembre 2026 : [fiche du modèle](https://aistudio.google.com/docs/models/gemini-3.5-flash-lite), [tarification, rubrique Gemini 3.5 Flash-Lite](https://aistudio.google.com/docs/pricing#gemini-3.5-flash-lite) et [calendrier de retrait des modèles](https://aistudio.google.com/docs/deprecations#gemini-3-models). Le fournisseur annonce un niveau gratuit pour les entrées et sorties standard de ce modèle. L’accès effectif et les quotas disponibles pour ce projet restent non testés ; aucune facturation n’a été activée pendant cette préparation.

Sous-étape IA 1, 17 novembre 2026 : `src/services/ai_suggestion.py` est construit
avec un client injectable uniquement. Besoin après trim de 1 à 1 000 caractères,
laboratoire/date sélectionnés, dix candidats distincts maximum dans l'ordre des
disponibilités existantes, identifiants temporaires, sortie structurée contrôlée
puis relecture de l'acteur et des disponibilités. Aucun appel fournisseur, route,
écran ou création/annulation n'est livré par ce service. Le contrat transmet une
échéance monotone de cinq secondes et rejette un résultat tardif ; il ne peut pas
interrompre un client bloquant et ne prouve pas le délai du futur transport.
Texte libre potentiellement personnel malgré la validation ; aucun ajout
d'identité/session/historique et aucune journalisation du besoin/résultat brut.
Guide des preuves et limites : `docs/AI_SERVICE_1.md`. Les conditions Google EEE
restent à clarifier avant tout usage réel ; aucune facturation activée.

Sous-étape IA 2 : adaptateur REST et `POST /api/labs/{id}/suggestion` construits,
sans interface ni appel Google. Client désactivé par défaut ; activation future
explicite via LAB_BOOKING_AI_ENABLED et clé applicative d'environnement uniquement,
sans lecture des fichiers CLI. Processus enfant sans Django/base, communication
privée bornée, tentative unique, échéance monotone incluant lancement et nettoyage.
Sorties structurées et candidats revérifiés ; aucune mutation de réservation.
Tests REST simulés, vrais processus locaux contrôlés et API/PostgreSQL avec client
substitué. Ce ne sont ni une preuve d'accès du compte au fournisseur, ni une
validation du rendu UI. Conditions Google EEE, statut et limites :
`docs/AI_TRANSPORT_2.md`. Aucun critère approuvé n'est modifié.

Sous-étape IA 3 : formulaire facultatif sur /labs, avertissement, sélection
manuelle conservée et confirmation explicite via la création existante.
Besoin/contexte modifiés : suggestion invalidée et réponse tardive ignorée.
Adaptateur toujours désactivé par défaut ; aucun fournisseur réel essayé.
Preuves DOM, HTTP PostgreSQL et Edge désactivé/simulé : `docs/AI_UI_3.md`.

## Auth
<!-- Local sign-in plus at least one provider. Say how an account signing in both ways stays one account. -->
- Local: Email and password, using a user model defined in the first migrations and Django's password hashing and session mechanisms.
- Provider: Google via OpenID Connect, avec traitement côté serveur et le même mécanisme de session Django que la connexion locale.
- Linking: la première liaison doit être initiée depuis un espace de compte authentifié, après réauthentification locale, avec confirmation explicite de l’utilisateur. L’adresse Google doit correspondre à celle du compte local et `email_verified` doit être vrai. Aucune fusion automatique ne doit avoir lieu sur la seule correspondance d’adresse. Conserver l’identité Google stable (`sub`, associée au fournisseur) pour retrouver le compte existant lors des connexions Google suivantes, sans nouvelle connexion locale préalable. Après cette première liaison, le retour du même `sub` avec une adresse différente ne doit ni recréer un utilisateur ni imposer une nouvelle liaison pour ce seul motif.
- Accounts: comptes précréés, sans inscription publique. Un compte Google non lié ne crée aucun compte ; afficher une explication permettant de revenir à la connexion locale puis au parcours de liaison.
- Roles: attribution administrative uniquement. La connexion Google ne confère aucun privilège de personnel.

Ces règles sont des décisions à implémenter. Source technique consultée le 3 novembre 2026 : [Google OpenID Connect](https://developers.google.com/identity/openid-connect/openid-connect), notamment `sub` et `email_verified`. Aucune connexion Google de l’application n’a été réalisée pendant la préparation de cette spécification.

## MCP tools
<!-- At least three tools your own MCP server exposes over this project's data.
     Each tool calls the same service functions the HTTP API calls, so the same rules apply.
     A description shorter than 20 characters is not a description. -->
| Tool | What it does | Who may call it |
| --- | --- | --- |
| list_free_slots | Consulter les créneaux et postes réservables pour préparer une réservation respectant les règles métier. | Utilisateur ordinaire authentifié, selon les mêmes permissions que la consultation HTTP. |
| my_bookings | Consulter ses propres réservations et leur historique, y compris les annulations et l’indisponibilité éventuelle du poste. | Utilisateur ordinaire authentifié, uniquement pour ses propres réservations. |
| book_slot | Réserver pour soi un poste sur un créneau proposé, après contrôle de la disponibilité, du quota et des chevauchements. | Utilisateur ordinaire authentifié autorisé à réserver, pour lui-même et sans dérogation aux règles. |
| cancel_booking | Annuler sa propre réservation avant son début, en conservant son historique et en libérant le créneau et le quota. | Utilisateur ordinaire authentifié, propriétaire de la réservation et sous les mêmes conditions que HTTP. |

Ces quatre outils sont retenus en complément de `find_lecture` et `search_lectures`
du TP 1. `list_free_slots`, `my_bookings`, `book_slot` et `cancel_booking` sont
livrés dans le seul mode `--project`, avec une session ordinaire revalidée à
chaque appel et les mêmes
services que leurs routes HTTP. Création non idempotente ; annulation propriétaire
idempotente après sa première transition, sans contourner les permissions.
Aucun accès administrateur implicite ni accès direct aux données depuis un outil.

Sous-étapes MCP 1–3 : le démarrage optionnel `--project`, l'adaptateur de session
Django et les quatre outils projet sont construits ; seuls des tests sur sessions
synthétiques PostgreSQL ont été effectués. Le catalogue projet contient les deux
outils TP1 et les quatre outils projet ; le mode par défaut conserve les seuls outils TP1.
Aucun parcours client final n'est validé. La remise manuelle
d'une vraie clé n'a pas été effectuée et n'est ni OAuth ni une connexion
automatique. Descriptions et annotations MCP sont des indications, pas une preuve
de consentement humain. Aucune mutation n'est relancée automatiquement après un
résultat de transport incertain : consulter l'historique avant une nouvelle
décision. Détails, résultats et limites : `docs/MCP_MUTATIONS_3.md`.

Finalisation : Gemini CLI 0.65.0 a réellement connecté le serveur avec
`gemini mcp list`, configuration/domicile isolés et jeton factice. Répertoire,
profil PostgreSQL et transfert d'environnement vérifiés, zéro sortie réseau
externe. Cette commande ne fait que initialize/notification/ping : aucune
découverte ni utilisation des outils par Gemini, aucune vraie session ou
confirmation humaine n'est déclarée validée. Les preuves AC-37/38/39 restent
celles des tests automatisés stdio/parité, avec leurs limites. État détaillé et
publication : `docs/MCP_FINALIZATION.md`.

## UI
<!-- Stack, and the three or more screens. The graded checklist lives in docs/UI.md. -->

- Stack: HTML, CSS and plain JavaScript using fetch to call the Django REST API.
- Slice 1 screens: local sign-in and the protected laboratories list, with sign-out available to the signed-in user.
- Final-project screens: connexion locale ou Google ; liste des laboratoires ; disponibilités d’un laboratoire avec suggestion IA intégrée ; « mes réservations » avec historique ; « espace du personnel » pour gérer laboratoires et postes et consulter les réservations ; espace de compte authentifié pour la liaison Google après réauthentification locale.
- States: prévoir les états chargement, vide, erreur et succès lorsqu’ils s’appliquent. Les erreurs doivent être compréhensibles ; la suggestion IA doit signaler son chargement et ses échecs tout en laissant la sélection manuelle disponible.

Catalogue, disponibilités, confirmation et historique/annulation sont construits
sur /labs au jalon 4. États et données fetch sont testés en DOM simulé, et le HTML
protégé avec Django. Codex a observé dans Edge le 12 novembre 2026 le parcours
disponibilités, confirmation, historique puis annulation conservée, sur la démo
PostgreSQL autorisée. Le 19 novembre, Codex a repris les essais à 380, 768 et
1 280 px CSS dans Edge, dont le refus de connexion à 380 px. Le parcours
clavier complet et les autres états non observés restent à vérifier.
L'espace du personnel contient la consultation des réservations en lecture seule
sur `/staff/bookings` et la création, le renommage et le changement d'état des
postes dans `/staff/catalogue`. L'espace de compte et Google restent à
construire. L'UI IA a été vérifiée hors fournisseur
(docs/AI_UI_3.md). Les quatre outils MCP sont construits et leur essai avec le
client final reste à faire. AC-40 reste partiel.

Attribution des exigences UI : `docs/UI.md` contient les largeurs 380/768/1280 pixels, l’absence de défilement horizontal et de déplacements au chargement, les états d’écran, le clavier et le focus, les libellés accessibles, le contraste 4,5:1, le titre et la langue, les cibles tactiles de 44 pixels et l’identification des suggestions IA. Il cite explicitement les jetons d’espacement et de typographie ; les jetons de couleurs et de rayons d’AC-45 sont une extension de conception retenue, pas une citation de cette checklist. L’organisation des espaces d’AC-40 est propre au projet. La checklist demande les quatre états sur chaque écran, alors qu’AC-41 conserve « lorsqu’ils s’appliquent » : cette correspondance devra être explicitée pour chaque écran. Elle ajoute un indicateur de chargement vers 100 ms, un succès visible sans rechargement, des preuves visuelles et une décision sur le mode sombre, que les critères ci-dessous ne remplacent pas. Aucun élément de la checklist n’est déclaré vérifié.

Statut des critères ci-dessous : cible fonctionnelle retenue par l’utilisateur, à implémenter et à vérifier. Leur formulation a été proposée par les assistants puis sélectionnée et corrigée par l’utilisateur ; cette sélection ne démontre ni sa compréhension ni une approbation du professeur. Chaque vérification est une méthode future, prévue pour rester courte après préparation des données. Les horloges, Google et l’IA seront simulés dans les tests automatisés ; ces simulations ne prouvent aucun accès effectif à un fournisseur. Des essais réels d’intégration Google/IA devront être distingués et autorisés séparément avant d’être exécutés ou rapportés. Aucun essai réel n’est autorisé pendant cette étape documentaire.

## Architecture
<!-- Exercise 3. One request traced through every layer, naming the file for each one,
     plus one place where your own code does not match this layering. -->

## Acceptance criteria

### Slice 2: disponibilités, réservation et annulation propriétaire

Slice 2 référence AC-11 et AC-13 à AC-28 ; leurs formulations restent dans les rubriques projet ci-dessous, sans doublon ni renumérotation. AC-40 à AC-45 sont transversaux, AC-46/47/49 concernent les sessions. Les critères futurs restent conservés et non validés. Preuves et écarts : docs/SLICE2_FINALIZATION.md et Traceability ; Architecture reste personnelle.
<!-- Every criterion carries an id. A test proves it by naming that id in its title, for example
     test('AC-3 a booking that overlaps another is refused with 409', ...).
     Say who acts, what they see, and what must be true in the database. -->
### Final project: authentication and permissions

- [AC-1] Première liaison Google : un utilisateur connecté à un compte précréé se réauthentifie localement puis confirme la liaison avec une identité Google portant la même adresse et email_verified=true. La liaison est confirmée et enregistrée avec l’identité stable Google, sans créer un second utilisateur. Vérification prévue : parcours avec fournisseur simulé et contrôle de la liaison et du nombre d’utilisateurs.
- [AC-2] Conditions de liaison manquantes : un utilisateur tente une liaison sans session locale, sans réauthentification, sans confirmation, avec une adresse différente ou non vérifiée. Chaque tentative est refusée avec une explication ; aucun utilisateur, rôle ou lien Google n’est créé ou modifié. Vérification prévue : test paramétré avec fournisseur simulé, une condition manquante à la fois.
- [AC-3] Connexion après liaison : un utilisateur déconnecté, dont l’identité Google est déjà liée, choisit la connexion Google. Le serveur retrouve directement le compte existant par l’identité Google stable et établit une session Django, sans nouvelle connexion locale ni utilisateur supplémentaire. Le même sub revenant avec une adresse différente ne déclenche ni recréation du compte ni nouvelle liaison pour ce seul motif. Vérification prévue : fournisseur simulé, avec adresse inchangée puis différente ; comparaison de l’identifiant utilisateur et des réservations retrouvées.
- [AC-4] Identité Google non liée : un visiteur utilise une identité Google non liée, même si son adresse correspond à un compte existant. La connexion explique comment revenir au parcours de liaison ; aucun compte ni lien n’est créé automatiquement. Aucune inscription publique n’est proposée. Vérification prévue : identité simulée non liée et contrôle des données.
- [AC-5] Autorisation du personnel : un étudiant authentifié tente directement une opération de gestion réservée au personnel via l’API, d’abord avec une session locale puis avec une session obtenue par Google. Dans les deux cas, la session valide sans le rôle nécessaire reçoit un refus d’autorisation ; le rôle et les données métier visées restent inchangés. L’absence d’un bouton ne suffit pas à démontrer ce contrôle. Vérification prévue : requêtes API avec les deux types de session, Google étant simulé dans le test automatisé, et comparaison en base.

### Final project: staff and workstation state

- [AC-6] Création d’un laboratoire : un membre du personnel connecté soumet des données valides pour un nouveau laboratoire. Le laboratoire apparaît dans la liste et une seule nouvelle entrée correspondante existe en base. Vérification prévue : création depuis l’espace du personnel et lecture de la ligne créée.
- [AC-7] Création d’un poste : un membre du personnel connecté ajoute un poste à un laboratoire existant. Le poste apparaît dans ce laboratoire et une seule entrée est créée avec le bon rattachement. Vérification prévue : formulaire préparé, affichage puis contrôle du rattachement en base.
- [AC-8] Mise à jour du catalogue : un membre du personnel connecté modifie les informations d’un laboratoire ou d’un poste existant. Les nouvelles informations sont visibles après rechargement ; l’objet est mis à jour sans duplication. Vérification prévue : test paramétré sur les deux types d’objet, avec comparaison avant/après.
- [AC-9] Consultation par le personnel : un membre du personnel connecté ouvre les réservations alors que les données de démonstration contiennent plusieurs propriétaires. Il peut consulter ces réservations ; cette lecture ne modifie aucune réservation. Vérification prévue : comparaison de la liste affichée avec les données préparées.
- [AC-10] Passage hors service : un membre du personnel place hors service un poste possédant des réservations futures. Son état change ; les réservations restent visibles avec l’indisponibilité signalée, sans annulation ni déplacement automatique. Vérification prévue : changement d’état et comparaison des propriétaires, créneaux et états des réservations.
- [AC-11] Nouvelle réservation sur un poste hors service : un étudiant sous le quota tente de réserver un créneau autrement valide sur un poste hors service. Il reçoit un refus compréhensible ; aucune réservation n’est créée. Vérification prévue : demande HTTP directe et contrôle du nombre de réservations.
- [AC-12] Remise en service : un membre du personnel remet en service un poste hors service. Ses créneaux satisfaisant toutes les autres règles redeviennent réservables ; ses réservations existantes restent inchangées. Vérification prévue : changement d’état, consultation des disponibilités et comparaison en base.

### Final project: time slots, booking and conflicts

- [AC-13] Créneaux proposés : un étudiant connecté consulte les disponibilités d’une date et d’un laboratoire préparés. Les créneaux proposés durent une heure, commencent à une heure entière et sont prévus du lundi au vendredi, de 08:00 à 18:00 dans Europe/Sofia, avec un dernier créneau 17:00–18:00 et sans calendrier des jours fériés. L’étudiant ne saisit pas librement leurs bornes. Ces horaires sont une convention du projet. Vérification prévue : consultation d’un jour du lundi au vendredi puis d’un week-end ; données métier inchangées.
- [AC-14] Conversion des horaires : un étudiant consulte des réservations de démonstration en période d’hiver et d’été. Les horaires affichés correspondent à Europe/Sofia, tandis que les échanges et la référence de stockage représentent les mêmes instants en UTC, sans décalage fixe. Vérification prévue : test de conversion sur deux dates préparées et contrôle des réponses API.
- [AC-15] Création valide : un étudiant connecté, sous le quota et sans conflit personnel, réserve un créneau futur libre sur un poste en service. Une confirmation apparaît ; une seule réservation est enregistrée pour cet étudiant, ce poste et ce créneau. Vérification prévue : action depuis l’écran et lecture de la réservation créée.
- [AC-16] Créneau temporellement invalide : un étudiant soumet directement une demande portant sur un créneau commencé, passé, hors horaires, le week-end ou ne respectant pas les bornes d’une heure proposées. Le serveur refuse la demande ; aucune réservation n’est créée. Vérification prévue : test paramétré incluant exactement l’instant de début, avec horloge simulée.
- [AC-17] Conflit avec une réservation déjà enregistrée : un étudiant tente de réserver un poste dont le créneau chevauche une réservation non annulée déjà présente en base avant sa demande. Il reçoit un refus compréhensible ; la réservation existante reste intacte et aucune nouvelle réservation n’est enregistrée. Vérification prévue : jeu de données contenant le conflit, puis demande séquentielle. Les demandes exécutées simultanément sont couvertes séparément par AC-22.
- [AC-18] Conflit personnel : un étudiant déjà titulaire d’une réservation non annulée tente d’en créer une autre qui la chevauche, sur un autre poste ou dans un autre laboratoire. La demande est refusée sans nouvelle réservation. Vérification prévue : test paramétré avec deux postes du même laboratoire puis de laboratoires différents.
- [AC-19] Créneaux consécutifs : un étudiant possédant une réservation 09:00–10:00 réserve 10:00–11:00, avec toutes les autres conditions satisfaites. La demande réussit ; les deux réservations sont conservées sans intervalle imposé entre elles. Vérification prévue : création du second créneau et contrôle des deux intervalles.
- [AC-20] Quatrième réservation future : un étudiant possédant trois réservations futures non annulées tente d’en créer une quatrième. Il reçoit un message compréhensible et aucune nouvelle réservation n’est créée, y compris lorsqu’une des trois porte sur un poste devenu hors service. Vérification prévue : test avec puis sans poste hors service parmi les trois réservations.
- [AC-21] Éléments exclus du quota : un étudiant possède deux réservations futures non annulées, ainsi que des réservations annulées, en cours et passées. Il réserve un nouveau créneau valide : la demande réussit et son nombre de réservations futures non annulées devient trois. Vérification prévue : jeu de données et horloge préparés, puis comptage avant/après.
- [AC-22] Concurrence sur un poste : deux étudiants admissibles demandent simultanément le même poste et le même créneau libre. Une seule demande réussit ; l’autre est refusée et une seule réservation est créée. Vérification prévue : test PostgreSQL préparé utilisant deux connexions concurrentes, distinct du conflit préexistant d’AC-17.
- [AC-23] Concurrence pour un étudiant : un étudiant admissible envoie simultanément deux demandes pour des créneaux qui se chevauchent sur deux postes libres. Une seule demande réussit ; une seule réservation est créée pour ces demandes. Vérification prévue : test PostgreSQL concurrent avec les deux demandes rattachées au même utilisateur.
- [AC-24] Concurrence sur le quota : un étudiant possédant deux réservations futures envoie simultanément deux nouvelles demandes valides et sans chevauchement. Une seule est acceptée ; son quota final reste à trois, sans quatrième réservation enregistrée. Vérification prévue : test PostgreSQL concurrent et contrôle du résultat des deux demandes.

### Final project: cancellation and history

- [AC-25] Annulation avant le début : un étudiant annule sa propre réservation strictement avant son début, y compris si le poste est hors service. L’annulation est confirmée et conservée dans l’historique ; elle cesse de bloquer le créneau et le quota. Un poste hors service reste néanmoins indisponible. Vérification prévue : cas en service/hors service, état enregistré et disponibilités recalculées.
- [AC-26] Annulation trop tardive : un étudiant tente d’annuler sa réservation exactement à son début ou après celui-ci. L’annulation est refusée avec une explication ; la réservation reste inchangée. Vérification prévue : test aux deux limites avec horloge simulée.
- [AC-27] Réservation d’un autre utilisateur : un étudiant tente directement d’annuler la réservation d’un autre utilisateur. L’opération est refusée ; ni la réservation, ni son propriétaire, ni son créneau ne sont modifiés. Vérification prévue : requête avec l’identifiant d’une réservation appartenant à un second compte.
- [AC-28] Réservations personnelles et historique : un étudiant ouvre « mes réservations » avec des réservations futures, passées et annulées préparées. Il retrouve les siennes avec leur état, dont l’indisponibilité éventuelle du poste, sans accéder à celles d’un autre étudiant. Vérification prévue : comparaison de la liste avec les propriétaires et états enregistrés ; aucune modification métier.

### Final project: model feature

- [AC-29] Liste bornée de candidats : un étudiant demande une suggestion avec trois candidats admissibles, puis avec plus de dix. Le serveur transmet respectivement les trois candidats disponibles et au maximum dix couples distincts « poste + créneau », tous conformes aux règles et filtres. Vérification prévue : inspection des appels d’un faux client ; aucune réservation créée.
- [AC-30] Aucun candidat : un étudiant demande une suggestion lorsqu’aucun candidat n’est réservable. L’interface indique cette absence ; aucun appel au modèle et aucune création de réservation n’ont lieu. Vérification prévue : compteur d’appels du faux client à zéro et données inchangées.
- [AC-31] Contenu transmis : un étudiant saisit un besoin après avoir vu l’avertissement sur les données personnelles. L’appel textuel vise gemini-3.5-flash-lite et contient le besoin et les caractéristiques utiles des candidats, sans ajout de son identité ou de son historique. Vérification prévue : inspection d’une requête capturée par le faux client ; aucune prétention de nettoyage garanti du texte libre ni de preuve d’accès réel au fournisseur.
- [AC-32] Suggestion valide : un étudiant demande une suggestion et le faux modèle retourne l’identifiant d’un candidat encore valable. L’application affiche un seul candidat, clairement présenté comme une suggestion, avec les informations issues de ses données ; aucune réservation n’est créée. Vérification prévue : réponse préparée du faux client, affichage et comptage en base.
- [AC-33] Sortie invalide ou devenue indisponible : un étudiant reçoit une sortie mal formée, un identifiant absent de la liste ou un candidat devenu indisponible avant l’affichage. L’application n’affiche pas de suggestion valide fictive, explique l’échec et conserve la sélection manuelle ; aucune réservation n’est créée. Vérification prévue : test paramétré avec faux client et changement préparé de disponibilité.
- [AC-34] Confirmation et nouvelle vérification : un étudiant confirme une suggestion affichée. Si toutes les règles sont encore satisfaites, une seule réservation est créée ; si une règle a changé entre-temps, la demande est refusée avec une explication et sans création. Vérification prévue : scénarios préparés de succès, poste occupé/hors service, quota atteint et conflit personnel, avec faux client pour la suggestion.
- [AC-35] Clé absente ou erreur du fournisseur : un étudiant demande une suggestion avec une configuration sans clé, puis avec un faux fournisseur renvoyant un quota dépassé ou une erreur. Un message explicite apparaît et la sélection manuelle reste utilisable. Aucune réservation ni relance automatique n’est produite. Vérification prévue : zéro appel sans clé ; une seule tentative simulée dans les autres cas.
- [AC-36] Budget maximal d’attente : un étudiant demande une suggestion à un faux fournisseur qui ne répond pas dans le délai. Le budget maximal d’attente de l’appel au fournisseur est de cinq secondes, sans relance automatique ni implicite. À son expiration, l’application signale l’échec et laisse la sélection manuelle disponible, sans réservation. Cela ne promet pas un affichage dans le navigateur exactement cinq secondes après le clic, indépendamment du réseau. Vérification prévue : horloge contrôlée, compteur d’appels et contrôle de l’absence de relance du client ; aucun appel réel.

### Final project: MCP and interface

- [AC-37] Catalogue des outils : un client MCP consulte le catalogue du serveur du projet. Il retrouve les deux outils du TP 1 et les quatre nouveaux outils retenus, chacun de ces quatre portant une description d’au moins vingt caractères. Vérification prévue : requête tools/list et contrôle du catalogue ; aucune modification métier.
- [AC-38] Authentification des outils du projet : un client tente d’appeler chacun des quatre nouveaux outils sans session valide. L’accès aux données du projet est refusé et aucune réservation n’est créée, annulée ou divulguée. Vérification prévue : test paramétré avec session absente puis invalide.
- [AC-39] Mêmes règles par HTTP et MCP : un utilisateur ordinaire exécute les mêmes consultations, créations et annulations par HTTP et MCP sur des données initiales identiques. Les décisions métier et effets en base sont équivalents, avec les mêmes contrôles de propriétaire, quota, horaires et conflits. Vérification prévue : tests des deux entrées et contrôle de leur appel aux services partagés.
- [AC-40] Espaces identifiables : un étudiant connecté navigue entre laboratoires, disponibilités, « mes réservations » et son espace de compte. La liaison Google se trouve dans cet espace authentifié ; le personnel dispose d’un « espace du personnel » distinct. Vérification prévue : parcours préparé avec les deux rôles ; navigation sans modification des données métier.
- [AC-41] États de l’interface : un utilisateur ouvre un écran dans les situations applicables de chargement, résultat vide, erreur et succès. Chaque situation est identifiable ; les erreurs sont compréhensibles, sans JSON brut ni trace technique, et l’IA signale son attente et son échec. Vérification prévue : scénarios préparés par écran, une vérification courte par état, avec fournisseur simulé pour l’IA.
- [AC-42] Affichage sur plusieurs largeurs : un utilisateur ouvre les écrans à 380, 768 et 1280 pixels. Le contenu reste lisible et utilisable, sans défilement horizontal ni chevauchement ; les éléments chargés réservent leur espace. Vérification prévue : test visuel préparé pour les trois largeurs ; aucune modification métier.
- [AC-43] Parcours au clavier : un étudiant réalise connexion, réservation et déconnexion au clavier seul. Les commandes sont accessibles, le focus reste visible et les champs possèdent un libellé utilisable par les technologies d’assistance. Vérification prévue : parcours clavier sur les données de démonstration ; effets métier conformes aux actions effectuées.
- [AC-44] Lisibilité et informations de page : un utilisateur consulte les écrans préparés. Les textes présentent un contraste d’au moins 4,5:1, les pages possèdent un titre et une langue appropriés, et les cibles tactiles atteignent 44 pixels. Vérification prévue : rapport d’audit préparé, avec outil de mesure du contraste nommé ; aucune modification métier.
- [AC-45] Styles cohérents : un mainteneur examine les styles de l’interface construite. Les couleurs, espacements, tailles typographiques et rayons reposent sur des jetons de style centralisés, plutôt que sur des valeurs indépendantes dispersées. Les couleurs et rayons sont un choix de conception retenu au-delà des jetons explicitement cités dans docs/UI.md. Vérification prévue : inspection ciblée des définitions et de leur utilisation ; aucune modification en base.

### Slice 1: sign-in and the laboratories list

- [AC-46] Protection de la page et de l’API : un visiteur sans session ouvre la page des laboratoires puis interroge son API. La page protégée redirige vers la connexion ; l’API répond HTTP 401 sans données des laboratoires. Les données métier restent inchangées. Vérification prévue : fenêtre privée et deux requêtes préparées sans cookie de session.
- [AC-47] Connexion locale valide et invalide : un visiteur utilise l’e-mail et le mot de passe corrects d’un compte de démonstration ; une session Django est établie et la liste protégée devient accessible. Dans une session indépendante, des identifiants incorrects produisent un refus sans session authentifiée ni nouveau compte. Vérification prévue : deux essais préparés et contrôle que le mot de passe de démonstration est stocké sous forme hachée.
- [AC-48] Liste réellement issue de la base : un étudiant connecté consulte la liste des laboratoires d’une base de démonstration dédiée et préparée pour cet essai. Après retrait d’un laboratoire de cette base puis rechargement, celui-ci disparaît ; après restauration selon la procédure préparée puis rechargement, il réapparaît. La consultation seule ne modifie pas la base. Aucune suppression n’est prévue sur une base contenant des données à conserver. Vérification prévue : procédure de démonstration contrôlant la base cible, conservant les données nécessaires à la restauration et confirmant leur rétablissement ; arrêt si la base n’est pas la base de démonstration attendue.
- [AC-49] Déconnexion effective : un utilisateur connecté se déconnecte puis tente de rouvrir la page et l’API des laboratoires. La page protégée redirige vers la connexion ; l’API répond HTTP 401 sans données des laboratoires. Réutiliser l’ancien cookie après invalidation de la session ne rétablit pas l’accès. Les données métier restent inchangées. Vérification prévue : parcours navigateur et requêtes préparées réutilisant l’ancienne session, côté page et API.

## Traceability
<!-- Filled in from Exercise 3 onward: each AC id, and the test that names it. -->

Relevé documentaire du 17 novembre 2026 sur c96aa2e : noms collectés et assertions
existantes, sans ajout d'identifiant aux tests ni modification des critères.
Les paramètres multiples abrégés dans une cellule sont des cas séparés de la
suite. Un titre portant un AC n'est pas une preuve de tout son comportement.
Les succès d'exécution viennent de la CI du SHA publié et des commandes précisées
dans `docs/LAB03_CLOSURE.md` ; cette collecte seule n'exécute pas Python.
Architecture reste personnellement à rédiger, dans la section dédiée laissée vide.

| Critère | Test réel représentatif (nom collecté ou titre Node) | Portée et preuves complémentaires |
| --- | --- | --- |
| AC-1 | Aucun test de liaison Google. | Non implémenté ; aucune validation revendiquée. |
| AC-2 | Aucun test des conditions de liaison Google. | Non implémenté. |
| AC-3 | Aucun test de connexion Google après liaison. | Non implémenté. |
| AC-4 | Aucun test d'identité Google non liée. | Non implémenté. |
| AC-5 (partiel) | `tests/test_staff_bookings.py::test_students_keep_personal_history_and_are_denied_staff_routes` ; `tests/test_staff_catalogue.py::test_student_cannot_apply_catalogue_mutations` et `test_workstation_state_rejects_student_with_valid_csrf_and_staff_without_csrf`. | Une session étudiante locale, y compris avec `is_staff` et CSRF valide, reçoit 403 sur les opérations réservées, dont le changement d'état. Rôle et données préservés. La session Google reste à vérifier. |
| AC-6 | `tests/test_staff_catalogue.py::test_catalogue_create_rename_and_reload[AC-6-AC-7-AC-8-AC-40]` ; `tests/staff_catalogue_ui.test.mjs`. | Création HTTP 201 et une seule ligne en base. Formulaire utilisé au clavier dans Edge. [Preuves](docs/STAFF_CATALOGUE.md). |
| AC-7 | `tests/test_staff_catalogue.py::test_catalogue_create_rename_and_reload` et `test_postgres_workstation_names_unique_per_laboratory`. | Création avec rattachement vérifié, conflit 409 dans le même laboratoire et acceptation du même nom ailleurs. Ajout observé dans Edge. |
| AC-8 | `tests/test_staff_catalogue.py::test_catalogue_create_rename_and_reload` ; `tests/staff_catalogue_ui.test.mjs`. | Deux renommages, noms persistants après rechargement, mêmes identifiants et rattachement. Tests PostgreSQL et parcours synthétique Edge. |
| AC-9 | `tests/test_staff_bookings.py::test_personnel_consults_two_owners_in_stable_order[AC-9-AC-40]` et autres cas AC-9 PostgreSQL ; `tests/staff_bookings_ui.test.mjs`. | Le personnel voit deux réservations de propriétaires distincts dans l'ordre prévu, et chaque étudiant voit uniquement la sienne sur son API. Comparaison des lignes avant/après. Codex a observé les deux lignes, leurs créneaux Europe/Sofia et le réessai dans Edge sur données synthétiques. [Preuves et procédure](docs/STAFF_BOOKINGS.md). |
| AC-10 | `tests/test_staff_catalogue.py::test_workstation_state_cycle_keeps_booking_and_controls_creation` ; `tests/test_workstation_state_concurrency.py` ; cas AC-10 dans les tests DOM du personnel. | La réservation reste identique en base et apparaît dans les deux historiques avec « Poste hors service ». Le créneau libre disparaît. Action et historiques observés dans Edge. |
| AC-11 | `tests/test_booking_api.py::test_creation_business_refusals[AC-11]` ; cycle HTTP et cas AC-11 de `tests/test_workstation_state_concurrency.py`. | Le POST direct sur le créneau autrement valide retourne 409 sans nouvelle réservation. PostgreSQL démontre l'attente du verrou et le refus après la désactivation. |
| AC-12 | Cycle de `tests/test_staff_catalogue.py` et tests DOM `tests/staff_catalogue_ui.test.mjs`. | La remise en service rétablit le créneau libre et garde le créneau occupé indisponible. La réservation existante reste identique. Rejeu Edge sur le même poste à 380 px CSS. |
| AC-13 | `tests/test_read_services.py::test_slots_use_sofia_hours_and_utc` (paramètres AC-13/14) ; `tests/test_booking_api.py::test_reads_real_rows_empty_and_private_history[AC-13-AC-14-AC-28]` ; titre Node `AC-13 AC-40 AC-41 catalogue opens availability, loading and safe DOM text`. | Jours/limites/futur et lecture réelle en tests directs/API. Edge : vingt créneaux observés ; week-end sans candidat IA observé seulement sur serveur isolé. Tous les états manuels n'ont pas été rejoués en navigateur. |
| AC-14 | `tests/test_booking_api.py::test_offset_input_is_returned_and_stored_as_utc[AC-14-winter-http]` et `[AC-14-summer-http]` ; titre Node `AC-14 Europe/Sofia display changes winter/summer offset without changing wire timestamps`. | Stockage/échanges UTC et conversion simulée hiver/été. Edge : horaire de novembre observé, pas d'essai estival réel. |
| AC-15 | `tests/test_booking_creation.py::test_valid_creation_owner_and_quota_exclusions[AC-15-AC-21]` ; `tests/test_booking_api.py::test_create_conflict_cancel_repeat_and_retained_row[AC-15-AC-17-AC-25-AC-28]` ; titre Node `AC-15 AC-41 explicit confirmation, CSRF, double click blocked, success refreshes without reload`. | Création/acteur/une ligne, API et DOM. Edge et sonde HTTP réelle : 201, propriétaire et ligne comparés ; SLICE2_FINALIZATION. |
| AC-16 | `tests/test_booking_creation.py::test_invalid_slots_leave_rows_unchanged`, `test_start_is_strictly_future` (paramètres AC-16) ; `tests/test_booking_api.py::test_invalid_payload_and_temporal_rules` (AC-15/16). | Refus de forme/horaires/futur sans mutation, horloge contrôlée. Pas de tous ces scénarios en navigateur. |
| AC-17 | `tests/test_booking_creation.py::test_existing_conflicts[AC-17-station]` ; `tests/test_booking_api.py::test_create_conflict_cancel_repeat_and_retained_row[AC-15-AC-17-AC-25-AC-28]`. | Conflit préexistant distinct de la concurrence. Sonde HTTP réelle Edge : 409 et toutes les lignes inchangées ; rendu du refus testé en DOM. |
| AC-18 | `tests/test_booking_creation.py::test_existing_conflicts[AC-18-personal]` et `[AC-18-other-lab]` ; `tests/test_booking_api.py::test_creation_business_refusals[AC-18]`. | Conflit personnel même/autre laboratoire, refus sans mutation. Pas de parcours navigateur de ce refus. |
| AC-19 | `tests/test_booking_creation.py::test_consecutive_slots_allowed[AC-19-before]` et `[AC-19-after]` ; `tests/test_booking_models.py::test_consecutive_half_open_intervals_are_allowed[AC-19-schema]`. | Preuves directes et contraintes PostgreSQL [début, fin). Ne pas revendiquer un essai HTTP ou navigateur spécifique de ces deux créations consécutives. |
| AC-20 | `tests/test_booking_creation.py::test_fourth_future_booking_is_refused[AC-20-online]` et cas hors service ; `tests/test_booking_api.py::test_creation_business_refusals[AC-20]`. | Quota, HTTP 409 et absence de mutation. DOM du message ; concurrence sous AC-24 ; pas d'essai manuel dédié. |
| AC-21 | `tests/test_booking_creation.py::test_valid_creation_owner_and_quota_exclusions[AC-15-AC-21]` ; `tests/test_read_services.py::test_quota_counts_future_offline_post_but_not_cancelled_or_current[AC-20-AC-21-read]`. | Passé/en cours/annulé exclus, réservation future hors service incluse. Preuve de service, pas de parcours navigateur dédié. |
| AC-22 | `tests/test_booking_concurrency.py::test_concurrent_creation[AC-22]`. | Deux backends PostgreSQL distincts, attente du verrou constatée ; un succès, WorkstationConflict, une ligne. Guide CONCURRENCY_2C ; pas une concurrence HTTP/MCP nouvellement testée. |
| AC-23 | `tests/test_booking_concurrency.py::test_concurrent_creation[AC-23]`. | Même acteur, postes différents, attente PostgreSQL prouvée ; un succès, PersonalConflict, une ligne. |
| AC-24 | `tests/test_booking_concurrency.py::test_concurrent_creation[AC-24]`. | Deux réservations initiales, demandes distinctes sans conflit temporel ; un succès, QuotaExceeded, total trois. Mutation temporaire du quota détectée au jalon 2C, code restauré ; pas rejouée ici. |
| AC-25 | `tests/test_booking_cancellation.py::test_valid_cancellation_keeps_row_and_history` (AC-25/28, poste en/hors service) et `test_repeat_after_start_preserves_timestamp_and_does_not_read_clock` ; `tests/test_booking_api.py::test_create_conflict_cancel_repeat_and_retained_row`. | Propriétaire, annulation conservée, répétition sans nouvelle mutation ; tests concurrents séparés dans test_cancellation_concurrency. Edge : ligne Annulée conservée ; sonde réelle 200, seul cancelled_at changé. Répétition non rejouée manuellement. |
| AC-26 | `tests/test_booking_cancellation.py::test_first_cancellation_at_or_after_start_is_refused[AC-26-exact-start]` et `[AC-26-after-start]` ; `tests/test_booking_api.py::test_cancellation_refusals[AC-26]`. | Refus temporel sans mutation et DOM du message ; pas de preuve navigateur de chaque borne. |
| AC-27 | `tests/test_booking_cancellation.py::test_refusals_leave_all_business_rows_unchanged` (cas propriétaire) ; `tests/test_booking_api.py::test_cancellation_refusals[AC-27]` et `[AC-27-repeat]`. | 403 métier, y compris ligne annulée ; sonde réelle avec CSRF valide et autre propriétaire : 403, tous les champs inchangés. Cas déjà annulé seulement automatisé. |
| AC-28 | `tests/test_read_services.py::test_personal_history_has_all_states_order_and_no_foreign_rows` ; `tests/test_booking_api.py::test_reads_real_rows_empty_and_private_history[AC-13-AC-14-AC-28]` ; titre Node `AC-25 AC-28 history empty/future/past/cancelled and cancellation refresh`. | Historique privé, quatre états, ordre et état actuel du poste en tests. Edge : vide → À venir → Annulée ; autres états/absence de fuite pas tous observés manuellement. |
| AC-29 | `tests/test_ai_suggestion.py::test_bound_order_and_payload` et `test_duplicates_and_changed_top_ten` (paramètres AC-29/33). | Trois candidats puis plafond dix, déterminisme/dédoublonnage/filtres, absence de mutation. Faux client exclusivement ; aucun accès ou qualité Google prouvé. |
| AC-30 | `tests/test_ai_suggestion.py::test_empty_means_zero_calls[AC-30-empty]` ; `tests/test_ai_suggestion_api.py::test_no_candidates_no_invocation[AC-30-API-empty]` ; titre Node `AC-30 genuine empty response and invalid responses never become AI success`. | Zéro candidat, zéro appel au client et message. Edge isolé : samedi sans candidat ; pas un fournisseur réel. |
| AC-31 | `tests/test_ai_suggestion.py::test_only_application_fields_and_no_identity[AC-31-payload-AC-32-application-values]` ; `tests/test_gemini_adapter.py::test_one_rest_request_has_only_minimal_inputs[AC-31-REST-AC-32-structured]` ; titre Node `AC-29 AC-31 need validation and explicit action only`. | Payload minimal inspecté, avertissement présent avant envoi et observé dans Edge. Texte libre non garanti anonyme. Aucun envoi réel Google. |
| AC-32 | `tests/test_ai_suggestion_api.py::test_success_uses_real_service_without_booking[AC-29-AC-31-AC-32-API]` ; titre Node `AC-32 AC-34 loading, one request, safe suggestion and explicit existing confirmation`. | Réponse construite depuis les données applicatives, texte sûr et aucune création avant clic. Edge isolé : suggestion factice et historique vide avant confirmation. |
| AC-33 | `tests/test_ai_suggestion.py::test_reject_untrusted_response`, `test_recheck_after_client` (AC-33) ; `tests/test_ai_suggestion_api.py::test_stale_candidate_is_not_success` ; titres Node `AC-33 stale response ignored after laboratory/date/need/manual/refresh` (cinq tests). | Forme/type/appartenance, disponibilité relue, contexte obsolète ignoré. Edge isolé : sortie invalide ; pas de réponse Google réelle. |
| AC-34 | `tests/test_ai_confirmation.py::test_confirmation_rechecks_current_rules[AC-34-suggestion-confirm-none/occupied/offline/quota/personal]` (cinq paramètres séparés) ; tests DOM de confirmation ci-dessus. | Suggestion sans mutation puis création existante : succès ou refus selon les données actuelles. Edge isolé : une entrée À venir après clic ; aucune création de démonstration conservée lors de cet essai IA. |
| AC-35 | `tests/test_ai_suggestion.py::test_absent_client`, `test_errors_are_safe_and_never_retried` ; `tests/test_ai_suggestion_api.py::test_real_configuration_with_missing_key_does_not_spawn` ; tests Node `AC-33 AC-35 AC-36 readable ...`. | Erreurs/clé synthétique absente, zéro retry et manuel disponible. Edge normal : désactivé/non configuré puis sélection manuelle ; Edge isolé : quota/session révoquée. Pas de clé réelle. |
| AC-36 | `tests/test_gemini_adapter.py::test_real_process_is_bounded_and_reaped` (AC-35/36) ; `tests/test_ai_suggestion.py::test_late_response_is_not_suggested` ; `tests/test_ai_suggestion_api.py::test_wait_is_outside_request_transaction`. | Deadline/processus locaux et nettoyage mesurés à la sous-étape 2. Edge isolé : message de dépassement simulé. Ni temps Google ni délai exact d'affichage navigateur prouvé. |
| AC-37 | `tests/test_mcp_mutations.py::test_AC_37_six_tools_and_mutation_schemas[AC-37]` ; `tests/test_mcp_reads.py::test_AC_37_AC_39_read_catalog_and_personal_history[AC-37-AC-39]`. | Vrai stdio : découverte, schémas et descriptions ; six outils en mode projet, deux TP1 en mode autonome. Client Gemini final : appels non validés. |
| AC-38 | `tests/test_mcp_session_auth.py::test_refuse_missing_or_unknown_session`, `test_refuse_invalidated_session_without_writing` ; `tests/test_mcp_mutations.py::test_AC_38_revocation_blocks_both_mutations_in_same_process`. | Sessions Django de test, expiration/révocation/inactivité/hash ; nouvel acteur à chaque appel. Remise réelle d'un jeton utilisateur au client final non validée. |
| AC-39 | `tests/test_mcp_mutations.py::test_AC_11_AC_15_AC_17_AC_18_AC_20_AC_39_creation_parity` et `test_AC_25_AC_26_AC_27_AC_28_AC_39_cancellation_parity` ; `tests/test_mcp_reads.py::test_AC_37_AC_39_read_catalog_and_personal_history`. | Vrais processus stdio, services identiques, 14 créations/8 annulations et lectures comparées HTTP/MCP, CSRF côté HTTP, aucune mutation sur refus. Ne prouve pas tous les scénarios ni le client final. |
| AC-40 (partiel) | `tests/test_booking_page.py::test_student_journey_template_keeps_session_csrf_and_navigation` ; `tests/test_staff_bookings.py::test_personnel_consults_two_owners_in_stable_order` ; `tests/test_staff_catalogue.py::test_catalogue_create_rename_and_reload`. | La navigation du personnel mène à « Réservations » et à « Catalogue ». Visibilité et accès contrôlés par le rôle. L'espace de compte et la liaison Google restent ouverts. |
| AC-41 | Titres Node de chargement/vide/erreur/succès dans booking_ui, labs_ui et ai_suggestion_ui ; notamment `AC-41 read network errors offer retries, no raw stack`. | DOM simulé et observations Edge répertoriées dans AI_UI_3/SLICE2_FINALIZATION. Tous les écrans et états du projet final ne sont pas présents ni audités. |
| AC-42 (partiel) | Le test Python vérifie le HTML et son accès. Codex a mesuré 380/768/1280 px CSS dans Edge sur la connexion, le parcours étudiant, les réservations du personnel et son catalogue. | Aucun débordement horizontal dans les scénarios mesurés. Les trois déplacements mesurés à 0 px concernent le parcours étudiant. Données synthétiques et limites dans [UI.md](docs/UI.md). Les autres états et écrans finaux restent ouverts. |
| AC-43 | `tests/test_booking_page.py::test_student_journey_template_keeps_session_csrf_and_navigation[AC-40-AC-41-AC-42-AC-43]` vérifie les libellés, la navigation et les commandes ; parcours Codex complet dans Edge sur PostgreSQL de test (UI.md). | Connexion → date/créneau → confirmation → historique actif puis annulé → déconnexion, au clavier seul, avec focus visible. La liste a évolué 10 → 9 → 10. Preuve du parcours étudiant préparé, distincte de la compréhension personnelle de l'étudiant. |
| AC-44 (partiel) | `tests/style_tokens.test.mjs` calcule les contrastes de la palette et vérifie les minimums CSS de 44 px ; Edge DevTools et Console : connexion et trois écrans livrés, états de lecture réels ou simulés, zoom navigateur réel 200 %, cibles visibles mesurées (UI.md). | Titre/langue et principaux contrastes relevés ; aucun débordement horizontal ni cible visible sous 44 CSS px dans les états mesurés. Les sous-commandes natives, certains états de mutation et les futurs écrans Google/compte restent hors preuve. |
| AC-45 | `tests/style_tokens.test.mjs` vérifie les jetons définis, leurs références et l'absence de valeurs dispersées pour couleurs, espacements, typographie et rayons. | `app.css` est le seul CSS applicatif ; `h2` utilise `--text-section`. Rendu des titres revu dans Edge durant le parcours étudiant. Les dimensions fixes des régions de résultats et des cibles ont une fonction explicite. |
| AC-46 | `tests/test_access.py::test_AC_46_anonymous_page_redirects_to_login` ; `tests/test_labs.py::test_api_refuses_without_html_redirect` ; `tests/test_booking_api.py::test_session_required_for_all_routes_including_csrf_valid_posts`. | Redirection page / JSON 401 API, sessions absentes/invalides/expirées/inactives ; sonde HTTP anonyme réelle 401. Texte utilisateur seul après déconnexion n'apporte pas le statut. |
| AC-47 | `tests/test_auth.py::test_AC_47_valid_login_creates_session_and_preserves_account`, `test_AC_47_generic_refusal_without_changes`, `test_AC_47_csrf_refusal_with_real_middleware`. | Mots de passe Django, connexion/refus uniformes, CSRF et redirections internes ; observations utilisateur du point 2 conservées distinctement. |
| AC-48 | `tests/test_labs.py`, `tests/test_demo_labs.py::test_backup_withdraw_restore_preserves_accounts_and_other_rows[AC-48-demo]` ; titre Node `AC-48 loading then real names rendered as text with same-origin session`. | Django/DOM isolés et preuve Edge réelle 3 → 2 → 3, Beta restauré à l'identique ; CHECKPOINT3. Pas de nouvelle manipulation de la base. |
| AC-49 | `tests/test_logout.py::test_AC_49_logout_invalidates_server_session_and_old_cookie`, `test_AC_49_logout_requires_post_and_valid_csrf` ; tests de refus API après déconnexion. | Session serveur invalidée, ancien cookie refusé, données métier conservées. Observations utilisateur et sondes HTTP réelles séparées des tests. |

Ces preuves automatisées sont distinctes de la démonstration navigateur. Après la construction et sur autorisation explicite de l’utilisateur, Codex a réalisé le retrait/restauration de Beta sur la base de démonstration selon CHECKPOINT3.md : **3 → 2 → 3** observé dans Edge, puis comparaison confirmant sa restauration exacte. Cette observation est détaillée ci-dessous ; elle n’est pas attribuée à l’utilisateur.

## Spec vs result
<!-- After the agent builds the slice: which criteria passed, which it missed or reinterpreted, and what you changed in this spec because of it. -->

Le cycle hors service et remise en service couvre AC-10 à AC-12. L'action
envoie l'état souhaité et le changement se coordonne avec la création d'une
réservation sur le verrou du poste. Les preuves PostgreSQL et le parcours
Edge à 380 px CSS sont distinctes. [Rejouer et vérifier le cycle](docs/STAFF_CATALOGUE.md#changer-létat-dun-poste)

Le catalogue réalise AC-6 à AC-8. La preuve Edge couvre quatre écritures puis
rechargement à 380, 768 et 1 280 px CSS sur données isolées. Les tests PostgreSQL
vérifient le rôle, le CSRF, le rattachement et l'unicité par laboratoire.
[Détail des preuves](docs/STAFF_CATALOGUE.md). AC-5, AC-40 et AC-42 restent partiels.

La consultation en lecture seule du personnel est livrée pour AC-9. Les
preuves PostgreSQL, DOM et Edge sont détaillées dans [STAFF_BOOKINGS.md](docs/STAFF_BOOKINGS.md).
Les contributions à AC-5, AC-40 et AC-42 restent partielles.

Le 19 novembre 2026, Codex a réalisé le contrôle à 380 px auparavant reporté et
vérifié aussi 768 et 1280 px dans Edge sur les deux écrans livrés. Les trois
listes du parcours étudiant disposent désormais d'une réserve d'espace au
chargement. Parcours manuel et repli IA désactivé observés à 380. Le relevé
[UI.md](docs/UI.md) précise les scénarios, les mesures et les limites d'AC-42.

Finalisation IA, 17 novembre 2026 : trois commits de sous-étapes conservés ;
couverture CI JavaScript étendue au fichier de tests IA existant, sans changement
de seuil, exclusion ou fonctionnalité. ex3 inchangé : 15/18 (sortie 1), défaut
npm Windows, traçabilité des critères futurs/UI et note personnelle manquante.
Bilan courant : `docs/AI_FINALIZATION.md`, qui distingue faux fournisseur,
adaptateur désactivé observé dans Edge, Google réel non essayé, client MCP final
et remise réelle non validés, note/revue personnelles et UI reportées.
La publication de la tranche ne constitue pas une clôture du Lab 03.

IA sous-étape 3, 17 novembre 2026 : interface facultative sur /labs construite
par Codex sur décisions utilisateur. Besoin trim 1–1 000, avertissement avant
envoi, action explicite, anti-double soumission, invalidation besoin/date/labo,
réponses obsolètes ignorées, affichage texte et confirmation existante réutilisée.
19 nouveaux tests DOM d'abord rouges, puis 42 tests Node réussis ; 5 tests HTTP
PostgreSQL supplémentaires vérifient la confirmation et les refus sans mutation.
Couverture PostgreSQL : 545 réussis/1 garde SQLite désélectionné, 9 TP1 ; services
322/322 lignes et 108/108 branches, global 1 765/1 865 lignes (94,64 %), sans
nouvelle exclusion. Couverture des modules JS chargés : 97,71 % lignes.
Codex a observé dans Edge le repli désactivé sur le serveur de développement,
20 choix manuels puis le panneau de confirmation sans soumission. Sur le seul
serveur isolé de test avec faux client : succès, historique vide avant clic,
confirmation puis une réservation À venir, délai/quota/réponse invalide simulés,
aucun candidat et session de test révoquée. Détails et limites : AI_UI_3.md.
Aucune requête Google, aucun usage autorisé/compte fournisseur validé ; ni délai
navigateur exact, ni conformité mobile/accessibilité complète déduits de ces
preuves. Note personnelle et 380 pixels restent reportés ; Lab 03 non clos.
Les paragraphes des étapes 1–2 ci-dessous sont des comptes rendus historiques.

IA sous-étape 2, 17 novembre 2026 : API protégée et adaptateur REST borné livrés,
désactivés par défaut, sans clé réelle ni appel Google. Tests ciblés 129 réussis ;
régression PostgreSQL 540 réussis/1 garde SQLite désélectionné et réussi à part,
puis 9 tests TP1. Services 322/322 lignes et 108/108 branches ; global Python
1 765/1 865 lignes (94,64 %), TP1 et intégrations inclus, périmètre inchangé.
Processus locaux contrôlés : 13 cas terminés/reapés, dont blocage et nettoyage
retardé, maximum observé 4,763058 s dans le relevé final (budget 5 s, tolérance
d'assertion 350 ms non ajoutée au budget). Les contrôles Node23/MCP12/ex232
réussissent. Aucun rendu IA, réseau Google, statut du compte fournisseur ou
conformité de mise à disposition EEE n'est déduit de ces preuves. Détails :
`docs/AI_TRANSPORT_2.md`. AC-34 et les parties UI restent à construire/vérifier ;
note personnelle et 380 pixels restent reportés. Aucun push pour ce jalon.

IA sous-étape 1, 17 novembre 2026 : 51 tests directs avec faux client réussis ;
régression PostgreSQL 462 réussis/1 garde SQLite désélectionné puis réussi
séparément ; 9 tests TP1 et 23 Node réussis. Couverture locale PostgreSQL :
services 319/319 lignes et 108/108 branches ; global Python 1 532/1 618 lignes
(94,68 %), TP1 inclus, seuils/inventaire inchangés. Le service ne crée ni n'annule,
ne fait aucun appel réel et ne prouve aucun rendu navigateur ni délai réseau.
AC-29 concerne ici le service ; AC-30 à AC-33/35/36 restent partiels, AC-34 IA
reste en attente. Aucune nouvelle observation UI, note personnelle ou validation
Google n'est ajoutée. Méthodes, erreurs d'environnement et limites : AI_SERVICE_1.

Complément HTTP du 12 novembre 2026 : l'utilisateur reporte la note et la revue
personnelles ; aucune compréhension n'est déclarée validée. Codex a observé
GET /api/bookings sans cookie sur le serveur PostgreSQL réel : HTTP 401, uniquement
{"error": "Connexion requise."}, deux réservations avant/après, tous leurs champs
inchangés. Preuve complémentaire de la protection de l'historique, pas une nouvelle
preuve complète d'AC-46/49 qui portent sur les laboratoires. Le compte étudiant
secondaire autorisé est créé sans privilèges ; sa préparation de mot de passe et
sa connexion ont été confirmées par l'utilisateur. Codex a ensuite observé dans
les sessions Edge réelles : POST /api/bookings : 201 (ligne 3, propriétaire id 2,
total 2 → 3), rejeu : 409 (3 → 3, tous champs identiques), puis POST /api/bookings/3/cancel
depuis student-ui : 403 métier de propriété (3 → 3, tous champs identiques), avec
CSRF de chaque session, sans exposer sa valeur. Les POST anonymes munis d'un CSRF
valide ont aussi donné 401. Annulation finale par le propriétaire : 200 ; seul
cancelled_at de la nouvelle ligne change ; trois lignes conservées. Après
rechargement, historique du second étudiant : une entrée Annulée. Ces observations
ne sont pas déduites des tests automatisés. Voir docs/SLICE2_FINALIZATION.md.

Finalisation Slice 2, 12 novembre 2026 : le regroupement AC-11/13–28 ci-dessus
fait autorité ; les mentions « regroupement ouvert » dans les bilans historiques
des jalons antérieurs décrivent leur état à cette date. Le parcours Edge a été
complété pour la partie réservation/annulation au clavier, le focus, l'erreur
réseau avec réessai et la mesure de palette/contraste. Aucun comportement métier
modifié pour cette finalisation. 380 pixels reste reporté ; note personnelle et
exigences IA/MCP du TP3 restent ouvertes. Les statuts HTTP demandés ont été
complétés par les observations ci-dessus. Voir docs/SLICE2_FINALIZATION.md pour les sources actuelles,
les limites de l'ex3 et les preuves locales/distantes distinctes.

Publication initiale Slice 2 : 2011d95d6d711dd0ee84d60af7eb2135801ae9de sur
origin/main par push normal, historique conservé. Les quatre jobs du run
43262915943 ont réussi ; bases PostgreSQL éphémères vides puis migrations,
tests concurrents et couverture réellement exécutés. Python global Linux :
1207/1283 lignes (94,08 %), services 220/220 lignes et 74/74 branches. L'ex3
Windows reste à 11/18 et la note personnelle reste à écrire ; ce résultat CI
ne valide pas les exigences manquantes du TP3/projet ni le contrôle à 380 pixels.

Jalon 4, 11 novembre 2026 : parcours étudiant construit sur /labs, API et services
inchangés. Confirmation explicite avant création, historique et annulation,
rafraîchissement sans rechargement, fuseau Europe/Sofia, états et erreurs textuels,
aucune relance automatique d'une mutation incertaine. Preuves automatisées et
limites : docs/STUDENT_UI_4.md. Démonstration PostgreSQL préparée une fois sur
autorisation supplémentaire (un étudiant sans privilèges, un laboratoire, deux
postes), sans transfert SQLite ni changement d'un compte existant. Mot de passe
et connexion effectués par l'utilisateur selon son retour. Le 12 novembre 2026,
Codex a observé dans Edge le laboratoire dédié et l'historique vide, puis les
20 créneaux du 13 novembre. Choix du poste A, 08:00–09:00 Europe/Sofia : un
écran de confirmation précède la création. Après confirmation, succès visible,
une réservation « À venir » dans l'historique et 18 créneaux disponibles.
Après annulation, la même entrée reste « Annulée » et 20 créneaux sont proposés,
sans rechargement manuel. Aucun statut HTTP n'a été relevé dans ce parcours
navigateur. Les captures affichées par l'outil ne sont pas archivées au dépôt.
Ces observations ne valident pas les refus, tous les états ou l'accessibilité.
Clavier complet, contraste et largeurs restent à vérifier ; 380 pixels reporté.

Jalon 3, 11 novembre 2026 : quatre contrats HTTP exposés par trois vues, services
existants inchangés. Tests d'intégration PostgreSQL avec sessions/CSRF réels,
propriétaire de session uniquement, codes et JSON explicites, contrôles des lignes
finales et refus sans mutation. Le CSRF des nouvelles routes est JSON sans
changer les formulaires HTML. Aucune interface ni preuve navigateur ajoutée,
aucun compte/donnée de démonstration créé. Guide : docs/HTTP_API_3.md.
Le regroupement définitif Slice 2 et la note d'architecture personnelle restent
à valider/rédiger par l'étudiant ; aucune formulation personnelle n'est présumée.

Jalon 2D, 11 novembre 2026 : service d'annulation propriétaire construit et testé
directement sur PostgreSQL. Authentification active et propriété précèdent le
retour idempotent ; première annulation strictement avant le début, ligne et
timestamp conservés. Tests concurrents : une seule transition pour deux
annulations ; création/annulation sur quota ou même poste respectent les deux
ordres contrôlés. Aucun endpoint ni HTTP 200 implémenté. Ces preuves ne couvrent
pas tous les entrelacements ni les parcours navigateur. Détails et mesures :
docs/CANCELLATION_2D.md. Regroupement définitif Slice 2 toujours ouvert.

Jalon 2C, 11 novembre 2026 : les trois scénarios directs AC-22/23/24 ont réussi
sur la seule base PostgreSQL de test dédiée, avec connexions distinctes et
attente de verrou constatée côté serveur. Le test quota échoue avec quatre
réservations lorsque le contrôle est neutralisé temporairement ; le service
est ensuite restauré exactement. Aucun correctif de production nécessaire.
Ces preuves ne couvrent pas tous les entrelacements, les futurs parcours HTTP,
l'annulation ou un autre niveau d'isolation. Détails : docs/CONCURRENCY_2C.md.
Regroupement définitif Slice 2 et note d'architecture personnelle restent ouverts.

Jalon 2B, 11 novembre 2026 : création directement testée sur PostgreSQL, acteur
étudiant actif relu sous verrou, propriétaire imposé par l'acteur. Transaction,
verrous utilisateur puis poste, heure relue après acquisition, règles et quota
revérifiés ; contraintes connues traduites après rollback, autres erreurs de base
propagées. Tests directs sans HTTP ni interface, sans essai à connexions
concurrentes : AC-22/23/24 restent à vérifier en 2C. Les AC ci-dessus restent
partiels ; aucun résultat concurrent ou distant n'est inféré. Résultats et
limites : docs/CREATION_2B.md. Regroupement définitif Slice 2 encore ouvert.

Jalon 2A, 11 novembre 2026 : disponibilités et historique personnel sont testés
directement sur PostgreSQL, avec horloge contrôlée et sans mutation. Les lectures
filtrent horaires, poste, conflits personnels et quota global ; elles ne garantissent
pas la disponibilité lors d'une future création. AC-13/14/28 restent partiels
sans parcours HTTP ou écran. Résultats : docs/READ_SERVICES_2A.md.

Jalon 1B, 11 novembre 2026 : schéma PostgreSQL et contraintes testés séparément
des services. La chaîne complète est appliquée sur une base de vérification vide ;
les références, exclusions et intervalles sont testés sur PostgreSQL isolé.
Les correspondances AC ci-dessus restent partielles. Aucun quota, permission
métier, traitement HTTP ou scénario concurrent n'est déclaré vérifié. Résultats
et limites : docs/POSTGRES_1B.md. La CI historique n'est pas adaptée à ce moteur.

Bilan factuel au 4 novembre 2026, après la correction de l’affichage et la démonstration AC-48 :

- Automatisé : la finalisation a relancé la mesure complète sur le code existant : **105 tests pytest, 9 tests TP1 et 7 tests JavaScript réussis**. Services Python : 25/25 lignes et 4/4 branches ; global Python : 587/642 lignes (91,43 %), serveur TP1 inclus ; branches globales : 151/172 (87,79 %). Le module JavaScript chargé par les tests atteint 97,26 % des lignes, sans prétendre couvrir tout le frontend. Les contrôles Django et de dérive des migrations réussissent, ainsi que 12/12 contrôles MCP. Le test de revalidation ajouté précédemment échouait avant la correction du template (304 au lieu de 200) ; cette preuve reste dans CHECKPOINT3.md. Commandes et rapport actualisé : docs/TP2_FINALIZATION.md. Ces chiffres ne remplacent pas les observations navigateur ci-dessous.
- Observations utilisateur reçues : vérifications du socle et préparation personnelle des mots de passe ; affichage de la connexion et du message d’erreur ; accès connecté à Laboratoires ; redirection vers /login?next=/labs sans session ; connexion/déconnexion au clavier avec focus visible. Elles ne constituent pas une validation de compréhension ni de l’ensemble du projet.
- Retour utilisateur du point 3 : connexion et contenu de la page présents, mais liste et messages absents même après rechargement complet ; consultation directe de l’API authentifiée avec les trois laboratoires reçus. Codex a confirmé dans Edge le refus MIME de labs.mjs (text/plain), également observé sur la réponse HTTP réelle. La configuration déclare désormais ce module en text/javascript, sans modifier les règles fonctionnelles.
- Reprise sur l’instance réelle : après le nouveau signalement utilisateur, Codex a identifié le serveur de ce dépôt sur 8000. Edge revalidait l’ancienne URL du module avec une réponse 304 et gardait text/plain ; aucune requête API ne partait. Le template utilise maintenant labs.mjs?v=2. Après redémarrage ciblé et rechargement normal dans le même onglet connecté, Codex a observé le module en 200, le fetch vers /api/labs en 200 et les trois laboratoires Alpha, Beta et Gamma visibles, avec « 3 laboratoire(s) affiché(s). ». Ce sont des observations du navigateur par Codex, pas une validation supplémentaire rapportée par l’utilisateur.
- Nouveau retour utilisateur : après déconnexion, `/api/labs` affiche `{"error": "Connexion requise."}`, sans laboratoire. Le statut HTTP n’a pas été relevé ; ce seul affichage ne prouve pas le statut 401, vérifié séparément par les tests automatisés.
- Démonstration navigateur AC-48 par Codex : avant toute mutation, `/labs` connecté affichait Alpha, Beta, Gamma. La base marquée `data/demo.sqlite3` et Beta (id 2) ont été identifiés ; `data/demo-lab-2-ac48-20261104.json` a été créé et vérifié avant retrait, avec tous les champs actuels (id/name). Aucune relation entrante ni aucun déclencheur de la table n’a été trouvé. Après retrait de Beta seul et rechargement, Alpha et Gamma étaient visibles, avec le compteur 2. Après restauration immédiate et rechargement, les trois noms étaient visibles dans l’ordre initial, avec le compteur 3. La comparaison finale avec la sauvegarde confirme Beta identique sur tous les champs et le catalogue initial rétabli. Ce scénario manuel AC-48 est réussi ; aucun compte, mot de passe, rôle ou migration n’a été modifié et la session existante est conservée. Les tests isolés antérieurs couvrent séparément la consultation sans mutation et la liste vide ; aucun test fonctionnel n’a été relancé pour cette étape sans modification de code.
- Limites : le statut HTTP de l’API après déconnexion n’a pas été confirmé manuellement dans le dernier retour utilisateur. La tranche entière n’est pas déclarée vérifiée manuellement ; aucune validation de compréhension ou approbation du professeur n’est déduite de la démonstration.
- Contrôle à 380 pixels : reporté explicitement par l’utilisateur, non effectué et non bloquant pour cette étape ; conformité mobile non validée.
- Adaptations concrètes : sauvegarde AC-48 séparée du retrait pour disposer du fichier de restauration avant toute suppression ; réponse de l’API limitée à id/name dans l’ordre des identifiants ; aucun catalogue de secours fictif. Aucune modification des objectifs ou seuils. La CI utilise le même lanceur Python, les dépendances déclarées, les tests JavaScript et les contrôles MCP/spécification conservés. La couverture du projet multilangage et la conformité mobile ne sont pas déclarées validées par le seul rapport Python.
- Publication et preuve distante : le commit de livraison `4243d717716142b45ab8304abf21c2056f28fdb7` a été poussé normalement sur origin/main. Son [exécution GitHub Actions](https://github.com/phillipe-BAGUEKA/webdev-phillipe-bagueka-erasmus/actions/runs/41758283141) réussit les quatre jobs test/coverage/mcp/spec : 105 tests pytest, 9 tests TP1, 7 tests JavaScript, 12/12 contrôles MCP, 32/32 contrôles de spécification. Couverture réellement mesurée sur Ubuntu : services 25/25 lignes et 4/4 branches ; global 587/642 lignes (91,43 %) et 151/172 branches (87,79 %) ; TP1 inclus, labs.mjs 97,26 % des lignes. Seule l’étape Docker est ignorée par sa condition existante, faute de Dockerfile. Aucun correctif CI ni seuil affaibli n’a été nécessaire. Cette preuve est liée à ce SHA précis ; elle ne remplace ni la vérification d’un commit suivant ni les essais manuels reportés.
