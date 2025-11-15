# 🔧 Guide de Dépannage - LEDs BLEDDM

## Comprendre les Erreurs 500

### Qu'est-ce qu'une erreur 500 ?

Une **erreur 500 (Internal Server Error)** signifie que le serveur Flask a rencontré un problème lors de l'exécution d'une commande.

Dans votre projet, cela arrive quand :
- ❌ La connexion Bluetooth échoue
- ❌ Les LEDs ne répondent pas
- ❌ Le timeout est dépassé
- ❌ Les LEDs sont déjà connectées ailleurs

### Messages d'erreur détaillés

Maintenant, l'interface web affiche des messages détaillés :

**Avant** :
```
❌ Echec
```

**Maintenant** :
```
❌ Echec: Timeout de connexion (10s) - LEDs hors de portée ou éteintes
```
ou
```
❌ Echec: Device with address XX:XX:XX:XX:XX:XX was not found
```

## Diagnostic avec le Script de Test

### Utilisation

```bash
cd /chemin/vers/leds
python test_connexion.py
```

### Menu du script

**1. Scanner les appareils Bluetooth**
- Liste tous les appareils Bluetooth à proximité
- Indique si vos LEDs sont détectées (🎯 CIBLE)
- Affiche la force du signal (RSSI)

**2. Tester la connexion aux LEDs**
- Tente une connexion complète
- Liste les services Bluetooth disponibles
- Vérifie que la caractéristique UUID est accessible
- Envoie une commande de test (allumer)

**3. Afficher la configuration**
- Montre les valeurs actuelles du fichier `.env`
- Vérifie l'adresse MAC configurée
- Affiche le timeout configuré

## Problèmes Courants et Solutions

### 1. Timeout de connexion

**Symptôme** :
```
❌ Echec: Timeout de connexion (10s) - LEDs hors de portée ou éteintes
```

**Causes** :
- LEDs éteintes
- LEDs trop éloignées
- Bluetooth PC désactivé

**Solutions** :
1. Vérifiez que les LEDs sont allumées
2. Rapprochez-vous des LEDs (< 10m)
3. Augmentez le timeout dans `.env` :
   ```
   BLUETOOTH_TIMEOUT=20
   ```

### 2. Appareil non trouvé

**Symptôme** :
```
❌ Echec: Device with address XX:XX:XX:XX:XX:XX was not found
```

**Causes** :
- Adresse MAC incorrecte
- LEDs connectées à un autre appareil
- LEDs hors de portée

**Solutions** :
1. Vérifiez l'adresse MAC avec `test_connexion.py` (option 1)
2. Déconnectez les LEDs dans Paramètres Bluetooth Windows :
   - Paramètres → Bluetooth et appareils
   - Cliquez sur les LEDs → Déconnecter
3. Corrigez l'adresse dans `.env` si nécessaire

### 3. Connexion refusée

**Symptôme** :
```
❌ Echec: Connection was refused
```

**Causes** :
- LEDs déjà connectées à un autre appareil
- Conflit Bluetooth

**Solutions** :
1. Fermez toute autre application utilisant les LEDs
2. Déconnectez les LEDs dans Windows
3. Redémarrez le Bluetooth :
   ```
   Paramètres → Bluetooth → Désactiver → Attendre 5s → Activer
   ```

### 4. Erreur de permission

**Symptôme** :
```
❌ Echec: Access denied
```

**Causes** :
- Permissions Bluetooth insuffisantes
- Antivirus bloquant

**Solutions** :
1. Lancez le serveur en tant qu'administrateur :
   - Clic droit sur cmd.exe → Exécuter en tant qu'administrateur
   - `cd serveur`
   - `python led_serveur.py`
2. Vérifiez les paramètres de l'antivirus

## Vérifications de Base

### Checklist avant de démarrer

- [ ] **LEDs allumées** - Vérifiez que les LEDs sont sous tension
- [ ] **Bluetooth PC activé** - Paramètres → Bluetooth et appareils
- [ ] **LEDs déconnectées** - Ne doivent pas être connectées dans Windows
- [ ] **Adresse MAC correcte** - Vérifiez dans `.env`
- [ ] **Dependencies installées** - `pip install -r requirements.txt`
- [ ] **Fichier `.env` existe** - Copiez `.env.example` si nécessaire

### Test rapide

1. **Vérifier la configuration** :
   ```bash
   python test_connexion.py
   # Choisir option 3
   ```

2. **Scanner les appareils** :
   ```bash
   python test_connexion.py
   # Choisir option 1
   # Vérifier que vos LEDs apparaissent avec 🎯
   ```

3. **Tester la connexion** :
   ```bash
   python test_connexion.py
   # Choisir option 2
   ```

## Logs du Serveur

Regardez toujours les logs dans le terminal du serveur Flask :

**Terminal du serveur** :
```bash
cd serveur
python led_serveur.py
```

**Exemples de logs** :

**Succès** :
```
[INFO] Demande d'allumage des LEDs
127.0.0.1 - - [09/Nov/2025 14:30:15] "POST /api/led/on HTTP/1.1" 200 -
```

**Échec** :
```
[INFO] Demande d'allumage des LEDs
[ERREUR] Timeout de connexion (10s) - LEDs hors de portée ou éteintes
127.0.0.1 - - [09/Nov/2025 14:30:15] "POST /api/led/on HTTP/1.1" 500 -
```

## Optimisation du Timeout

Le timeout détermine combien de temps attendre la connexion :

**Timeout court** (rapide mais peut échouer) :
```env
BLUETOOTH_TIMEOUT=5
```

**Timeout moyen** (recommandé) :
```env
BLUETOOTH_TIMEOUT=10
```

**Timeout long** (pour connexions difficiles) :
```env
BLUETOOTH_TIMEOUT=20
```

**Note** : Après modification du `.env`, redémarrez le serveur Flask.

## Codes HTTP

| Code | Signification | Description |
|------|---------------|-------------|
| 200 | OK | Commande réussie |
| 500 | Internal Server Error | Échec Bluetooth ou erreur serveur |
| 404 | Not Found | Route API inexistante |
| 400 | Bad Request | Données JSON invalides |

## Support et Débogage Avancé

### Mode debug Flask

Activez le mode debug pour plus d'informations :

**.env** :
```env
FLASK_DEBUG=True
```

**Attention** : Ne jamais utiliser `FLASK_DEBUG=True` en production !

### Vérifier la version de bleak

```bash
pip show bleak
```

Vérifiez que la version est >= 0.20.0

### Réinstaller les dépendances

```bash
pip uninstall bleak flask flask-cors python-dotenv
pip install -r requirements.txt
```

## Problèmes Spécifiques Windows

### Bluetooth ne détecte pas les LEDs

1. Ouvrez Gestionnaire de périphériques
2. Vérifiez que l'adaptateur Bluetooth est activé
3. Mettez à jour le pilote Bluetooth

### Pare-feu bloque le serveur

Si vous accédez depuis un autre appareil (iPhone) :

1. Paramètres Windows → Pare-feu
2. Autoriser une application
3. Ajouter Python ou autoriser le port 5000

## Contacts et Ressources

- **Documentation Bleak** : https://bleak.readthedocs.io/
- **Documentation Flask** : https://flask.palletsprojects.com/
- **Protocole BLEDDM** : Voir communauté GitHub

---

**Dernière mise à jour** : 2025-11-15
