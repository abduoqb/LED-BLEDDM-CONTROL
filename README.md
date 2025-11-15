<!-- prettier-ignore-file -->

# 🎨 Système de Contrôle LEDs BLEDDM

Projet de contrôle de bandes LEDs Bluetooth BLEDDM avec interface locale, serveur API Flask et automatisation iPhone.

## 📋 Table des matières

- [Présentation](#présentation)
- [Fonctionnalités](#fonctionnalités)
- [Structure du projet](#structure-du-projet)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [API Documentation](#api-documentation)
- [Automatisation iPhone](#automatisation-iphone)
- [Dépannage](#dépannage)

---

## 🚀 Démarrage Rapide (5 minutes)

```bash
# 1. Clone et installe
git clone https://github.com/abduoqb/LED-BLEDDM-CONTRO
cd leds
pip install -r requirements.txt

# 2. Configure ton adresse MAC
cp .env.example .env
# Édite .env et remplace LED_ADDRESS par l'adresse de tes LEDs

# 3. Lance le contrôle local
cd control
python led_control_system.py

# OU lance le serveur web
cd serveur
python led_serveur.py
# Accède à http://localhost:5000/dashboard
```

**Besoin d'aide ?** Voir [Installation détaillée](#installation) ou [Dépannage](#dépannage)

---

## 🎯 Présentation

Ce projet permet de contrôler des LEDs Bluetooth BLEDDM/ELK-BLEDOM de deux façons :

1. **Interface locale** : Menu interactif en ligne de commande sur PC


<img width="300" height="300" alt="Capture d&#39;écran 2025-11-15 051241" src="https://github.com/user-attachments/assets/cefa5887-6c88-41e9-a046-b8d9db7f34ed" />


2. **Serveur web** : API Flask + Interface web accessible depuis navigateur ou iPhone




<img width="700" height="400" alt="image" src="https://github.com/user-attachments/assets/b0ad92a0-32be-4081-9999-b03bb2ab3252" />
### Caractéristiques principales

- ✅ Contrôle Bluetooth via Python (bleak)
- ✅ 9+ effets lumineux (arc-en-ciel, aurores boréales, etc.)
- ✅ Mode Pomodoro pour la concentration
- ✅ API REST Flask pour contrôle à distance
- ✅ Interface web responsive
- ✅ Automatisation iPhone avec Raccourcis iOS
- ✅ Détection d'arrivée à domicile

---

## ✨ Fonctionnalités

### Contrôles de base

- Allumer/Éteindre
- Changement de couleur RGB (0-255)
- Réglage de la luminosité (0-100%)
- Mode blanc

### Effets spéciaux

- 🌈 **Arc-en-ciel** : Cycle de couleurs continu
- 💨 **Respiration** : Variation douce de luminosité
- ⚡ **Stroboscope** : Clignotement rapide
- 🚨 **Sirène de police** : Alternance rouge/bleu
- 🌌 **Aurores boréales** : Transitions douces vert/violet/bleu
- 🎯 **Mode Pomodoro** : Cycles travail/pause avec alertes visuelles

### Couleurs rapides

- Rouge, Vert, Bleu, Jaune, Magenta, Cyan

---

## 📁 Structure du projet

```bash
leds/
├───control/
│    led_control_system.py
│
├───serveur/
|   │     led_serveur.py
|   │
|   └───templates/
|         index.html
|
├ .env.exemple
├ TOGGLE_SERVEUR_LED.vbs
├ README.md
├ TROUBLESHOOTING.md
├ requirements.txt
```

### Description des fichiers

**`control/led_control_system.py`**

- Menu interactif en terminal
- Tous les effets disponibles
- Contrôle direct des LEDs via Bluetooth
- Effets en boucle (arrêt avec Entrée)

**`serveur/led_serveur.py`**

- Serveur Flask API REST
- Routes pour tous les contrôles
- Supporte requêtes depuis iPhone/navigateur
- Écoute sur `0.0.0.0:5000`

**`serveur/templates/index.html`**

- Interface web responsive
- Boutons de contrôle visuels
- Feedback en temps réel
- Design moderne (fond sombre)

---

## 🔧 Prérequis

- **Python 3.8+**
- **Windows 10/11** (Bluetooth intégré)
- **LEDs BLEDDM/ELK-BLEDOM** (allumées et appairées)
- **Connexion Bluetooth active**
- **⚠️ Application mobile des LEDs FERMÉE** (importante : ne doit pas être ouverte)

> **Note importante :** L'application mobile officielle BLEDDM/ELK-BLEDOM ne doit **jamais** être ouverte en même temps que ce système. Elle monopolise la connexion Bluetooth et empêche le contrôle depuis le PC. Fermez-la complètement avant d'utiliser ce projet.

---

## 📦 Installation

### 1. Cloner ou télécharger le projet

```bash
git clone https://github.com/abduoqb/LED-BLEDDM-CONTROL
cd projet-leds
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

Cela installera automatiquement : `bleak`, `flask`, `flask-cors`, `python-dotenv`

### 3. Configuration

Crée ton fichier de configuration `.env` :

```bash
cp .env.example .env
```

**Trouve l'adresse MAC de tes LEDs** :

**Option 1 : nRF Connect (Android/iOS)**

- Télécharge l'app nRF Connect
- Scanne les appareils Bluetooth
- Note l'adresse MAC (ex: `AA:BB:CC:DD:EE:FF`)

**Option 2 : Windows**

- Paramètres → Bluetooth → Appareil BLEDDM → Propriétés
- Note l'adresse affichée

**Modifie le fichier `.env`** :

```env
LED_ADDRESS=AA:BB:CC:DD:EE:FF  # ← Ta vraie adresse MAC ici
```

**Note** : Ne commit JAMAIS le fichier `.env` (déjà dans `.gitignore`)

---

## 🚀 Utilisation

### Option 1 : Contrôle local (Menu interactif)

cd control
python led_control_system.py

Un menu s'affiche avec toutes les options disponibles. Les effets tournent en boucle jusqu'à ce que tu appuies sur **Entrée**.

**Raccourci clavier VSCode (optionnel) :**

- Crée `.vscode/tasks.json`
- Ajoute la configuration fournie
- Lance avec `Ctrl + Shift + B`

---

### Option 2 : Serveur web + API (Connexion Persistante - Recommandé)

#### Démarrer/Arrêter le serveur

**🪟 Windows : Script Toggle (Recommandé)**

Double-cliquez sur **`TOGGLE_SERVEUR_LED.vbs`** pour :
- **Démarrer** le serveur (si arrêté) + ouvre automatiquement le navigateur
- **Arrêter** le serveur (si actif)

✨ **Un seul script pour tout gérer !**

**Lancement manuel (alternative)** :
```bash
cd serveur
python led_serveur.py
```

**Note** : Le serveur utilise une connexion Bluetooth **persistante** pour une latence ultra-faible (~100ms au lieu de ~3.5s par commande).

Le serveur démarre sur :

http://127.0.0.1:5000 (local PC)
http://192.168.X.XXX:5000 (réseau local - note ton IP)

**Nouveautés** :

- ⚡ Latence divisée par 35 (97% plus rapide)
- 🔄 Reconnexion automatique
- 📊 Statistiques en temps réel : `http://localhost:5000/api/stats`
- 💚 Health check : `http://localhost:5000/api/health`

#### Accéder à l'interface web

Ouvre ton navigateur et va sur :

http://localhost:5000/dashboard

Tu verras une interface avec des boutons pour contrôler tes LEDs !

---

## 📡 API Documentation

### Routes disponibles

#### `GET /api/status`

Vérifie que le serveur fonctionne

curl http://localhost:5000/api/status

**Réponse :** `{"status": "online", "message": "Serveur LED actif"}`

---

#### `POST /api/led/on`

Allume les LEDs
curl -X POST http://localhost:5000/api/led/on

**Réponse :** `{"status": "success", "message": "LEDs allumees"}`

---

#### `POST /api/led/off`

Éteint les LEDs
curl -X POST http://localhost:5000/api/led/off

curl -X POST http://localhost:5000/api/led/color
-H "Content-Type: application/json"
-d '{"r": 255, "g": 0, "b": 0}'

**Paramètres :**

- `r` : Rouge (0-255)
- `g` : Vert (0-255)
- `b` : Bleu (0-255)

---

#### `POST /api/home-arrival`

Scénario d'arrivée à la maison (allume en couleur orange chaleureuse)
curl -X POST http://localhost:5000/api/home-arrival

---

## 📱 Automatisation iPhone

### Prérequis

- iPhone et PC sur le **même réseau Wi-Fi**
- Serveur Flask en cours d'exécution
- Autoriser le port 5000 dans le pare-feu Windows

### Configuration

#### 1. Trouve l'IP de ton PC

**Windows :**
ipconfig

Note l'adresse IPv4 (ex: `192.168.1.226`)

---

#### 2. Crée le raccourci iOS

Dans l'app **Raccourcis** sur iPhone :

1. Nouveau raccourci
2. Ajoute l'action **"Obtenir le contenu de l'URL"**
3. Configure :
   - **URL :** `http://192.168.1.226:5000/api/home-arrival` (remplace l'IP)
   - **Méthode :** POST
4. Nomme le raccourci "LEDs Maison"

---

#### 3. Crée l'automatisation de localisation

Dans l'onglet **Automatisation** :

1. Nouvelle automatisation → **Arriver**
2. Sélectionne **Domicile**
3. Action : **Exécuter le raccourci** → "LEDs Maison"
4. **Désactive "Demander avant d'exécuter"**

Maintenant tes LEDs s'allument automatiquement quand tu rentres chez toi ! 🎉

---

## 🛠️ Dépannage

### Les LEDs ne répondent pas

**Vérifications :**

- [ ] Les LEDs sont allumées
- [ ] Le Bluetooth du PC est activé
- [ ] L'adresse MAC est correcte dans le code
- [ ] Les LEDs ne sont pas connectées à un autre appareil
- [ ] **L'application mobile des LEDs (BLEDDM/ELK-BLEDOM) est FERMÉE**

**⚠️ IMPORTANT :** L'application mobile officielle des LEDs ne doit **PAS** être ouverte pendant l'utilisation de ce script. Elle monopolise la connexion Bluetooth et empêche le contrôle depuis le PC.

**Solution :**

1. Ferme complètement l'application mobile des LEDs
2. Déconnecte les LEDs dans les paramètres Bluetooth Windows
3. Relance le script

---

### Le serveur fonctionne en local mais pas depuis iPhone

**Causes possibles :**

1. **Pare-feu Windows bloque le port 5000**

   - Paramètres → Pare-feu → Règles entrantes
   - Autorise Python ou le port 5000

2. **iPhone et PC pas sur le même Wi-Fi**

   - Vérifie que les deux sont sur le même réseau

3. **Mauvaise adresse IP**
   - Vérifie avec `ipconfig` et utilise l'IP locale (192.168.X.X)

**Test rapide :** Ouvre Safari sur iPhone et va sur `http://TON_IP:5000/api/status`

---

### Erreur "Device not found"

**Solution :**

- Lance un scan Bluetooth pour vérifier la présence de l'appareil
- Rapproche-toi des LEDs
- Redémarre le Bluetooth sur le PC

---

### Effet Pomodoro interrompu brutalement

C'est normal ! Appuyer sur Entrée arrête l'effet immédiatement. Le script gère l'interruption proprement.

---

## 🎨 Personnalisation

### Ajouter un nouvel effet

Dans `led_control_system.py`, ajoute une nouvelle fonction async :

async def mon_effet(self):
global stop_effect
stop_effect = False

thread = threading.Thread(target=wait_for_enter, daemon=True)
thread.start()

while not stop_effect: # Ton code ici
await self.set_color(255, 0, 0)
await asyncio.sleep(1)

Puis ajoute-le au menu dans `main_menu()`.

---

### Ajouter une route API

Dans `led_serveur.py` :

@app.route('/api/mon-endpoint', methods=['POST'])
def mon_endpoint():

# Ton code ici

return jsonify({"status": "success"})

---

## 📝 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

Projet personnel et éducatif, libre d'utilisation et de modification.

---

## 👤 Auteur

Développé pour contrôler des LEDs BLEDDM avec Python, Flask et automatisation iOS.

---

## 🙏 Remerciements

- **bleak** : Bibliothèque Python Bluetooth LE
- **Flask** : Framework web Python
- **Communauté GitHub** : Documentation BLEDDM/ELK-BLEDOM

---

**Bon contrôle de LEDs ! 🎉💡**
