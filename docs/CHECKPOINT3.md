# Point 3 — API et liste des laboratoires

Implémenté avec l’aide de Codex le 4 novembre 2026, puis corrigé après les retours utilisateur sur l’absence de liste. Codex a observé Alpha, Beta et Gamma dans le véritable onglet Edge sur `127.0.0.1:8000/labs`, puis réalisé la démonstration AC-48 **3 → 2 → 3** avec restauration exacte de Beta, sur autorisation explicite de l’utilisateur. Le détail et les limites figurent ci-dessous. Le contrôle à 380 pixels est reporté à la demande de l’utilisateur, non effectué et non bloquant pour cette étape. Aucune conformité mobile ni compréhension personnelle n’est déduite de ces résultats. Aucune autre tranche n’est commencée.

## Observations déjà reçues

L’utilisateur a confirmé les vérifications du socle, la préparation personnelle des mots de passe, l’affichage de la connexion et de son message d’erreur, l’accès connecté à Laboratoires, la redirection sans session vers `/login?next=/labs`, ainsi que connexion et déconnexion au clavier avec focus visible. Ces observations restent attribuées à l’utilisateur. Elles ne constituent pas un essai de la nouvelle liste ou de l’API.

Retour suivant : l’utilisateur voit son e-mail, le titre et la déconnexion, mais aucun laboratoire ni message d’état, même après rechargement complet. Il a ouvert directement `/api/labs` dans son navigateur connecté et reçu les trois objets id/name Alpha, Beta et Gamma. Cela confirme cette consultation directe de l’API, pas l’exécution du script de liste. Aucune réussite de l’affichage après correction n’a encore été rapportée.

Dernier retour utilisateur : après déconnexion, l’ouverture de `/api/labs` affiche `{"error": "Connexion requise."}`, sans laboratoire. Le statut HTTP n’a pas été relevé dans cette observation : ce corps JSON seul ne prouve pas le statut 401. Les tests automatisés du statut restent une preuve distincte.

## Reprise sur l’instance réelle — cache du module

Après la première correction MIME, l’utilisateur a signalé que la page restait vide. Codex a identifié le processus réellement en écoute : PID 5544, parent 42360, lancé par `.venv/Scripts/python.exe` de ce dépôt avec `manage.py runserver 127.0.0.1:8000 --insecure --noreload`. L’instance renvoyait déjà text/javascript pour une nouvelle requête complète au module : la correction MIME était chargée.

Dans le même onglet Edge connecté, un rechargement normal avec le panneau Réseau ouvert a pourtant montré **labs.mjs → 304 Not Modified**, l’erreur Console indiquant toujours text/plain et **aucune requête fetch** à `/api/labs`. Le fichier JavaScript n’ayant pas changé, sa date Last-Modified était identique : la revalidation conservait les anciennes métadonnées MIME du cache. Une requête HTTP conditionnelle sur cette même instance a reproduit le 304 sans Content-Type. La panne n’était donc pas une liste reçue puis masquée par CSS.

Les deux scripts initiés par le HTML réellement servi étaient `/static/js/logout.js` et `/static/js/labs.mjs`. Leurs corps reçus correspondent aux fichiers du dépôt ; aucun des deux ne contient d’import statique ou dynamique, donc aucun module secondaire n’est à télécharger. La correction minimale dans `src/templates/labs.html` ajoute **`?v=2`** à l’URL de labs.mjs. Un commentaire explique cette nouvelle version. Le module, son fetch, les règles métier et les styles ne changent pas.

Cette version est une invalidation ponctuelle du cache pour cet incident : si une future modification nécessite de remplacer une réponse déjà mise en cache, il faudra augmenter la version. La revue indépendante n’a trouvé aucun problème bloquant ou important ; elle a retenu cette remarque de maintenance sans demander de changement supplémentaire du correctif.

