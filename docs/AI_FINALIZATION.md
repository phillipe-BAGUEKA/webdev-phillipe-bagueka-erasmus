# Finalisation de la tranche IA — Lab 03 reste ouvert

17 novembre 2026. État initial propre sur main, trois commits locaux attendus :

- `3fa6ecb238e64761d95cff5ac0299aee01fda01a` : service injectable et faux client.
- `aeba6daa3e375412767b9904224d13128b5287a1` : transport borné et API protégée.
- `e1474e16cbbef59d6febf3248407b5e7afbd6da4` : interface et parcours manuel.

Ces choix sont ceux de l'utilisateur ; code, tests, rédaction et finalisation
assistés par Codex. L'autorisation couvre publication normale et ajustements CI
nécessaires, sans nouvelle fonctionnalité, fournisseur, clé réelle, installation
locale, facturation, déploiement ou Lab 04. Pas de réécriture de l'historique.

## Preuves et limites distinctes

| Élément | Ce qui est réellement établi |
| --- | --- |
| Faux fournisseur | Tests directs/API PostgreSQL, réponses HTTP simulées et processus locaux contrôlés ; DOM et serveur navigateur isolé. Candidat validé/relu, refus explicites, aucune réservation avant confirmation, règles revérifiées à la création. Guides AI_SERVICE_1, AI_TRANSPORT_2 et AI_UI_3. |
| Fournisseur désactivé | Codex a observé dans Edge sur le serveur normal le message désactivé/non configuré puis vingt choix manuels et le panneau de confirmation, sans créer dans les données conservées. |
| Google réel | Aucun appel, clé réelle ou accès/quota du compte vérifié. Conditions EEE à clarifier selon les sources datées d'AI_TRANSPORT_2.md ; aucune activation de facturation. Une simulation réussie ne prouve ni accès ni qualité réelle. |
| MCP final | Tests stdio/parité/sessions synthétiques livrés ; lancement MCP-only Gemini CLI observé. Remise réelle de session et appels d'outils depuis le client final non validés, aucun nouvel essai ici. |
| Note/revue personnelles | Section Architecture de SPEC vide, rédaction et lecture personnelle du diff encore à faire ; revue Codex indépendante distincte, sans validation de compréhension. |
| Interface | Observations Edge et palette/clavier partiels conservés ; audit complet et largeurs 380/768/1280 non validés. 380 pixels explicitement reporté ; aucune nouvelle observation navigateur dans cette finalisation. |

## CI et périmètre conservé

Un seul ajustement nécessaire dans `.github/workflows/ci.yml` : la commande de
couverture JavaScript inclut maintenant `tests/ai_suggestion_ui.test.mjs` en plus
des deux suites existantes. Seuil 80 % et filtres inchangés. `npm test` découvre
déjà chaque fichier `tests/*.test.mjs`, donc les nouveaux tests sont exécutés
dans le job test sans changer le lanceur. Pytest collecte les suites automatisées
`test_*.py`, dont transport/API/confirmation, MCP stdio et concurrence. Les
fixtures et dispositifs manuels ne sont pas des suites collectées.

Les jobs test/coverage conservent chacun PostgreSQL 16 éphémère sur 5433, rôle
applicatif non administrateur, preuve du schéma vide puis migrations complètes.
Le mode MCP TP1 autonome et ex2 restent dans leurs jobs dédiés. L'étape Docker
conserve sa condition existante ; elle est ignorée en l'absence de Dockerfile.
L'adaptateur reste désactivé par défaut ; les tests utilisent des faux clients
et des processus locaux, jamais le fournisseur. Aucun secret GitHub requis.

Le lanceur Python inchangé inventorie toute la production : src (services,
routes, données, migrations, réglages, intégrations et worker), outils et TP1.
Exclusions existantes : tests, test_server TP1, venv et répertoires générés ou
vendeur ; aucune nouvelle exclusion. Seuils : 100 % lignes ET branches des
services, au moins 80 % des lignes Python globales, TP1 exécuté et compté.
`tests/browser_ai_demo.py` est un dispositif navigateur manuel, non collecté par
pytest, non exécuté/compilé dans la CI et non couvert par sa mesure. Il a été
utilisé et compilé localement à la sous-étape 3 ; cette preuve est distincte de
la CI. Son exclusion du calcul repose sur le répertoire tests existant ; ce
n'est pas du code de production ni un mode de simulation du déploiement normal.

Mesure locale antérieure sur le même code Python, sous PostgreSQL : 1 765/1 865
lignes (94,64 %), 445/488 branches ; services 322/322 lignes et 108/108 branches.
Cette finalisation ne change aucun Python de production ni test. La CI doit
mesurer réellement sa propre couverture Linux ; aucune égalité avec Windows
n'est présumée. Vérifier les résultats distants sur le SHA publié exact.

Vérifications de cette finalisation : `npm test` exécuté directement réussit
avec 545 tests PostgreSQL (1 garde historique SQLite désélectionné), cette garde
rejouée séparément et réussie, 9 TP1 et 42 Node. Aucun autre test ignoré.
La commande JavaScript modifiée de la CI réussit : 41 tests, 97,71 % lignes,
95,59 % branches sur les modules chargés ; ce n'est pas une couverture visuelle.
ex2 : 32/32, diff --check réussi. SQLite conserve son SHA256 initial ; profils,
base, sauvegardes et venv restent ignorés et non suivis, sans lire leur contenu.

## Contrôle Lab 03 actuel, sans retouche

`node checks/ex3.mjs` : **15/18**, sortie **1**, le 17 novembre 2026.

