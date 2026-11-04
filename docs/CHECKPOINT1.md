# Point 1 — structure et données

Socle construit le 3 novembre 2026 avec l’aide de Codex. Le 4 novembre, l’utilisateur a rapporté sa vérification locale : mots de passe définis personnellement pour les deux comptes ; second seed sans création ; toutes les migrations marquées [X] ; trois laboratoires Alpha/Beta/Gamma ; deux étudiants actifs, sans privilèges administrateur ; aucune table métier de poste ou de réservation. Ce retour ne constitue pas une preuve de compréhension. Les résultats et étapes ci-dessous décrivent le point 1 ; la construction suivante est décrite dans [CHECKPOINT2.md](CHECKPOINT2.md). À la fin du point 1, Spec vs result restait vide ; il contient maintenant le bilan factuel des trois points. Voir [la finalisation du TP2](TP2_FINALIZATION.md) pour l’état actuel et la CI.

## Fichiers et chemin des données

1. `requirements.txt` et `requirements-dev.txt` fixent les dépendances, séparant exécution et tests ; `.gitignore` exclut `.venv/`, `.local/`, les bases et les données locales dans `/data/`, sans exclure `src/data/` ni ses migrations.
2. `tools/init_local.py` prépare une nouvelle clé locale sans l’afficher et un marqueur de base jetable. Il ne lit ni ne remplace une clé existante et refuse d’adopter une base préexistante sans marqueur. Les secrets Gemini ne sont pas utilisés.
3. `manage.py` charge `src/config/settings.py`, qui complète `base.py` pour la démonstration locale. `AUTH_USER_MODEL` était défini avant la première migration. Au point 1, `urls.py` était volontairement vide ; le point 2 y ajoute les parcours de session. `wsgi.py` est l’entrée standard Django.
4. `src/data/models.py` définit User et Laboratory ; `managers.py` crée les utilisateurs avec `set_password()` de Django. L’e-mail est normalisé en minuscules et les doublons de casse sont refusés en base. Le rôle métier étudiant/personnel est distinct de `is_staff`/`is_superuser`. Les permissions des futurs parcours restent à écrire dans les services partagés HTTP/MCP.
5. `src/data/migrations/0001_initial.py`, générée puis relue avant application, crée les deux modèles. Ne plus modifier cette migration appliquée : toute évolution exige une nouvelle migration. Les migrations techniques de Django créent notamment `django_session` ; cela ne constitue pas une connexion/déconnexion applicative réalisée.
6. `manage.py seed_demo` → commande dans `src/data/management/commands/seed_demo.py` → `src/data/demo.py` → ORM → `data/demo.sqlite3`. La commande refuse une autre base ou un marqueur absent/invalide. Les données divergentes provoquent un refus sans écriture partielle ; les lignes conformes restent intactes.
7. `tests/settings.py` importe uniquement les réglages non secrets et utilise une base de test en mémoire, créée par les migrations. `test_models.py` vérifie l’identité, les contraintes, le hachage Django et le schéma ; `test_demo_data.py` couvre l’idempotence, les refus et les entrées masquées simulées. Les mots de passe de test sont générés temporairement, indépendamment des comptes de démonstration.

## Versions et compatibilité