Le test ajouté à `tests/test_access.py` rend le HTML avec un compte isolé, en extrait l’URL du module et simule la revalidation de l’ancienne URL. **Avant correction : échec 304 au lieu de 200 ; après : réussite**, avec vérification du type JavaScript et du corps servi. L’assertion existante sur la balise module est actualisée. Les neuf tests accès/statique passent après correction, puis les **57 tests accès/statique/laboratoires/connexion/déconnexion** passent en 54,02 secondes avec la commande ci-dessous. Ce test complète les observations du vrai navigateur, sans prétendre simuler le moteur Edge.

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_access.py tests/test_static_assets.py tests/test_labs.py tests/test_auth.py tests/test_logout.py -q --tb=short
```

Le JavaScript et le Python de production n’ont pas changé dans cette correction d’URL : les résultats Node et la mesure Python de la correction MIME précédente sont réutilisés comme tels, sans prétendre les avoir relancés pour ce dernier changement de template.

Codex a redémarré uniquement le serveur identifié, après nouvelle vérification de son PID et de sa commande. Nouveau processus en écoute : **19816**, lanceur **17820**, répertoire de travail du dépôt et `--settings=src.config.settings` explicite. Aucun autre processus Python n’a été arrêté. Django a chargé normalement sa configuration de développement ; aucune valeur de clé, mot de passe ou cookie n’a été consultée ou affichée. Les données et la session existante sont conservées.

Après un **rechargement normal**, sans effacer le cache ni désactiver les protections, le panneau Réseau du navigateur réel a montré :

| Ressource sur 127.0.0.1:8000 | Réponse observée |
| --- | --- |
| `/labs` | 200 ; le HTML initie les deux scripts ci-dessous |
| `/static/js/logout.js` | 200 depuis le cache mémoire ; GET de vérification : 200 / application/javascript, corps identique au dépôt |
| `/static/js/labs.mjs?v=2` | 200 téléchargé ; GET de vérification : 200 / text/javascript, corps identique au dépôt |
| `/api/labs` | 200, type fetch, initiateur labs.mjs?v=2 ligne 23, réponse de 155 octets |
| `/static/css/app.css` | 304 au rechargement ; GET de vérification : 200 / text/css, corps identique au dépôt |

Le DOM accessible de la page contient **3 laboratoire(s) affiché(s).** puis les trois éléments **DEMO - Laboratory Alpha**, **Beta** et **Gamma**. Après fermeture des outils de diagnostic, une capture de l’outil a confirmé leur affichage visible dans la page. Aucun laboratoire n’est codé en dur dans l’interface. Ce résultat est une **observation de Codex dans le navigateur réel**, pas un retour utilisateur supplémentaire ni la validation complète d’AC-48 (retrait/restauration restant à faire).

Le serveur corrigé reste actif en arrière-plan sur 8000. Ses journaux ignorés sont `.local/server-5358eca71a844e0dbbbee0a566ac12a1.out.log` et `.local/server-5358eca71a844e0dbbbee0a566ac12a1.err.log`. L’ancien terminal ne pilote plus ce nouveau processus. Avant un futur redémarrage manuel, identifier de nouveau le PID en écoute sur 8000 et ne stopper que le serveur de ce dépôt ; ne pas arrêter tous les processus Python. Les PID ci-dessus sont les observations de cette session, pas des valeurs permanentes à réutiliser aveuglément.

## Correction du chargement du module — 4 novembre 2026

Cause démontrée avant modification :

- Le serveur existant sur `127.0.0.1:8000` sert `/static/js/labs.mjs` en HTTP 200 avec **Content-Type: text/plain** et le véritable code du module. `/static/js/logout.js` répond aussi 200, mais avec application/javascript.
- Dans l’onglet connecté existant, Codex a constaté l’absence de liste et lu dans la Console Edge : `Failed to load module script`, avec refus explicite du type MIME text/plain pour `labs.mjs`. Le module est donc refusé avant son initialisation et avant fetch ; ses messages ne peuvent pas apparaître.
- Python reconnaît également `.mjs` comme text/plain dans cet environnement Windows. Le template inclut un module en fin de page ; les sélecteurs correspondent aux éléments HTML et le code lit bien `payload.laboratories`. La règle CSS `[hidden]` conserve normalement la liste masquée jusqu’à son chargement : elle n’est pas modifiée pour contourner le problème.

Correction minimale dans `src/config/base.py` : enregistrer `.mjs` comme **text/javascript** avec `mimetypes.add_type`, au démarrage du processus Django. Aucun changement du registre Windows, du module client, du JSON, des services, de CSRF ou de la vérification MIME du navigateur. Sources techniques : [mimetypes dans Python](https://docs.python.org/3.13/library/mimetypes.html), [chargement des modules JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules).

`tests/test_static_assets.py` reproduit une association système incorrecte avant de démarrer Django dans un sous-processus aux réglages de test. Il contrôle la réponse du gestionnaire statique utilisé par runserver : statut, type MIME et corps identique au fichier. **Avant correction : 1 test en échec, AssertionError: text/plain. Après correction : réussite dans les 56 tests ciblés.** `tests/test_access.py` vérifie maintenant la balise exacte du module dans le HTML rendu. Aucun compte de démonstration n’est utilisé par ces tests.

Un serveur HTTP éphémère, avec les réglages de test sans secret local, a réellement servi `/static/js/labs.mjs` en **200 / text/javascript**, avec corps vérifié identique. La suite complète relancée passe : **104 tests pytest, 9 tests TP1, 7 tests Node** ; le contrôle Django ne relève aucun problème.

Commandes de cette correction : `.\.venv\Scripts\python.exe -m pytest tests/test_static_assets.py tests/test_access.py tests/test_labs.py tests/test_auth.py tests/test_logout.py -q`, puis le lanceur `tools/check_coverage.py` et les tests Node déjà indiqués ci-dessous. `node checks/ex2.mjs` reste à **32/32, code 0** ; `git diff --check` termine avec **code 0**.

Couverture finale relancée, sans changement des seuils ni de la configuration : services **25/25 lignes et 4/4 branches** ; global **587/642 lignes, 91,43 %**, branches **151/172, 87,79 %** (taux combiné 90,66 %). Rapport brut : `.local/coverage/185585b069ee429f98c008ca65e24136/coverage.json`, code 0, **104 tests pytest et 9 tests TP1 réussis**. Le périmètre conserve tout le code de production précédent et les deux nouvelles lignes de configuration ; aucun fichier applicatif n’est retiré de la mesure.

La revue indépendante a relevé qu’un premier rapport après correction comptait aussi le script temporaire de préparation navigateur, ignoré par Git et absent de l’inventaire de production : 587/666 lignes (88,14 %), rapport conservé dans `.local/coverage/d51d9bd3f3a04cd18c4cbaf39c002ac6/coverage.json`. Pour ne pas laisser cet artefact d’un essai interrompu modifier le périmètre, son contenu a été conservé sans suppression sous `.local/mime-browser-check.py.txt`. La mesure finale ci-dessus a ensuite été réellement exécutée. Aucun seuil, réglage d’exclusion ou code applicatif n’a été modifié pour cela. Aucun autre défaut significatif n’a été signalé par la revue ; aucun constat n’a été écarté.

Limite historique de la première tentative : un serveur navigateur temporaire avec SQLite en mémoire, compte fictif et cookies séparés avait été préparé, sans charger les secrets ni toucher à la démonstration. L’utilisateur avait interrompu Computer Use avec Échap avant son essai dans Edge. Aucune autre action navigateur n’avait été effectuée dans ce tour ; le serveur temporaire avait été arrêté et son script archivé comme texte ignoré. Le rendu n’était alors pas vérifié. La reprise autorisée sur l’instance réelle, décrite plus haut, apporte maintenant cette observation d’affichage après la correction complémentaire du cache.

## Ce qui est construit

| Fichiers | Rôle |
| --- | --- |
| `src/data/labs.py` | Lecture ORM des seuls champs id/name, triés par id. |
| `src/services/labs.py` | Contrôle de l’acteur actif par le service commun, puis lecture ; aucun HttpRequest. |
| `src/routes/labs.py`, `src/config/urls.py` | GET `/api/labs`, JSON 200 ou JSON 401 sans liste ni redirection. |
| `src/templates/labs.html`, `src/static/js/labs.mjs`, `src/static/css/app.css` | Chargement avec fetch et la session existante ; états chargement, liste, vide, erreur et nouvelle tentative ; noms insérés avec textContent. |
| `src/data/demo_labs.py`, `src/data/management/commands/demo_labs.py` | Inspection et sauvegarde/retrait/restauration strictement limités aux laboratoires fictifs de la base marquée. |
| `tests/test_labs.py`, `test_demo_labs.py`, compléments de `test_access.py` et `test_logout.py` | Preuves isolées pour AC-46 à AC-49, y compris session expirée, retrait/restauration et ancien cookie après déconnexion. |
| `tests/labs_ui.test.mjs` | Tests du véritable script client avec DOM et réseau simulés : chargement, texte, vide, HTTP/réseau/JSON invalide, 401 et réessai. Aucun rendu visuel testé. |
| `.coveragerc`, `tools/check_coverage.py`, `tests/test_coverage_runner.py`, `requirements-dev.txt` | Mesure Python réelle, sous-processus TP1, inventaire des fichiers et seuils distincts ; tests des refus du lanceur. |

Chemin : fetch → route HTTP → service de contrôle d’accès → couche de données → ORM/SQLite. La lecture ne crée ni ne modifie de données métier. Le service pourra être appelé par les futurs outils MCP avec un acteur authentifié ; aucun nouvel outil n’est ajouté ici.

Réponse authentifiée : `{"laboratories":[{"id":1,"name":"…"}]}`. Une base vide renvoie `{"laboratories":[]}`. Les sessions absentes, invalides, expirées ou rattachées à un compte devenu inactif reçoivent HTTP 401 et `{"error":"Connexion requise."}`. La page `/labs` conserve sa redirection vers la connexion, distincte du contrat JSON de l’API. Le client efface les données précédemment affichées avant une nouvelle tentative, distingue 401 des autres erreurs HTTP, propose Se reconnecter et permet de réessayer. Aucune donnée de secours fictive.

## Commande de lancement manuel

L’instance corrigée tourne déjà en arrière-plan, comme indiqué plus haut : aucun redémarrage supplémentaire n’est nécessaire pour revoir la liste maintenant. Pour un prochain lancement manuel, libérer d’abord le port 8000 en arrêtant uniquement le serveur de ce dépôt après identification. Si le serveur tourne dans ton terminal, utiliser **Ctrl+C** et attendre l’invite PowerShell. `--noreload` impose un redémarrage après modification du Python ou d’un template mis en cache. Une fois le port libre, lancer depuis la racine du dépôt :

```powershell
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --insecure --noreload
```

Garde ce terminal ouvert. `--insecure` sert les fichiers statiques locaux avec DEBUG=False ; les protections de session et CSRF restent actives. Aucune installation, migration, préparation de compte ou réinitialisation de mot de passe n’est nécessaire pour cet essai.

URL exactes :

- Connexion : <http://127.0.0.1:8000/login>
- Liste : <http://127.0.0.1:8000/labs>
- API : <http://127.0.0.1:8000/api/labs>

Utilise le même hôte `127.0.0.1` dans tout le parcours.

## Premier essai navigateur — liste et accès

1. Après le redémarrage, ouvre `/login` et connecte-toi personnellement avec ton compte existant. Attendu sur `/labs` : trois noms, dans l’ordre **DEMO - Laboratory Alpha**, **DEMO - Laboratory Beta**, **DEMO - Laboratory Gamma**. Le chargement peut être trop rapide pour être vu localement ; il est testé avec une réponse différée simulée.
2. Dans un autre onglet du même navigateur, ouvre `/api/labs`. Attendu : JSON contenant trois objets avec seulement id et name, sans données de compte.
3. Déconnecte-toi depuis `/labs`, puis rouvre `/labs` : retour à `/login?next=/labs`. Recharge l’onglet `/api/labs` : erreur JSON « Connexion requise. », sans liste. Le statut HTTP attendu est 401, observable dans l’onglet Réseau des outils du navigateur. Aucune extraction ou transmission de cookie n’est nécessaire.

Le contrôle à 380 pixels reste reporté. La présence des nouveaux contrôles dans le parcours clavier peut être vérifiée à ton rythme ; ne pas présenter le seul test Node comme une vérification du clavier ou du rendu navigateur.

## Essai AC-48 — une commande à la fois

Ces manipulations n’ont pas été exécutées sur ta base pendant la construction. Elles ont ensuite été réalisées par Codex sur ton autorisation explicite, comme consigné ci-dessous. Pour refaire l’essai : ouvre un second terminal PowerShell à la racine du dépôt, le serveur restant ouvert. Reconnecte-toi au site avant d’observer les changements.

**1. Vérifier la cible et les trois lignes.**

```powershell
.\.venv\Scripts\python.exe manage.py demo_labs list
```

Attendu : chemin du dépôt se terminant par `data\demo.sqlite3`, mention Disposable demo et identifiants 1, 2, 3. La commande vérifie le chemin configuré et le marqueur de base jetable. Si ces contrôles échouent, ne poursuivre aucune manipulation.

**2. Préparer la restauration, sans modifier la base.**

```powershell
.\.venv\Scripts\python.exe manage.py demo_labs backup --id 2 --snapshot data/demo-lab-2.json
```

Attendu : `Snapshot saved. No database change.` Le fichier contient la base cible, l’identifiant 2 et tous les champs actuels du laboratoire Beta. Il est créé exclusivement, écrit et synchronisé avant tout retrait. Un fichier existant n’est jamais écrasé : pour refaire ultérieurement la démonstration, choisis un nouveau nom de sauvegarde et utilise ce même nom pour les deux commandes suivantes. Ne supprime pas une sauvegarde nécessaire à une restauration en attente.

**3. Retirer uniquement Beta après sauvegarde réussie.**

```powershell
.\.venv\Scripts\python.exe manage.py demo_labs withdraw --snapshot data/demo-lab-2.json
```

Attendu : `One demo laboratory withdrawn; snapshot preserved.` Recharge `/labs` : seuls Alpha et Gamma doivent apparaître. Le retrait refuse une sauvegarde absente/invalide, une autre base ou une ligne qui a changé. Les comptes et les autres laboratoires restent intacts.

**4. Restaurer immédiatement la ligne et son identifiant.**

```powershell
.\.venv\Scripts\python.exe manage.py demo_labs restore --snapshot data/demo-lab-2.json
```

Attendu : `Laboratory restored.` Recharge `/labs` : les trois noms reviennent, dans leur ordre initial. La restauration ne remplace jamais une ligne divergente ; une ligne déjà restaurée à l’identique est conservée. La sauvegarde reste disponible.

**5. Confirmer le rétablissement.**

```powershell
.\.venv\Scripts\python.exe manage.py demo_labs list
```

Attendu : les mêmes identifiants 1, 2, 3 et les mêmes noms. Le scénario de liste entièrement vide est testé automatiquement sur une base isolée ; il ne nécessite pas de vider ta base de démonstration.

### Résultat effectivement observé par Codex — 4 novembre 2026

La session Edge existante sur `http://127.0.0.1:8000/labs` était connectée avant toute manipulation. Un rechargement a affiché Alpha, Beta et Gamma, dans cet ordre. La commande `demo_labs list` a confirmé la base `C:\Users\loicp\Documents\I3\Web\Web-Project\webdev-phillipe-bagueka-erasmus\data\demo.sqlite3` et les lignes 1, 2 et 3.

