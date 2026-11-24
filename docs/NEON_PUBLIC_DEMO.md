# Démonstration publique sur Neon — intervention locale

Le service Render est accessible sur `https://lab-booking-phillipe.onrender.com`.
Les comptes de démonstration publics ne sont **pas encore créés**. Cette procédure
écrit uniquement dans la base Neon `lab_booking` du projet existant, sans importer
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
Pour la persistance, noter l'identifiant d'un poste public, redéployer le même
code avec la même base Neon, puis vérifier que son identifiant et son nom sont
inchangés. Cette vérification n'a pas encore été effectuée.