| Échec exact | Qualification et action restante |
| --- | --- |
| `the test suite passes` : `spawnSync npm ENOENT` | Incompatibilité Windows du vérificateur : `execFileSync('npm', ..., shell:false)` ne lance pas npm.cmd. Exécuter `npm test` directement distingue le résultat applicatif de cette incompatibilité. Le vérificateur n'est pas modifié. |
| `every acceptance criterion traces to a test` : AC-45, AC-5/6/7/8/9/10/12, AC-43/44 | Gestion du personnel non construite pour AC-5 à AC-10 et AC-12 ; preuves complètes/tests nommés absents pour AC-43 à AC-45 malgré observations partielles de clavier/palette et styles existants. Aucun identifiant artificiel ajouté. |
| `the architecture note exists` | Exigence réellement manquante : note personnelle reportée. Codex ne la rédige pas à la place de l'étudiant. |

Le contrôle de traçabilité cherche de simples sous-chaînes dans les fichiers,
pas les titres collectés : AC-1 peut sembler présent via AC-11, par exemple.
La collecte Python réelle confirme **aucun AC-1 à AC-10**, et présence exacte
d'AC-29 à AC-36 ; les tests Node n'ajoutent pas de parcours Google/personnel.
Google/liaison AC-1 à AC-4 restent donc absents même s'ils ne sont pas tous
signalés par ex3. Un test portant un identifiant ne prouve pas tout le critère.

Ce contrôle reste rouge. Ni le succès des quinze autres vérifications
structurelles, ni une CI verte ne clôturent le Lab 03. Les anciens relevés
11/18 de SLICE2_FINALIZATION sont historiques, antérieurs à IA/MCP.
Le helper d'ex3 fixe aussi 180 s pour sa commande enfant ; les seuls tests
PostgreSQL ont pris 206,01 s lors du lancement Windows direct. Aucun résultat
d'ex3 sous Linux n'est présumé ; ses limites restent intactes, à discuter avec
le professeur si elles empêchent l'exécution de la suite dans son environnement.

## Avant de demander la clôture au professeur

- Rédiger la note, relire personnellement le diff et établir le bilan personnel
  des écarts, sans les remplacer par une revue d'assistant.
- Compléter les preuves UI reportées, dont 380 pixels et audit complet.
- Clarifier si un usage fournisseur réel est requis à ce stade et dans quel
  cadre Google l'autorise ; ne pas confondre offre gratuite et usage autorisé.
- Compléter le parcours réel MCP et sa remise de session si exigés.
- Faire confirmer le périmètre Lab 03 face aux AC de tout le projet : Google et
  gestion du personnel restent absents. Ne pas les construire dans cette phase.
- Faire confirmer les adaptations Windows, rédaction assistée et commits délégués,
  la correspondance des critères de refus avec 409/422 et la relation plusieurs-
  à-plusieurs portée par Booking ; références dans SLICE2_FINALIZATION.md.

Les preuves HTTP manuelles 201/409/401/403 antérieures sont conservées, non
rejouées. SQLite, données conservées, profils et instance 5432 sont préservés.
Commandes et résultats de finalisation, revue et publication : journal et bilan
de livraison. Aucun résultat distant n'est déduit de la seule mesure locale.

## Publication et preuves distantes observées

Push normal effectué au SHA `da875b9fa25f56880bbc5e144285455dd60d6219`, incluant
les trois commits IA et la finalisation. Local et origin/main identiques, arbre
propre à cette vérification. Aucun force push, installation locale ni fournisseur.

[CI de ce SHA](https://github.com/phillipe-BAGUEKA/webdev-phillipe-bagueka-erasmus/actions/runs/44138036352) :

| Job | Résultat réellement lu dans les logs |
| --- | --- |
| [test](https://github.com/phillipe-BAGUEKA/webdev-phillipe-bagueka-erasmus/actions/runs/44138036352/job/134232857200) | Réussi : 545 PostgreSQL, 1 garde SQLite désélectionné puis rejoué séparément (1 réussi), 9 TP1 et 42 Node. Titres AC-29 à AC-36 et concurrence AC-22/23/24 effectivement présents. |
| [coverage](https://github.com/phillipe-BAGUEKA/webdev-phillipe-bagueka-erasmus/actions/runs/44138036352/job/134232857566) | Réussi : Python global 1 766/1 865 lignes (94,69 %), 446/488 branches (91,39 %) ; services 322/322 lignes et 108/108 branches (100 %). JS chargé : 41 tests, 97,71 % lignes / 95,59 % branches. |
| [mcp](https://github.com/phillipe-BAGUEKA/webdev-phillipe-bagueka-erasmus/actions/runs/44138036352/job/134232857715) | Réussi : TP1 autonome 12/12. Le mode projet est testé dans les suites PostgreSQL des jobs test/coverage. |
| [spec](https://github.com/phillipe-BAGUEKA/webdev-phillipe-bagueka-erasmus/actions/runs/44138036352/job/134232857919) | Réussi : ex2 32/32. Ce job ne signifie ni ex3 vert ni acceptation du professeur. |

Test/coverage montrent zéro table publique avant migrations, puis application de
0001/0002/0003 en PostgreSQL éphémère avec rôle restreint. Aucun job ignoré ; seule
l'étape « Docker image builds » est ignorée par la condition préexistante, sans
Dockerfile. Aucun correctif fonctionnel nécessaire à cette publication.
Le léger écart de couverture Linux/Windows est conservé, pas masqué.

Revue indépendante unique : correction documentaire retenue sur le dispositif
navigateur manuel non collecté/non exécuté en CI ; aucun constat écarté ni
défaut fonctionnel trouvé. Cette revue ne remplace pas la revue personnelle.
Le commit documentaire qui enregistre ces preuves doit recevoir sa propre
vérification CI sur son SHA ; la réussite ci-dessus concerne uniquement da875b9.
