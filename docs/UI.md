# UI checklist

<!-- Exercise 4 hands this in. Tick an item only when you have checked it, and replace
     the "how I checked" line with what you actually did. An unticked box is not a
     failure: it is a gap you then write into READINESS.md. A ticked box you cannot
     demonstrate at the defence is worse than an unticked one. -->

"Modern" is not a style. It is a short list of things a user notices when they are
missing: the screen tells you what is happening, you can get through it with a keyboard,
the text is readable, and nothing jumps around while it loads.

## Layout and typography

- [ ] **One spacing scale and one type scale.** Sizes come from a small set of design tokens, not from numbers typed where they were needed.
  - how I checked:
- [ ] **Responsive at 380, 768 and 1280 pixels wide.** No horizontal scrollbar, no text running under another element.
  - how I checked: 19 novembre 2026, Codex dans Edge. Connexion et parcours
    étudiant vérifiés aux trois largeurs CSS. Périmètre et mesures ci-dessous.
- [ ] **Nothing jumps while the page loads.** Images and cards reserve their space before their content arrives.
  - how I checked:

## The four states, on every screen

A screen that only handles "it worked" is a screen that lies to the user on the day it matters.

- [ ] **Loading.** Something tells the user the app is working, within about 100 ms.
  - how I checked:
- [ ] **Empty.** The screen says what this list is for and what to do next, instead of showing nothing.
  - how I checked:
- [ ] **Error.** A sentence a person can read. Never a raw JSON body, never a stack trace, never just "Error".
  - how I checked:
- [ ] **Success.** The user can see that what they did took effect, without reloading the page to find out.
  - how I checked:

## Keyboard and accessibility

- [ ] **The main flow works with the keyboard alone.** Sign in, do the core action, sign out, without touching the mouse.
  - how I checked:
- [ ] **The focused element is visible.** A `:focus-visible` outline that is not switched off.
  - how I checked:
- [ ] **Text contrast is at least 4.5:1.** Name the tool you measured with.
  - how I checked: 12 novembre 2026, Codex : Edge DevTools CSS overview sur /labs,
    puis calcul WCAG 2 en Python. Palette applicative mesurée de 7,463:1 à
    15,520:1 ; associations et limites dans SLICE2_FINALIZATION.md. La case globale
    reste ouverte pour les autres écrans/états et contrôles natifs.
- [ ] **Every input has a label** a screen reader reads, not just placeholder text.
  - how I checked:
- [ ] **The page has a correct `<title>` and `lang`.**
  - how I checked:
- [ ] **Touch targets are at least 44 pixels.**
  - how I checked:

## The model feature

- [ ] **It shows that it is thinking.** A model call is slow and a free service may have been asleep; a frozen button is the worst possible answer.
  - how I checked:
- [ ] **It shows when it failed,** and the rest of the screen still works.
  - how I checked:
- [ ] **The user can tell the model's suggestion from a fact.** It is labelled as a suggestion, not presented as data the app knows.
  - how I checked:

## Decisions

- [ ] **Dark mode, or a written decision not to have one.**
  - what I decided and why:

## Evidence

Jalon 4 : interface sur /labs, tests dans tests/booking_ui.test.mjs et
tests/test_booking_page.py. Il s'agit de DOM/réseau simulé et d'intégration
Django, pas d'une validation visuelle ou clavier. Guide : STUDENT_UI_4.md.
Les cases restent non cochées tant que leurs vérifications réelles ne sont pas
effectuées ; 380 pixels explicitement reporté. Démo PostgreSQL préparée sur
autorisation supplémentaire. Le 12 novembre 2026, Codex a observé dans Edge
le choix d'un créneau, sa confirmation, son ajout à l'historique puis son état
Annulée conservé, avec actualisation sans rechargement manuel. Ce parcours ne
valide pas tous les états, le clavier complet, le contraste ou les largeurs.
Aucune capture n'est archivée ; 380 pixels reste reporté.

Finalisation du 12 novembre : Codex a observé la réservation et l'annulation
au clavier, le contour de focus, une erreur réseau simulée puis le réessai
HTTP 200. Pas de nouvel essai unique connexion/action/déconnexion ; observations
utilisateur TP2 conservées séparément. Les mesures de palette ci-dessus ne
valident pas les largeurs ni tous les aspects d'accessibilité. Guide détaillé :
SLICE2_FINALIZATION.md. Les anciennes limites du jalon 4 sont historiques.

<!-- Screenshots of at least the four states of one screen, and of the model feature
     thinking and failing. A link to them is enough; they do not have to be in the repo. -->

IA sous-étape 3, 17 novembre 2026 : Codex a observé dans Edge l'avertissement,
le chargement et le repli de l'adaptateur désactivé sur le serveur normal, puis
le choix manuel jusqu'au panneau de confirmation sans création. Sur le seul
serveur isolé avec faux client : suggestion identifiée, historique vide avant
confirmation, réservation après clic, délai/quota/sortie invalide simulés,
aucun candidat et session révoquée. Aucun accès Google ni largeur précise
validés ; 380 pixels reste reporté. Aucun nouvel audit clavier/contraste global
ni capture archivée. Méthode, tests DOM distincts et limites : `AI_UI_3.md`.

### Vérification responsive du 19 novembre 2026

Codex a réglé Edge DevTools sur Responsive, hauteur 430 px CSS. Pour chaque
largeur, la console a confirmé `window.innerWidth` et comparé `clientWidth`
à `scrollWidth`. La mise à l'échelle de l'aperçu n'entre pas dans ces mesures.
Les captures de la session montrent des données fictives et restent dans la
conversation. Aucun fichier image n'a été archivé. L'utilisateur n'a effectué
aucune action pendant ces essais. Ses observations TP2 restent celles du guide
de la tranche 1.

