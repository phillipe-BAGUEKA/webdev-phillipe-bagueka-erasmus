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
  - how I checked:
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
