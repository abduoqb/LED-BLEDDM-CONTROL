# 📝 Guide du Script VBS - Serveur LED

Un seul script pour tout gérer : **`TOGGLE_SERVEUR_LED.vbs`**

---

## 🎯 Qu'est-ce que c'est ?

**`TOGGLE_SERVEUR_LED.vbs`** est un script Windows VBScript qui permet de démarrer et arrêter le serveur LED en un seul double-clic.

### ✨ Fonctionnalités

- 🚀 **Si le serveur est arrêté** → Démarre + ouvre le navigateur automatiquement
- 🛑 **Si le serveur est actif** → Arrête proprement tous les processus
- ✅ **Détection automatique** de l'état du serveur
- 🚫 **Prévention des doublons** : vérifie qu'aucune instance n'est déjà en cours
- 📊 **Messages clairs** sans accents pour compatibilité Windows

---

## 🚀 Utilisation

### Démarrer le serveur

1. **Double-cliquez** sur `TOGGLE_SERVEUR_LED.vbs`
2. Attendez le message de confirmation (3 secondes)
3. Le navigateur s'ouvre automatiquement sur `http://localhost:5000/dashboard`

**Message affiché** :
```
Serveur LED demarre avec succes en arriere-plan !

Interface web: http://localhost:5000/dashboard
API status: http://localhost:5000/api/status

Le navigateur va s'ouvrir automatiquement...

Double-cliquez a nouveau pour arreter.
```

---

### Arrêter le serveur

1. **Double-cliquez** à nouveau sur `TOGGLE_SERVEUR_LED.vbs`
2. Le serveur s'arrête proprement

**Message affiché** :
```
Serveur LED arrete avec succes !

X processus termine(s).

Double-cliquez a nouveau pour redemarrer.
```

---

## 🏗️ Architecture

**Un seul fichier autonome** (162 lignes) :

```
TOGGLE_SERVEUR_LED.vbs
├─ Fonction IsServerRunning()      → Vérifie si led_serveur.py tourne
├─ Fonction CountServerInstances() → Compte les instances actives
├─ Logique TOGGLE
   ├─ Si serveur actif   → Arrêter
   └─ Si serveur arrêté  → Démarrer + ouvrir navigateur
```

---

## 🔧 Fonctionnement technique

### Détection de l'état du serveur

```vbscript
1. Exécute : wmic process where "name='python.exe'" get commandline
2. Cherche "led_serveur.py" dans la sortie
3. Si trouvé → Serveur actif
4. Si non trouvé → Serveur arrêté
```

### Démarrage du serveur

```vbscript
1. Lance : cmd /c cd "serveur" && python led_serveur.py
2. Mode invisible (fenêtre cachée)
3. Attend 3 secondes
4. Vérifie que le processus tourne
5. Ouvre le navigateur : http://localhost:5000/dashboard
6. Affiche message de succès
```

### Arrêt du serveur

```vbscript
1. Scanne le port 5000 avec netstat
2. Extrait tous les PIDs des processus
3. Termine chaque processus : wmic process where ProcessId=X delete
4. Vérifie que le port est libéré
5. Affiche message de succès
```

---

## ⚠️ Résolution de problèmes

### Le serveur ne démarre pas

**Message d'erreur** :
```
Erreur: Le serveur n'a pas pu demarrer.

Verifiez que:
• Python est installe
• Les dependances sont installees (pip install -r requirements.txt)
• Le fichier .env existe

Double-cliquez a nouveau pour reessayer.
```

**Solutions** :
1. Vérifiez que Python est installé : `python --version`
2. Installez les dépendances : `pip install -r requirements.txt`
3. Vérifiez que `.env` existe à la racine du projet
4. Vérifiez l'adresse MAC dans `.env`

---

### Le serveur ne s'arrête pas

**Message d'erreur** :
```
Attention: Certains processus n'ont pas pu etre arretes.

Essayez de redemarrer l'ordinateur ou d'arreter manuellement les processus Python.
```

**Solutions** :

**Option 1 : Gestionnaire des tâches**
1. Ouvrez le Gestionnaire des tâches (Ctrl+Shift+Esc)
2. Onglet "Détails"
3. Cherchez "python.exe"
4. Clic droit → Terminer le processus

**Option 2 : Ligne de commande**
```cmd
wmic process where "name='python.exe'" delete
```

---

### Plusieurs instances détectées

**Symptôme** : Le serveur a été lancé plusieurs fois

**Solution** :
1. Double-cliquez sur `TOGGLE_SERVEUR_LED.vbs` pour tout arrêter
2. Attendez 5 secondes
3. Double-cliquez à nouveau pour redémarrer proprement

Le script détecte et arrête **toutes les instances** en une seule fois.

---

## 📌 Notes importantes

1. **Mode invisible** : Aucune fenêtre de terminal ne s'affiche. Le serveur tourne en arrière-plan.

2. **Emplacement** : Le script doit rester à la racine du projet (même niveau que le dossier `serveur/`)

3. **Détection intelligente** : Le script vérifie si `led_serveur.py` est déjà actif avant de lancer une nouvelle instance.

4. **Ouverture automatique** : Le navigateur s'ouvre automatiquement sur le dashboard au démarrage.

5. **Messages sans accents** : Pour compatibilité maximale avec les systèmes Windows.

6. **Permissions** : Aucun besoin de droits administrateur (sauf si problème de pare-feu).

---

## 🎨 Personnalisation

### Changer le port par défaut

Éditez le fichier `.env` :
```env
FLASK_PORT=8080
```

Puis dans `TOGGLE_SERVEUR_LED.vbs`, remplacez :
```vbscript
WshShell.Run "http://localhost:5000/dashboard"
```
par :
```vbscript
WshShell.Run "http://localhost:8080/dashboard"
```

### Désactiver l'ouverture automatique du navigateur

Dans `TOGGLE_SERVEUR_LED.vbs`, commentez ou supprimez la ligne :
```vbscript
' WshShell.Run "http://localhost:5000/dashboard"
```

### Changer le temps d'attente au démarrage

Par défaut : 3 secondes. Pour modifier, cherchez :
```vbscript
WScript.Sleep 3000
```
Changez `3000` (millisecondes) selon vos besoins.

---

## 🆘 Besoin d'aide ?

Si le script VBS ne fonctionne pas, vous pouvez toujours lancer le serveur manuellement :

```cmd
cd serveur
python led_serveur.py
```

**Avantage** : Vous verrez les logs en direct
**Inconvénient** : La fenêtre doit rester ouverte

---

## 📊 Comparaison avec l'ancien système

| Critère | Ancien système (4 scripts) | Nouveau système (1 script) |
|---------|---------------------------|---------------------------|
| Fichiers VBS | 4 (273 lignes total) | 1 (162 lignes) |
| Pour démarrer | LANCER_SERVEUR_INVISIBLE.vbs | TOGGLE_SERVEUR_LED.vbs |
| Pour arrêter | ARRETER_SERVEUR.vbs | TOGGLE_SERVEUR_LED.vbs |
| Pour le statut | STATUT_SERVEUR.vbs | (état détecté auto) |
| Maintenance | 4 fichiers à maintenir | 1 seul fichier |
| Simplicité | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**Avantages du système toggle** :
- ✅ Plus simple : 1 seul fichier
- ✅ Plus intuitif : double-clic pour basculer
- ✅ Moins de code : 162 lignes au lieu de 273
- ✅ Ouverture auto du navigateur
- ✅ Messages sans accents

---

**Dernière mise à jour** : 2025-11-15