La sauvegarde a été créée **avant le retrait**, sans écraser de fichier existant, avec les commandes du guide et le nom `data/demo-lab-2-ac48-20261104.json`. Le message obtenu était `Snapshot saved. No database change.` Une lecture SQLite en mode lecture seule a confirmé que le modèle possède exactement les colonnes `id` et `name`, que leur contenu correspond à la sauvegarde (`2`, `DEMO - Laboratory Beta`), et qu’aucune clé étrangère entrante ni aucun déclencheur de cette table ne peut provoquer de suppression liée. Les contrôles existants de base marquée et d’absence de relations du modèle ont aussi réussi. Base et sauvegarde sont ignorées par Git.

| Étape | Commande et observation réelle dans le même navigateur |
| --- | --- |
| Avant retrait | **3 laboratoire(s) affiché(s).** : Alpha, Beta, Gamma. |
| Retrait ciblé | `demo_labs withdraw --snapshot data/demo-lab-2-ac48-20261104.json` → `One demo laboratory withdrawn; snapshot preserved.` Après rechargement : **2 laboratoire(s) affiché(s).**, Alpha et Gamma seuls ; Beta absent. |
| Restauration immédiate | `demo_labs restore --snapshot data/demo-lab-2-ac48-20261104.json` → `Laboratory restored.` Après rechargement : **3 laboratoire(s) affiché(s).**, Alpha, Beta, Gamma. |