Installation uniquement dans `.venv`, à partir du Python local 3.13.7 ; SQLite embarqué 3.50.4. Django 5.2 accepte Python 3.13 selon sa [documentation officielle](https://docs.djangoproject.com/en/5.2/faq/install/#what-python-version-can-i-use-with-django), consultée le 3 novembre 2026. Cela ne signifie pas que le correctif Python 3.13.7 est le plus récent ; aucun Python global n’a été mis à jour. Les métadonnées installées de Django, pytest et pytest-django demandent Python >= 3.10. `pip check` ne détecte aucun conflit. Le fonctionnement local est testé ; Codespaces n’a pas été exécuté pendant cette étape.

| Dépendance directe | Version installée | Usage |
| --- | --- | --- |
| Django | 5.2.18 | Branche 5.2 LTS, ORM, migrations, authentification et hachage |
| tzdata | 2026.6 | Résolution de Europe/Sofia, vérifiée sur Windows |
| pytest | 9.2.0 | Exécution des tests |
| pytest-django | 4.14.0 | Création de base isolée et intégration Django |

Dépendances transitives également figées : asgiref 3.13.0, sqlparse 0.6.1, colorama 0.4.6 (Windows), iniconfig 2.3.1, packaging 26.3, pluggy 1.7.0 et Pygments 2.21.0. Aucun outil de couverture installé pour ce point ; sa mesure complète reste au point 3, sans baisse de seuil.

## Reproduire le socle sur une nouvelle copie locale

Depuis la racine, PowerShell ; ne pas remplacer un environnement ou des données existants :

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt
.\.venv\Scripts\python.exe tools/init_local.py
.\.venv\Scripts\python.exe manage.py migrate --noinput
.\.venv\Scripts\python.exe manage.py seed_demo --no-input
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe -m pytest -v
```

Sous Linux/Codespaces, remplacer `.\.venv\Scripts\python.exe` par `.venv/bin/python`. Ces équivalents n’ont pas été exécutés sur Linux ici. La migration initiale est versionnable : ne pas la régénérer sur une nouvelle copie avant de l’appliquer.

`init_local.py` crée `.local/django-dev-key` uniquement si absent ; sa valeur n’est pas affichée. Les réglages de développement utilisent cette nouvelle clé sans charger de `.env`. Il s’agit de réglages locaux, pas de paramètres de production. Les chemins locaux et les dossiers temporaires de pytest sont ignorés par Git ; ils ne doivent pas être ajoutés avec `git add -f`.

## Données préparées et mots de passe

Base dédiée : `data/demo.sqlite3`, identifiée par `data/demo.marker`.

| Type | Identifiant | Valeur |
| --- | --- | --- |
| Compte étudiant | e-mail | student1@demo.example |
| Compte étudiant | e-mail | student2@demo.example |
| Laboratoire | 1 | DEMO - Laboratory Alpha |
| Laboratoire | 2 | DEMO - Laboratory Beta |
| Laboratoire | 3 | DEMO - Laboratory Gamma |

Le premier lancement non interactif a créé deux comptes et trois laboratoires ; le second a créé zéro compte et zéro laboratoire. Ils étaient initialement sans mot de passe utilisable. L’utilisateur a confirmé le 4 novembre avoir défini personnellement les deux mots de passe ; ne pas les réinitialiser pour poursuivre le projet.

Uniquement pour préparer les comptes sur une nouvelle copie, la procédure interactive est la suivante. Elle n’est pas à répéter sur les comptes déjà configurés :

```powershell
.\.venv\Scripts\python.exe manage.py changepassword student1@demo.example
.\.venv\Scripts\python.exe manage.py changepassword student2@demo.example
.\.venv\Scripts\python.exe manage.py seed_demo --no-input
```

Chaque commande `changepassword` demande et confirme le mot de passe en saisie masquée, puis applique les validateurs et le hachage Django. Ne fournis jamais le mot de passe comme argument, dans le chat ou dans une capture. La dernière commande doit indiquer zéro création et `password set` pour chaque compte ; elle ne change aucun mot de passe ni rôle.

Sur une base neuve, `seed_demo` sans `--no-input` demande directement les mots de passe des seuls comptes qu’il vient de créer. Il exige un terminal et refuse le repli de `getpass` vers une saisie visible. Un refus ou une interruption laisse les comptes non encore configurés sans mot de passe utilisable ; `changepassword` permet de reprendre explicitement leur préparation. Relancer le seed ne réinitialise jamais les comptes existants.

## Vérification manuelle du point 1, rapportée par l’utilisateur le 4 novembre

1. Ouvre uniquement `data/demo.sqlite3` dans ton visualiseur SQLite. Consulte `data_laboratory` : trois lignes, avec les identifiants et noms du tableau ci-dessus.
2. Consulte uniquement les colonnes `id`, `email`, `role`, `is_active`, `is_staff`, `is_superuser` de `data_user`. Attendu : deux comptes étudiants actifs, sans privilèges administrateur. Ne partage ni mot de passe ni hash.
3. Lance `manage.py showmigrations` avec le Python du venv : toutes les migrations listées sont cochées, notamment `data.0001_initial` et `sessions.0001_initial`. Aucune table de réservation ou de poste n’est prévue.
4. La préparation personnelle des mots de passe et les résultats non sensibles (trois laboratoires, deux comptes, migrations cochées) ont été confirmés. Au terme du point 1, aucune page de connexion n’était encore à essayer ; elle appartient au point 2.

## Résultats et limites

- Migration initiale appliquée avec succès sur la nouvelle base de démonstration ; tests créant leur propre base neuve avec les migrations.
- `manage.py check` : aucun problème ; `makemigrations --check --dry-run` : aucun changement détecté.
- Suite finale du socle : 25 tests réussis, dont vérification effective PBKDF2/Django, refus des identifiants invalides dans le mécanisme Django, unicité y compris les variantes de casse, idempotence et absence de modification après conflit. Une erreur d’import dans une annotation de test ajoutée pendant la relecture a été corrigée avant ce résultat final. Il ne s’agit pas encore de tests des futures routes HTTP.
- Revue indépendante effectuée une fois, sans problème bloquant de code. L’entrée de journal demandée est présente. Les recommandations sur la protection contre le clickjacking avant les écrans et les identifiants des futurs tests HTTP sont conservées pour le point 2 ; aucun parcours supplémentaire n’a été construit.
- Les neuf tests existants du TP1 passent, sans modification de son serveur. `node checks/ex2.mjs` : 31/32, seul Spec vs result restant volontairement vide. `git diff --check` passe. Ces contrôles ne constituent pas une validation du parcours complet de la tranche.
- Première exécution dans le bac à sable : 22 succès et 3 erreurs de préparation causées par les permissions des dossiers temporaires Windows. La même suite hors de cette restriction a réussi, sans affaiblir les assertions. Des dossiers temporaires `pytest-cache-files-*` issus de cet essai restent ignorés ; aucune donnée de travail n’a été supprimée.
- La saisie réelle des mots de passe et les vérifications manuelles ont depuis été rapportées par l’utilisateur le 4 novembre. Elles n’ont pas été rejouées par Codex. Les tests de saisie masquée utilisent un faux terminal et des valeurs temporaires.
- À la fin du point 1, la CI n’installait pas requirements-dev.txt et n’était pas prête. La couverture a été mesurée au point 3, puis la CI adaptée et exécutée après publication autorisée : voir TP2_FINALIZATION.md pour les résultats distants liés au commit de livraison.
- Aucun point 2/3, Google, modèle IA, PostgreSQL, nouveau MCP, déploiement, commit ou push.
