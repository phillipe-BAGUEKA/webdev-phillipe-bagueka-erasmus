# Démonstration publique sur Neon — intervention locale

Le service Render est accessible sur `https://lab-booking-phillipe.onrender.com`.
L'étudiant a exécuté cette procédure localement et a transmis le message
« Préparation réussie : 2 comptes, 1 laboratoire, 2 postes créés. » Cette
observation ne valide pas encore la connexion ni les réservations publiques.
La procédure écrit uniquement dans la base Neon `lab_booking` du projet existant, sans importer
SQLite ni PostgreSQL local. La formule Render Free ne fournit pas de shell pour
préparer ces lignes depuis le service ; le lanceur utilise l'image Docker locale.

Après publication du correctif et vérification de sa CI, depuis PowerShell à la
racine du dépôt :

```powershell
docker build --tag lab-booking:render-fix .
.\.venv\Scripts\python.exe tools\prepare_neon_demo.py
```

Le lanceur demande en saisie masquée : la chaîne **Direct connection** Neon de
`lab_booking` déjà validée avec `sslmode=verify-full`, `sslrootcert=system` et
`channel_binding=require`, puis deux nouveaux mots de passe distincts, saisis
deux fois. N'ajoute rien dans une commande, un profil, Render, Git ou le chat.
La chaîne n'est fournie qu'à l'entrée standard du conteneur ; le script masque
les erreurs externes et désactive son journal Docker. L'image ne lance pas sa
commande normale de migration : le conteneur exécute seulement le préparateur.

Les seuls enregistrements prévus sont deux comptes actifs sans privilèges Django
(`student-public@demo.example`, rôle étudiant ; `personnel-public@demo.example`,
rôle personnel), `DEMO PUBLIC - Laboratory` et deux postes en service
`DEMO PUBLIC - Poste A` et `DEMO PUBLIC - Poste B`. Le préparateur ne touche ni aux
comptes existants, ni aux autres laboratoires, ni aux réservations. La
transaction est atomique. Une relance ne duplique pas ces lignes et ne change
aucun mot de passe ou rôle existant ; si les comptes existaient déjà, utiliser
leurs mots de passe initiaux pour la connexion. Un enregistrement homonyme mais
incompatible déclenche un refus sans mutation partielle.

Après le message de réussite, ouvre `/login` sur Render avec le compte étudiant,
puis vérifie `/labs`, la consultation des créneaux et une création/annulation sur
le catalogue `DEMO PUBLIC`. La connexion du personnel permet de voir les
réservations et le catalogue, sans lui attribuer `is_staff`. Vérifie dans les
outils du navigateur le cookie de session sur HTTPS : `Secure`, `HttpOnly` et
`SameSite` attendu. Ne colle ni cookie ni mot de passe dans la conversation.

La première connexion étudiante a affiché « Adresse e-mail ou mot de passe
incorrect ». Pour distinguer l'identité, le hash et le backend Django, lance
depuis la racine du dépôt :

```powershell
.\.venv\Scripts\python.exe -m tools.check_neon_demo_login
```

Saisis localement la même URL directe puis le mot de passe étudiant choisi lors
de la préparation. Le diagnostic force une transaction en lecture seule et
retourne uniquement `DEMO_LOGIN:...` avec un compte du catalogue. Ne transmets
que cette ligne. `LOGIN_VALID` indique que le mot de passe est accepté dans la
base interrogée ; `PASSWORD_MISMATCH`, `ACCOUNT_MISSING` et `ACCOUNT_INACTIVE`
isolent d'autres causes. L'étudiant a obtenu
`DEMO_LOGIN:PASSWORD_MISMATCH:catalogue=1/2` avec l'URL et le mot de passe
ressaisis localement. Les lignes du catalogue existent dans la base interrogée,
mais ce mot de passe ne correspond pas au hash du compte étudiant. Cela ne
prouve pas à lui seul la configuration de la base côté Render.

L'étudiant a demandé de rétablir les deux mots de passe qu'il a choisis. Après
les tests et la revue du correctif local, reconstruis l'image pour inclure la
fonction de reset, puis lance :

```powershell
docker build --tag lab-booking:render-fix .
.\.venv\Scripts\python.exe -m tools.reset_neon_demo_passwords
```

Saisis la même URL directe Neon, puis chacun des deux mots de passe désirés
deux fois dans l'invite masquée. Le reset vérifie l'identité, l'activité et le
rôle des deux comptes avant écriture. Il modifie uniquement leurs deux hashes
dans une transaction ; identifiants, rôles, catalogue et réservations restent
inchangés. Les sessions existantes de ces comptes seront invalidées par le
hash de session Django. N'envoie que le code final `DEMO_RESET:...` ; en cas de
résultat incertain, ne relance pas automatiquement la commande.

Le 24 novembre, l'étudiant a transmis `DEMO_RESET:OK` après cette saisie
masquée. Il a ensuite confirmé que les deux connexions Render fonctionnent.
Codex a observé dans Edge la session personnel sur `/labs` et le laboratoire
`DEMO PUBLIC - Laboratory`. Le parcours de réservation reste à vérifier.

La revue a reproduit sous Windows une conversion de `\n` en `\r\n` dans
`subprocess.run(text=True)`. L'ancien worker retirait seulement `\n`, ce qui
pouvait enregistrer un `\r` final dans les mots de passe. Les trois lanceurs
utilisent désormais une entrée binaire UTF-8 et acceptent les fins de ligne
CRLF ; les tests contrôlent ce transport. Ce défaut est une explication
plausible du refus, pas une preuve que c'était sa seule cause sur Neon.

Pour la persistance, noter l'identifiant d'un poste public, redéployer le même
code avec la même base Neon, puis vérifier que son identifiant et son nom sont
inchangés. Cette vérification n'a pas encore été effectuée.