La restauration a suivi directement l’observation intermédiaire. La comparaison finale en lecture seule a confirmé l’égalité de Beta avec sa sauvegarde sur **tous ses champs, identifiant compris**. Le catalogue final retrouve exactement les trois identifiants et noms initiaux, dans l’ordre 1, 2, 3. La sauvegarde reste disponible localement. Aucune préparation de comptes, connexion/déconnexion supplémentaire, modification de rôle, mot de passe ou migration n’a été effectuée ; la session existante est restée utilisable.

Il s’agit d’observations de Codex dans le navigateur réel (rendu visible et arbre accessible), distinctes du retour utilisateur sur l’API après déconnexion. Aucun fichier de capture n’a été archivé dans le dépôt. Le scénario navigateur AC-48 de retrait/restauration est réussi ; la liste vide et l’absence de modification métier par la consultation restent couvertes par les tests isolés précédemment exécutés, non relancés lors de cet essai sans changement de code.

Contrôles documentaires de cette étape : `node checks/ex2.mjs` a passé **32/32 contrôles, code 0**, après un premier blocage EPERM du bac à sable sur un répertoire temporaire pytest existant et relance autorisée. `git diff --check` a terminé avec **code 0**. Aucun contrôle ni fichier applicatif n’a été modifié pour obtenir ces résultats.

