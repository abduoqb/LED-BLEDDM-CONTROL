# led_serveur.py - Serveur API avec CONNEXION PERSISTANTE (Optimisé)
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import asyncio
import os
import random
import threading
import time
from pathlib import Path
from bleak import BleakClient
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
CORS(app)

# Configuration depuis les variables d'environnement
LED_ADDRESS = os.getenv('LED_ADDRESS', 'XX:XX:XX:XX:XX:XX')
CHAR_UUID = os.getenv('CHAR_UUID', '0000fff3-0000-1000-8000-00805f9b34fb')
BLUETOOTH_TIMEOUT = float(os.getenv('BLUETOOTH_TIMEOUT', '10'))
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# Variable globale pour arrêter les effets
stop_effect = False
current_effect_thread = None

class PersistentLEDController:
    """Contrôleur LED avec connexion Bluetooth persistante"""

    def __init__(self, address, char_uuid):
        self.address = address
        self.char_uuid = char_uuid
        self.client = None
        self.is_connected = False
        self.current_color = (255, 255, 255)  # Blanc par défaut
        self.current_brightness = 100

        # Thread et event loop pour gérer la connexion asynchrone
        self.loop = None
        self.connection_lock = threading.Lock()
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5

        # Statistiques
        self.stats = {
            'commands_sent': 0,
            'commands_failed': 0,
            'reconnections': 0,
            'uptime_start': time.time()
        }

    def start(self):
        """Démarre le contrôleur avec connexion persistante"""
        print("\n[STARTUP] Démarrage du contrôleur LED avec connexion persistante...")

        # Créer un nouveau thread pour gérer la connexion Bluetooth
        self.connection_thread = threading.Thread(target=self._run_connection_loop, daemon=True)
        self.connection_thread.start()

        # Attendre que la connexion soit établie
        max_wait = 15
        waited = 0
        while not self.is_connected and waited < max_wait:
            time.sleep(0.5)
            waited += 0.5

        if self.is_connected:
            print("[STARTUP] ✅ Connexion Bluetooth établie avec succès!")
            return True
        else:
            print("[STARTUP] ❌ Échec de la connexion initiale")
            return False

    def _run_connection_loop(self):
        """Exécute la boucle de connexion dans un thread séparé"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        try:
            self.loop.run_until_complete(self._maintain_connection())
        except Exception as e:
            print(f"[ERROR] Erreur dans la boucle de connexion: {e}")
        finally:
            self.loop.close()

    async def _maintain_connection(self):
        """Maintient la connexion Bluetooth active et reconnecte si nécessaire"""
        while True:
            try:
                print(f"[BT] Tentative de connexion à {self.address}...")

                async with BleakClient(self.address, timeout=BLUETOOTH_TIMEOUT) as client:
                    self.client = client
                    self.is_connected = True
                    self.reconnect_attempts = 0

                    print(f"[BT] ✅ Connecté! RSSI: {client.rssi if hasattr(client, 'rssi') else 'N/A'}")

                    # Maintenir la connexion active
                    while client.is_connected:
                        await asyncio.sleep(1)
                        # Vérification périodique de la connexion

                    print("[BT] ⚠️ Connexion perdue")
                    self.is_connected = False

            except asyncio.TimeoutError:
                self.is_connected = False
                self.reconnect_attempts += 1
                print(f"[BT] ❌ Timeout de connexion (tentative {self.reconnect_attempts}/{self.max_reconnect_attempts})")

                if self.reconnect_attempts >= self.max_reconnect_attempts:
                    print(f"[BT] ⚠️ Nombre maximum de tentatives atteint, attente 30s...")
                    await asyncio.sleep(30)
                    self.reconnect_attempts = 0
                else:
                    await asyncio.sleep(5)

            except Exception as e:
                self.is_connected = False
                print(f"[BT] ❌ Erreur: {e}")
                await asyncio.sleep(5)

            # Incrémenter le compteur de reconnexions
            if self.stats['reconnections'] > 0 or not self.is_connected:
                self.stats['reconnections'] += 1

    async def _send_command_async(self, command):
        """Envoie une commande de manière asynchrone (thread-safe)"""
        if not self.is_connected or not self.client:
            return {"success": False, "error": "Non connecté aux LEDs"}

        try:
            await self.client.write_gatt_char(
                self.char_uuid,
                bytearray(command),
                response=False
            )
            await asyncio.sleep(0.05)  # Réduit de 0.1s à 0.05s
            self.stats['commands_sent'] += 1
            return {"success": True, "error": None}

        except Exception as e:
            self.stats['commands_failed'] += 1
            return {"success": False, "error": str(e)}

    def send_command(self, command):
        """Envoie une commande de manière synchrone (pour appels depuis Flask)"""
        if not self.is_connected:
            return {"success": False, "error": "Bluetooth non connecté"}

        # Utiliser asyncio.run_coroutine_threadsafe pour exécuter dans le bon event loop
        future = asyncio.run_coroutine_threadsafe(
            self._send_command_async(command),
            self.loop
        )

        try:
            result = future.result(timeout=2.0)
            return result
        except TimeoutError:
            self.stats['commands_failed'] += 1
            return {"success": False, "error": "Timeout lors de l'envoi de la commande"}
        except Exception as e:
            self.stats['commands_failed'] += 1
            return {"success": False, "error": str(e)}

    def power_on(self):
        """Allumer"""
        return self.send_command([0x7e, 0x00, 0x04, 0xf0, 0x00, 0x01, 0xff, 0x00, 0xef])

    def power_off(self):
        """Éteindre"""
        return self.send_command([0x7e, 0x00, 0x04, 0x00, 0x00, 0x00, 0xff, 0x00, 0xef])

    def set_color(self, r, g, b):
        """Changer couleur"""
        self.current_color = (r, g, b)
        return self.send_command([0x7e, 0x00, 0x05, 0x03, r, b, g, 0x00, 0xef])

    def set_brightness(self, brightness):
        """Définir la luminosité (0-100)"""
        value = int((brightness / 100) * 255)
        self.current_brightness = brightness
        return self.send_command([0x7e, 0x00, 0x01, value, 0x00, 0x00, 0x00, 0x00, 0xef])

    def set_white(self, brightness=255):
        """Mode blanc pur"""
        result = self.set_color(255, 255, 255)
        if not result['success']:
            return result
        if brightness < 255:
            return self.set_brightness(int((brightness / 255) * 100))
        return {"success": True, "error": None}

    def get_stats(self):
        """Retourne les statistiques"""
        uptime = time.time() - self.stats['uptime_start']
        return {
            **self.stats,
            'uptime_seconds': uptime,
            'is_connected': self.is_connected,
            'success_rate': (
                self.stats['commands_sent'] /
                (self.stats['commands_sent'] + self.stats['commands_failed']) * 100
                if (self.stats['commands_sent'] + self.stats['commands_failed']) > 0
                else 0
            )
        }

    # Effets spéciaux (exécutés dans le thread d'effets)
    def rainbow_effect(self):
        """Effet arc-en-ciel"""
        global stop_effect
        print("[RAINBOW] Démarrage effet arc-en-ciel")

        colors = [
            (255, 0, 0), (255, 127, 0), (255, 255, 0),
            (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)
        ]

        while not stop_effect:
            for color in colors:
                if stop_effect:
                    break
                self.set_color(*color)
                time.sleep(1.0)

        print("[RAINBOW] Effet arrêté")

    def breathing_effect(self, color=None):
        """Effet respiration - utilise la couleur actuelle si non spécifiée"""
        global stop_effect

        # Utiliser la couleur actuelle si aucune couleur n'est spécifiée
        if color is None:
            color = self.current_color

        print(f"[BREATH] Démarrage effet respiration avec couleur {color}")

        # Définir la couleur une seule fois au début
        self.set_color(*color)

        while not stop_effect:
            for brightness in range(0, 101, 5):
                if stop_effect:
                    break
                self.set_brightness(brightness)
                time.sleep(0.05)

            for brightness in range(100, -1, -5):
                if stop_effect:
                    break
                self.set_brightness(brightness)
                time.sleep(0.05)

        self.set_brightness(100)
        print("[BREATH] Effet arrêté")

    def strobe_effect(self, color=None):
        """Effet stroboscopique - utilise la couleur actuelle si non spécifiée"""
        global stop_effect

        # Utiliser la couleur actuelle si aucune couleur n'est spécifiée
        if color is None:
            color = self.current_color

        print(f"[STROBE] Démarrage effet stroboscope avec couleur {color}")

        while not stop_effect:
            self.set_color(*color)
            time.sleep(0.1)
            self.set_color(0, 0, 0)
            time.sleep(0.1)

        # Restaurer la couleur d'origine après l'effet
        self.set_color(*color)

        print("[STROBE] Effet arrêté")

    def police_effect(self):
        """Effet sirène de police"""
        global stop_effect
        print("[POLICE] Démarrage effet sirène de police")

        while not stop_effect:
            self.set_color(255, 0, 0)
            time.sleep(0.3)
            if stop_effect:
                break
            self.set_color(0, 0, 255)
            time.sleep(0.3)

        print("[POLICE] Effet arrêté")

    def aurora_effect(self):
        """Effet aurores boréales"""
        global stop_effect
        print("[AURORA] Démarrage effet aurores boréales")

        aurora_colors = [
            (0, 255, 100), (50, 255, 150), (0, 200, 255),
            (100, 150, 255), (150, 100, 255), (100, 255, 200)
        ]

        color_index = 0

        while not stop_effect:
            target_color = aurora_colors[color_index]

            steps = 10
            delay = 0.1
            start_r, start_g, start_b = self.current_color
            target_r, target_g, target_b = target_color

            for i in range(steps + 1):
                if stop_effect:
                    break

                progress = i / steps
                r = int(start_r + (target_r - start_r) * progress)
                g = int(start_g + (target_g - start_g) * progress)
                b = int(start_b + (target_b - start_b) * progress)

                self.set_color(r, g, b)
                brightness = random.randint(70, 100)
                self.set_brightness(brightness)
                time.sleep(delay)

            time.sleep(random.uniform(1.5, 3.0))
            color_index = (color_index + 1) % len(aurora_colors)

        self.set_brightness(100)
        print("[AURORA] Effet arrêté")

    def fade_colors_effect(self, colors=None, speed=1.0):
        """Effet fondu entre plusieurs couleurs personnalisées"""
        global stop_effect
        print("[FADE] Démarrage effet fondu de couleurs")

        # Couleurs par défaut si non spécifiées
        if colors is None:
            colors = [
                (255, 0, 0),    # Rouge
                (255, 165, 0),  # Orange
                (255, 255, 0),  # Jaune
                (0, 255, 0),    # Vert
                (0, 0, 255),    # Bleu
                (148, 0, 211)   # Violet
            ]

        color_index = 0
        steps = 50  # Nombre d'étapes pour la transition
        base_delay = 0.05 / speed  # Ajuster la vitesse

        while not stop_effect:
            start_color = colors[color_index]
            next_index = (color_index + 1) % len(colors)
            target_color = colors[next_index]

            # Transition douce entre les deux couleurs
            for i in range(steps + 1):
                if stop_effect:
                    break

                progress = i / steps
                r = int(start_color[0] + (target_color[0] - start_color[0]) * progress)
                g = int(start_color[1] + (target_color[1] - start_color[1]) * progress)
                b = int(start_color[2] + (target_color[2] - start_color[2]) * progress)

                self.set_color(r, g, b)
                time.sleep(base_delay)

            color_index = next_index

        print("[FADE] Effet arrêté")

    def wave_effect(self, speed=1.0):
        """Effet vague - cycle lent entre couleurs chaudes et froides"""
        global stop_effect
        print("[WAVE] Démarrage effet vague")

        # Couleurs chaudes
        warm_colors = [
            (255, 0, 0),      # Rouge
            (255, 87, 34),    # Rouge orangé
            (255, 165, 0),    # Orange
            (255, 193, 7),    # Ambre
            (255, 255, 0)     # Jaune
        ]

        # Couleurs froides
        cool_colors = [
            (0, 255, 255),    # Cyan
            (0, 191, 255),    # Bleu ciel
            (0, 0, 255),      # Bleu
            (75, 0, 130),     # Indigo
            (148, 0, 211)     # Violet
        ]

        all_colors = warm_colors + cool_colors
        color_index = 0
        steps = 80  # Transitions très douces
        base_delay = 0.1 / speed

        while not stop_effect:
            start_color = all_colors[color_index]
            next_index = (color_index + 1) % len(all_colors)
            target_color = all_colors[next_index]

            # Transition ultra-douce
            for i in range(steps + 1):
                if stop_effect:
                    break

                progress = i / steps
                r = int(start_color[0] + (target_color[0] - start_color[0]) * progress)
                g = int(start_color[1] + (target_color[1] - start_color[1]) * progress)
                b = int(start_color[2] + (target_color[2] - start_color[2]) * progress)

                self.set_color(r, g, b)
                time.sleep(base_delay)

            color_index = next_index

        print("[WAVE] Effet arrêté")

    def custom_blink_effect(self, count=10, speed=1.0, color=None):
        """Effet clignotement personnalisé"""
        global stop_effect
        print(f"[BLINK] Démarrage clignotement ({count} fois)")

        # Utiliser la couleur actuelle si non spécifiée
        if color is None:
            color = self.current_color

        base_delay = 0.3 / speed

        blinks_done = 0
        while not stop_effect and (count == 0 or blinks_done < count):
            # Allumer
            self.set_color(*color)
            time.sleep(base_delay)

            if stop_effect:
                break

            # Éteindre
            self.set_color(0, 0, 0)
            time.sleep(base_delay)

            blinks_done += 1

        # Restaurer la couleur à la fin
        self.set_color(*color)
        print(f"[BLINK] Effet arrêté ({blinks_done} clignotements)")

# Initialiser le contrôleur
led_controller = PersistentLEDController(LED_ADDRESS, CHAR_UUID)

# ====== ROUTES API ======

@app.route('/')
def home():
    """Page d'accueil"""
    return jsonify({
        "message": "Serveur LED (Connexion Persistante)",
        "version": "2.0-persistent",
        "connected": led_controller.is_connected,
        "routes": [
            "/api/status",
            "/api/health",
            "/api/stats",
            "/api/led/on",
            "/api/led/off",
            "/api/led/color",
            "/api/led/brightness",
            "/api/led/white",
            "/api/home-arrival",
            "/api/effect/rainbow",
            "/api/effect/breathing",
            "/api/effect/strobe",
            "/api/effect/police",
            "/api/effect/aurora",
            "/api/effect/fade",
            "/api/effect/wave",
            "/api/effect/blink",
            "/api/effect/stop"
        ]
    })