Le démarrage du cluster 5433 a échoué. Les essais visuels ont donc utilisé les
routes, services et fichiers réels dans un serveur local jetable sur 8011.
Il chargeait une base SQLite en mémoire avec un compte synthétique, un labo,
deux postes et une ligne d'historique annulée. La fixture de lecture ne crée
pas les deux contraintes d'exclusion propres à PostgreSQL dans son schéma
jetable. Elle préremplissait la date du 20 novembre 2026 et retardait de 600 ms
les réponses du catalogue, des disponibilités et de l'historique. La session de
test était ouverte par la fixture, le fournisseur désactivé. Serveur arrêté
après les essais. Les comptes et les réservations de démonstration sont restés
intacts.

| Écran | Largeur CSS mesurée | Action | Résultat observé par Codex | Preuve |
| --- | --- | --- | --- | --- |
| Connexion | 380 | Lire le formulaire et tabuler au bouton d'envoi | Champs, libellés et bouton lisibles. Contour clavier visible. | Capture Edge et client/scroll 380/380. |
| Connexion | 380 | Envoyer des identifiants fictifs avec Entrée, corriger les deux champs et revenir au bouton au clavier | Refus lisible, e-mail conservé, mot de passe vidé. Les deux champs restent modifiables et le bouton reprend un contour de focus visible. | Captures Edge, console `POST /api/auth/login` 401 et `innerWidth/clientWidth/scrollWidth` de 380/380/380 après le refus. |
| Connexion | 768 | Lire le formulaire et tabuler au bouton d'envoi | Champs et bouton lisibles. Contour clavier visible. | Capture Edge et client/scroll 768/768. |
| Connexion | 1 280 | Inspecter champs, libellés et bouton | Formulaire dans la largeur, sans chevauchement observé. | Capture Edge et client/scroll 1280/1280. |
| Réservation | 380 | Choisir le laboratoire, afficher 20 créneaux, demander une suggestion désactivée, choisir manuellement, atteindre la confirmation, consulter « Mes réservations » | Message rouge lisible après HTTP 503 local. Créneau manuel sélectionnable, focus visible sur la confirmation et l'historique. Ligne annulée lisible. | Captures Edge et client/scroll 380/380. Les trois listes mesurent 298/298 horizontalement. |
| Réservation | 768 | Choisir le laboratoire et un des 20 créneaux, atteindre la confirmation, consulter « Mes réservations » | Contours de focus visibles. Résumé, boutons et historique lisibles. | Captures Edge et client/scroll 768/768. Les trois listes mesurent 494/494 horizontalement. |
| Réservation | 1 280 | Choisir le laboratoire et un des 20 créneaux, atteindre la confirmation, consulter « Mes réservations » | Contours de focus visibles. Résumé, boutons et historique dans la largeur. | Captures Edge et client/scroll 1280/1280. Les trois listes mesurent 494/494 horizontalement. |

Aucun chevauchement de texte, bouton hors largeur ou défilement horizontal
relevé dans ces parcours. Les listes peuvent défiler verticalement. Le cadre
de confirmation a été atteint sans actionner son bouton. L'historique contenait
toujours sa seule ligne synthétique.

**Défaut reproduit et corrigé.** À 380 px, ouvrir `/labs` avec la latence du
banc, attendre catalogue et historique, puis afficher les 20 créneaux. Mesurer
la position dans le document de `#booking-journey`, `#logout-form` et
`#ai-title` avant et après chaque réponse. Le template réserve maintenant une
zone défilante et nommée pour chaque liste. Le CSS stabilise la hauteur de ces
zones et réserve la place des messages. Rejeu après redémarrage du banc et
rechargement du CSS sans cache.
Le test de template vérifie les trois conteneurs, leur nom accessible, leur
attribut `tabindex` et les listes qu'ils entourent. Les mesures viennent d'Edge.

| Réponse | Élément suivi | Déplacement avant, à 380 px | Déplacement après, à 380/768/1280 px |
| --- | --- | --- | --- |
| Catalogue | Début du parcours étudiant | +163 px (407 → 570) | 0 / 0 / 0 px |
| Historique | Bloc de déconnexion | +167 px (885 → 1052) | 0 / 0 / 0 px |
| Disponibilités | Titre de la suggestion IA | +2 080 px (1098 → 3178) | 0 / 0 / 0 px |

À 380, les positions après correction sont respectivement 584, 1093 et 1386 px
avant comme après les réponses concernées. Pour l'IA désactivée, le titre de
l'historique est resté à 2104 px entre le message d'attente et le 503. Le choix
du laboratoire, l'apparition du panneau de confirmation et l'affichage initial
du message d'attente restent des changements visibles suite aux actions.
Les 0 px du tableau portent sur les trois déplacements mesurés.

Le refus de connexion à 380 px a été vérifié lors d'une reprise séparée avec
le même banc isolé et une session neuve. Codex a vu le message « Adresse e-mail
ou mot de passe incorrect. » et corrigé les champs sans renvoyer le formulaire.
Les captures restent dans la conversation. Les essais de l'étudiant restent
consignés dans les guides précédents.

**AC-42 partiel.** Les deux écrans livrés ont des preuves aux trois largeurs dans
les scénarios ci-dessus. Le refus de connexion a été vérifié à 380 px. Les
autres états et jeux de données, le refus à 768 et 1 280 px et les écrans finaux
de compte et de personnel restent sans preuve. La conformité globale et le
parcours clavier complet restent ouverts. Les contrôles Django et DOM complètent
le relevé Edge.