## Tests et couverture de la construction initiale

Commandes exécutées :

```powershell
.\.venv\Scripts\python.exe tools/check_coverage.py
node --test tests/labs_ui.test.mjs
node --check src/static/js/labs.mjs
.\.venv\Scripts\python.exe manage.py check --settings=tests.settings
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run --settings=tests.settings
.\.venv\Scripts\python.exe -m pip check
node checks/ex2.mjs
git diff --check
```

Le lanceur utilise le Python courant et coverage.py **7.17.1**, installé seulement dans `.venv`. Il exécute pytest puis les neuf tests stdio du TP1, avec `patch = subprocess`, combine les données et produit un rapport JSON dans un nouveau répertoire à chaque exécution. Il refuse des tests en échec, un fichier de production absent du rapport, des services non mesurés, un serveur TP1 sans lignes exécutées ou un seuil insuffisant. Aucun essai Gemini ni appel fournisseur.

Résultats sur les fichiers relus : **103 tests pytest réussis**, **9 tests TP1 réussis**, **7 tests JavaScript réussis**. Les contrôles Django n’indiquent aucun problème ni dérive de migration ; syntaxe JavaScript et dépendances cohérentes. Le premier lancement Node a été bloqué par `spawn EPERM` dans le bac à sable ; la même commande hors de cette restriction a réussi, sans modification des assertions.