@app.route('/dashboard')
def dashboard():
    """Interface web de contrôle"""
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def status():
    """Vérifier que le serveur fonctionne"""
    return jsonify({
        "status": "online",
        "message": "Serveur LED actif",
        "bluetooth_connected": led_controller.is_connected,
        "version": "2.0-persistent"
    })

@app.route('/api/health', methods=['GET'])
def health():
    """Health check détaillé"""
    stats = led_controller.get_stats()
    return jsonify({
        "status": "healthy" if led_controller.is_connected else "degraded",
        "bluetooth": {
            "connected": led_controller.is_connected,
            "address": LED_ADDRESS,
            "reconnections": stats['reconnections']
        },
        "performance": {
            "commands_sent": stats['commands_sent'],
            "commands_failed": stats['commands_failed'],
            "success_rate": f"{stats['success_rate']:.2f}%",
            "uptime_seconds": int(stats['uptime_seconds'])
        }
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Statistiques du contrôleur"""
    return jsonify(led_controller.get_stats())

@app.route('/api/led/on', methods=['POST'])
def led_on():
    """Allumer les LEDs"""
    print("[INFO] Demande d'allumage des LEDs")
    result = led_controller.power_on()
    if result['success']:
        return jsonify({"status": "success", "message": "LEDs allumees"})
    return jsonify({
        "status": "error",
        "message": f"Echec: {result['error']}"
    }), 500

@app.route('/api/led/off', methods=['POST'])
def led_off():
    """Éteindre les LEDs"""
    print("[INFO] Demande d'extinction des LEDs")
    result = led_controller.power_off()
    if result['success']:
        return jsonify({"status": "success", "message": "LEDs eteintes"})
    return jsonify({
        "status": "error",
        "message": f"Echec: {result['error']}"
    }), 500

@app.route('/api/led/color', methods=['POST'])
def led_color():
    """Changer la couleur"""
    data = request.json
    r = data.get('r', 255)
    g = data.get('g', 255)
    b = data.get('b', 255)

    print(f"[INFO] Changement de couleur: RGB({r}, {g}, {b})")
    result = led_controller.set_color(r, g, b)
    if result['success']:
        return jsonify({
            "status": "success",
            "message": f"Couleur changee: RGB({r},{g},{b})"
        })
    return jsonify({
        "status": "error",
        "message": f"Echec: {result['error']}"
    }), 500

@app.route('/api/led/brightness', methods=['POST'])
def led_brightness():
    """Changer la luminosité"""
    data = request.json
    brightness = data.get('brightness', 100)

    print(f"[INFO] Changement de luminosité: {brightness}%")
    result = led_controller.set_brightness(brightness)
    if result['success']:
        return jsonify({
            "status": "success",
            "message": f"Luminosite: {brightness}%"
        })
    return jsonify({
        "status": "error",
        "message": f"Echec: {result['error']}"
    }), 500

@app.route('/api/led/white', methods=['POST'])
def led_white():
    """Mode blanc"""
    data = request.json
    brightness = data.get('brightness', 255)

    print(f"[INFO] Mode blanc: {brightness}")
    result = led_controller.set_white(brightness)
    if result['success']:
        return jsonify({
            "status": "success",
            "message": f"Mode blanc: {brightness}"
        })
    return jsonify({
        "status": "error",
        "message": f"Echec: {result['error']}"
    }), 500

@app.route('/api/home-arrival', methods=['POST'])
def home_arrival():
    """Déclencheur automatique quand tu arrives chez toi"""
    print("[INFO] *** ARRIVEE A LA MAISON DETECTEE ***")

    # Allume en couleur chaleureuse (orange)
    led_controller.power_on()
    led_controller.set_color(255, 180, 50)

    return jsonify({
        "status": "success",
        "message": "Bienvenue a la maison! LEDs allumees."
    })

# ====== ROUTES EFFETS ======

@app.route('/api/effect/stop', methods=['POST'])
def stop_current_effect():
    """Arrêter l'effet en cours"""
    global stop_effect, current_effect_thread

    print("[INFO] Arrêt de l'effet en cours")
    stop_effect = True

    if current_effect_thread and current_effect_thread.is_alive():
        current_effect_thread.join(timeout=2)

    return jsonify({
        "status": "success",
        "message": "Effet arrêté"
    })

def start_effect(effect_func, *args):
    """Démarre un effet dans un thread séparé"""
    global stop_effect, current_effect_thread

    # Arrêter l'effet précédent
    stop_effect = True
    if current_effect_thread and current_effect_thread.is_alive():
        current_effect_thread.join(timeout=1)

    # Démarrer le nouvel effet
    stop_effect = False
    current_effect_thread = threading.Thread(
        target=effect_func,
        args=args,
        daemon=True
    )
    current_effect_thread.start()

@app.route('/api/effect/rainbow', methods=['POST'])
def effect_rainbow():
    """Effet arc-en-ciel"""
    start_effect(led_controller.rainbow_effect)
    return jsonify({
        "status": "success",
        "message": "Effet arc-en-ciel démarré"
    })

@app.route('/api/effect/breathing', methods=['POST'])
def effect_breathing():
    """Effet respiration"""
    data = request.get_json(silent=True) or {}

    # Si une couleur est fournie, l'utiliser, sinon utiliser la couleur actuelle (None)
    if 'r' in data and 'g' in data and 'b' in data:
        color = (data['r'], data['g'], data['b'])
    else:
        color = None  # Utilisera self.current_color

    start_effect(led_controller.breathing_effect, color)
    return jsonify({
        "status": "success",
        "message": "Effet respiration démarré"
    })

@app.route('/api/effect/strobe', methods=['POST'])
def effect_strobe():
    """Effet stroboscope"""
    data = request.get_json(silent=True) or {}

    # Si une couleur est fournie, l'utiliser, sinon utiliser la couleur actuelle (None)
    if 'r' in data and 'g' in data and 'b' in data:
        color = (data['r'], data['g'], data['b'])
    else:
        color = None  # Utilisera self.current_color

    start_effect(led_controller.strobe_effect, color)
    return jsonify({
        "status": "success",
        "message": "Effet stroboscope démarré"
    })

@app.route('/api/effect/police', methods=['POST'])
def effect_police():
    """Effet sirène de police"""
    start_effect(led_controller.police_effect)
    return jsonify({
        "status": "success",
        "message": "Effet sirène de police démarré"
    })

@app.route('/api/effect/aurora', methods=['POST'])
def effect_aurora():
    """Effet aurores boréales"""
    start_effect(led_controller.aurora_effect)
    return jsonify({
        "status": "success",
        "message": "Effet aurores boréales démarré"
    })

@app.route('/api/effect/fade', methods=['POST'])
def effect_fade():
    """Effet fondu de couleurs"""
    data = request.get_json(silent=True) or {}
    speed = data.get('speed', 1.0)

    # Récupérer les couleurs personnalisées si fournies
    colors = data.get('colors', None)

    start_effect(led_controller.fade_colors_effect, colors, speed)
    return jsonify({
        "status": "success",
        "message": "Effet fondu de couleurs démarré"
    })

@app.route('/api/effect/wave', methods=['POST'])
def effect_wave():
    """Effet vague de couleurs"""
    data = request.get_json(silent=True) or {}
    speed = data.get('speed', 1.0)

    start_effect(led_controller.wave_effect, speed)
    return jsonify({
        "status": "success",
        "message": "Effet vague démarré"
    })

@app.route('/api/effect/blink', methods=['POST'])
def effect_blink():
    """Effet clignotement personnalisé"""
    data = request.get_json(silent=True) or {}
    count = data.get('count', 10)
    speed = data.get('speed', 1.0)

    # Récupérer la couleur si fournie
    if 'r' in data and 'g' in data and 'b' in data:
        color = (data['r'], data['g'], data['b'])
    else:
        color = None  # Utilisera self.current_color

    start_effect(led_controller.custom_blink_effect, count, speed, color)
    return jsonify({
        "status": "success",
        "message": f"Effet clignotement démarré ({count} fois)"
    })

if __name__ == '__main__':
    print("=" * 60)
    print("  SERVEUR API LEDS - CONNEXION PERSISTANTE")
    print("=" * 60)
    print(f"  Configuration:")
    print(f"    - Adresse MAC: {LED_ADDRESS}")
    print(f"    - Host: {FLASK_HOST}")
    print(f"    - Port: {FLASK_PORT}")
    print(f"    - Debug: {FLASK_DEBUG}")
    print("=" * 60)

    # Démarrer la connexion persistante
    if led_controller.start():
        print(f"\n  ✅ Système prêt!")
        print(f"  📡 Connexion Bluetooth PERSISTANTE active")
        print(f"  ⚡ Latence réduite de ~3.5s à ~0.1s par commande")
        print("=" * 60)
        print(f"  🌐 Acces local: http://localhost:{FLASK_PORT}")
        print(f"  🎨 Interface web: http://localhost:{FLASK_PORT}/dashboard")
        print(f"  📊 Statistiques: http://localhost:{FLASK_PORT}/api/stats")
        print(f"  💚 Health check: http://localhost:{FLASK_PORT}/api/health")
        print("=" * 60)
        print("\n[SERVEUR] En attente de connexions...\n")
    else:
        print("\n  ⚠️ ATTENTION: Connexion Bluetooth non établie")
        print("  Le serveur démarre quand même, mais les commandes échoueront")
        print("  Le système tentera de se reconnecter automatiquement")
        print("=" * 60)
        print(f"  🌐 Acces local: http://localhost:{FLASK_PORT}")
        print("=" * 60)
        print("\n[SERVEUR] En attente de connexions...\n")

    # Lance le serveur avec configuration depuis .env
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