`node checks/ex2.mjs` : **32/32 contrôles, code 0**. `git diff --check` : **code 0, aucune erreur**. La section Spec vs result contient désormais un bilan factuel de la construction, avec les essais manuels encore en attente ; ce contrôle structurel ne valide pas ces essais.

| Mesure Python | Résultat | Seuil |
| --- | --- | --- |
| Lignes des services | 25/25 = **100 %** | 100 % |
| Branches des services | 4/4 = **100 %** | 100 % |
| Lignes globales | 585/640 = **91,41 %** | Au moins 80 % |
| Branches globales, informatif | 151/172 = **87,79 %** | Aucun seuil global supplémentaire choisi |
| Lignes du serveur TP1 incluses | 91/106 = **85,85 %** | Incluses dans le global |

Le tableau standard de coverage.py affiche aussi un taux combinant lignes et branches de **90,64 %** ; le seuil demandé de 80 % est contrôlé sur les seules lignes, sans confusion avec ce taux combiné. La commande complète termine avec le code 0.

Périmètre : tout le Python du dépôt consacré au projet, dont `src/`, migrations, configuration, commandes de démonstration, `manage.py`, `tools/` et `mcp-server/server.py`. Exclusions de mesure : `tests/*`, `mcp-server/test_server.py` (code de test), `.venv/*` (dépendances tierces). Les répertoires de métadonnées Git, dépendances/générations et artefacts locaux ne sont pas des sources de production dans l’inventaire. Aucun pragma ou exception TYPE_CHECKING n’exclut des lignes de production. L’annotation de User dans le service d’authentification utilise désormais un import direct, sans branche réservée au typage.

Les lignes non exécutées restent au dénominateur : notamment le chargement des réglages locaux dans `src/config/settings.py`, `manage.py` et WSGI sont à 0 % dans cette mesure isolée. Aucun secret existant n’a été lu pour les couvrir. Le parent de la suite unittest, dont le code de test est exclu, émet `No data was collected` ; ses sous-processus sont néanmoins mesurés, avec 91 lignes exécutées du serveur dans le rapport fusionné. Cet avertissement n’est pas masqué.

Rapport brut local, ignoré par Git : `.local/coverage/45df6bbef57b420088ba7e907e8488cc/coverage.json`. Les données brutes par processus sont conservées dans le même répertoire. Sources officielles consultées : [configuration coverage.py](https://coverage.readthedocs.io/en/latest/config.html), [mesure des sous-processus](https://coverage.readthedocs.io/en/latest/subprocess.html).

Cette mesure concerne Python. Les sept tests Node vérifient la logique client avec des doubles de DOM/réseau, pas la couverture globale multilangage ou le rendu mobile. Aucun workflow CI n’avait été modifié pendant la construction du point 3 ; l’adaptation ultérieure autorisée et les résultats locaux actualisés sont dans [TP2_FINALIZATION.md](TP2_FINALIZATION.md).

La revue indépendante en lecture seule n’a relevé aucun problème fonctionnel important. Une contradiction du plan sur le statut des commandes a été corrigée : seules les variantes Codespaces/CI restent prévisionnelles. Une suggestion facultative de mise en forme plus aérée de tests est différée, sans défaut de comportement identifié. Aucun code de production n’a changé après la mesure ci-dessus.

## Retour attendu et limites

L’affichage réel par fetch et le scénario AC-48 **3 → 2 → 3** ont été observés par Codex sur l’instance 8000 ; Beta est restauré à l’identique. L’utilisateur a rapporté le refus JSON de l’API après déconnexion, sans statut HTTP relevé : la confirmation manuelle de ce statut reste distincte des tests automatisés réussis. Le bilan Spec vs result sépare ces trois sources de preuves. Le contrôle 380 pixels reste explicitement non effectué ; la tranche entière n’est pas déclarée vérifiée manuellement. La finalisation documentaire et la CI locale sont maintenant préparées séparément dans TP2_FINALIZATION.md, sans rejouer Beta. Aucune nouvelle tranche, inspection des secrets, activation de facturation, commit ou push.
