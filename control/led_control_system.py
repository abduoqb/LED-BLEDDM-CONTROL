# led_control_system.py - VERSION COMPLETE avec Flammes, Aurores, Pomodoro
import asyncio
import threading
import random
import os
from pathlib import Path
from bleak import BleakClient
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Configuration depuis les variables d'environnement
LED_ADDRESS = os.getenv('LED_ADDRESS', 'XX:XX:XX:XX:XX:XX')
CHAR_UUID = os.getenv('CHAR_UUID', '0000fff3-0000-1000-8000-00805f9b34fb')
BLUETOOTH_TIMEOUT = float(os.getenv('BLUETOOTH_TIMEOUT', '15'))

# Variable globale pour arrêter les effets
stop_effect = False

def wait_for_enter():
    """Attend que l'utilisateur appuie sur Entrée"""
    global stop_effect
    input("\n[INFO] Appuyez sur ENTREE pour arreter l'effet...\n")
    stop_effect = True

class LEDController:
    def __init__(self, address):
        self.address = address
        self.client = None
        self.is_on = False
        self.current_color = (0, 0, 0)
        self.current_brightness = 100
    
    async def connect(self):
        """Connexion aux LEDs"""
        print(f"Connexion a {self.address}...")
        try:
            self.client = BleakClient(self.address, timeout=BLUETOOTH_TIMEOUT)
            await self.client.connect()
            print("Connecte avec succes!\n")
            return True
        except Exception as e:
            print(f"Erreur de connexion: {e}")
            return False
    
    async def disconnect(self):
        """Déconnexion"""
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            print("\nDeconnecte")
    
    async def send_command(self, command):
        """Envoyer une commande aux LEDs"""
        try:
            if self.client and self.client.is_connected:
                await self.client.write_gatt_char(CHAR_UUID, bytearray(command), response=False)
                await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Erreur lors de l'envoi de la commande: {e}")
    
    async def power_on(self):
        """Allumer les LEDs"""
        await self.send_command([0x7e, 0x00, 0x04, 0xf0, 0x00, 0x01, 0xff, 0x00, 0xef])
        self.is_on = True
        print("[ON] LEDs allumees")
    
    async def power_off(self):
        """Éteindre les LEDs"""
        await self.send_command([0x7e, 0x00, 0x04, 0x00, 0x00, 0x00, 0xff, 0x00, 0xef])
        self.is_on = False
        print("[OFF] LEDs eteintes")
    
    async def set_color(self, red, green, blue):
        """Définir la couleur RGB (0-255)"""
        await self.send_command([0x7e, 0x00, 0x05, 0x03, red, blue, green, 0x00, 0xef])
        self.current_color = (red, green, blue)
    
    async def set_brightness(self, brightness):
        """Définir la luminosité (0-100)"""
        value = int((brightness / 100) * 255)
        await self.send_command([0x7e, 0x00, 0x01, value, 0x00, 0x00, 0x00, 0x00, 0xef])
        self.current_brightness = brightness
    
    async def set_white(self, brightness=255):
        """Mode blanc pur"""
        await self.set_color(255, 255, 255)
        if brightness < 255:
            await self.set_brightness(int((brightness / 255) * 100))
        print(f"[WHITE] {brightness}")
    
    # Effets de base
    async def fade_to_color(self, target_r, target_g, target_b, duration=2.0):
        """Transition douce vers une couleur"""
        print(f"[FADE] Transition vers RGB({target_r}, {target_g}, {target_b})...")
        steps = 30
        delay = duration / steps
        
        start_r, start_g, start_b = self.current_color
        
        for i in range(steps + 1):
            progress = i / steps
            r = int(start_r + (target_r - start_r) * progress)
            g = int(start_g + (target_g - start_g) * progress)
            b = int(start_b + (target_b - start_b) * progress)
            await self.set_color(r, g, b)
            await asyncio.sleep(delay)
    
    async def rainbow_effect(self):
        """Effet arc-en-ciel en boucle"""
        global stop_effect
        stop_effect = False
        
        print("[RAINBOW] Effet arc-en-ciel demarre (Appuyez sur ENTREE pour arreter)")
        
        thread = threading.Thread(target=wait_for_enter, daemon=True)
        thread.start()
        
        colors = [
            (255, 0, 0),    # Rouge
            (255, 127, 0),  # Orange
            (255, 255, 0),  # Jaune
            (0, 255, 0),    # Vert
            (0, 0, 255),    # Bleu
            (75, 0, 130),   # Indigo
            (148, 0, 211),  # Violet
        ]
        
        while not stop_effect:
            for color in colors:
                if stop_effect:
                    break
                await self.set_color(*color)
                await asyncio.sleep(1.0)
        
        print("[RAINBOW] Effet arrete")
    
    async def strobe_effect(self, color=(255, 255, 255)):
        """Effet stroboscopique en boucle"""
        global stop_effect
        stop_effect = False
        
        print("[STROBE] Effet stroboscopique demarre (Appuyez sur ENTREE pour arreter)")
        
        thread = threading.Thread(target=wait_for_enter, daemon=True)
        thread.start()
        
        while not stop_effect:
            await self.set_color(*color)
            await asyncio.sleep(0.1)
            await self.set_color(0, 0, 0)
            await asyncio.sleep(0.1)
        
        print("[STROBE] Effet arrete")
    
    async def breathing_effect(self, color=(0, 0, 255)):
        """Effet respiration en boucle"""
        global stop_effect
        stop_effect = False
        
        print("[BREATH] Effet respiration demarre (Appuyez sur ENTREE pour arreter)")
        
        thread = threading.Thread(target=wait_for_enter, daemon=True)
        thread.start()
        
        await self.set_color(*color)
        
        while not stop_effect:
            # Montée
            for brightness in range(0, 101, 5):
                if stop_effect:
                    break
                await self.set_brightness(brightness)
                await asyncio.sleep(0.05)
            
            # Descente
            for brightness in range(100, -1, -5):
                if stop_effect:
                    break
                await self.set_brightness(brightness)
                await asyncio.sleep(0.05)
        
        await self.set_brightness(100)
        print("[BREATH] Effet arrete")
    
    async def police_effect(self):
        """Effet sirène de police en boucle"""
        global stop_effect
        stop_effect = False
        
        print("[POLICE] Effet sirene de police demarre (Appuyez sur ENTREE pour arreter)")
        
        thread = threading.Thread(target=wait_for_enter, daemon=True)
        thread.start()
        
        while not stop_effect:
            await self.set_color(255, 0, 0)  # Rouge
            await asyncio.sleep(0.3)
            if stop_effect:
                break
            await self.set_color(0, 0, 255)  # Bleu
            await asyncio.sleep(0.3)
        
        print("[POLICE] Effet arrete")
    
    # NOUVEAUX EFFETS
    
    async def fire_effect(self):
        """Effet feu/flammes réaliste avec couleurs chaudes"""
        global stop_effect
        stop_effect = False
    
        print("[FIRE] Effet flammes demarre (Appuyez sur ENTREE pour arreter)")
        print("[FIRE] Simulation de feu avec variations chaudes aleatoires...")
        
        thread = threading.Thread(target=wait_for_enter, daemon=True)
        thread.start()
        
        # Palette de couleurs de flammes (du plus chaud au plus sombre)
        fire_colors = [
            # Coeur du feu (très chaud - blanc/jaune)
            (255, 255, 200),  # Blanc-jaune chaud
            (255, 245, 150),  # Jaune brillant
            (255, 235, 100),  # Jaune intense
            
            # Flammes principales (orange chaud)
            (255, 200, 50),   # Orange-jaune
            (255, 180, 40),   # Orange vif
            (255, 160, 30),   # Orange profond
            (255, 140, 20),   # Orange foncé
            
            # Base des flammes (rouge-orange)
            (255, 120, 10),   # Rouge-orange
            (255, 100, 5),    # Rouge chaud
            (255, 80, 0),     # Rouge vif
            (245, 70, 0),     # Rouge profond
            
            # Braises (rouge sombre)
            (220, 50, 0),     # Rouge sombre
            (200, 40, 0),     # Braise chaude
            (180, 30, 0),     # Braise moyenne
        ]
        
        while not stop_effect:
            # Choix aléatoire pondéré (plus de couleurs chaudes)
            color_choice = random.choices(
                fire_colors,
                weights=[
                    8, 10, 12,  # Coeur (plus rare)
                    15, 20, 20, 18,  # Flammes (fréquent)
                    15, 12, 10, 8,   # Base (moyen)
                    5, 3, 2          # Braises (rare)
                ],
                k=1
            )[0]
            
            r, g, b = color_choice
            
            # Ajoute des variations subtiles pour plus de naturel
            r = min(255, r + random.randint(-10, 10))
            g = min(255, max(0, g + random.randint(-15, 15)))
            b = min(255, max(0, b + random.randint(-5, 5)))
            
            await self.set_color(r, g, b)
            
            # Variation de luminosité pour effet scintillement
            # Plus lumineux pour les couleurs chaudes
            if g > 150:  # Couleurs jaunes (coeur)
                brightness = random.randint(85, 100)
            elif g > 100:  # Couleurs oranges (flammes)
                brightness = random.randint(75, 95)
            else:  # Couleurs rouges (base)
                brightness = random.randint(60, 85)
            
            await self.set_brightness(brightness)
            
            # Délai aléatoire variable selon l'intensité
            if g > 150:  # Coeur : change vite
                await asyncio.sleep(random.uniform(0.03, 0.08))
            elif g > 80:  # Flammes : vitesse moyenne
                await asyncio.sleep(random.uniform(0.05, 0.12))
            else:  # Braises : change lentement
                await asyncio.sleep(random.uniform(0.1, 0.2))
        
        await self.set_brightness(100)
        print("[FIRE] Effet arrete")

    
    async def aurora_effect(self):
        """Effet aurores boréales"""
        global stop_effect
        stop_effect = False
        
        print("[AURORA] Effet aurores boreales demarre (Appuyez sur ENTREE pour arreter)")
        print("[AURORA] Variations douces de vert, bleu et violet...")
        
        thread = threading.Thread(target=wait_for_enter, daemon=True)
        thread.start()
        
        # Palette d'aurores boréales
        aurora_colors = [
            (0, 255, 100),    # Vert brillant
            (50, 255, 150),   # Vert-cyan
            (0, 200, 255),    # Cyan
            (100, 150, 255),  # Bleu-violet
            (150, 100, 255),  # Violet
            (100, 255, 200),  # Vert d'eau
        ]
        
        color_index = 0
        
        while not stop_effect:
            target_color = aurora_colors[color_index]
            
            # Transition douce vers la couleur suivante
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
                
                await self.set_color(r, g, b)
                
                # Légère variation de luminosité
                brightness = random.randint(70, 100)
                await self.set_brightness(brightness)
                
                await asyncio.sleep(delay)
            
            # Pause sur la couleur
            await asyncio.sleep(random.uniform(1.5, 3.0))
            
            # Couleur suivante
            color_index = (color_index + 1) % len(aurora_colors)
        
        await self.set_brightness(100)
        print("[AURORA] Effet arrete")
    
    async def pomodoro_mode(self, work_minutes=25, break_minutes=5, cycles=4):
        """Mode concentration Pomodoro"""
        global stop_effect
        stop_effect = False
        
        print("=" * 60)
        print("[POMODORO] Mode concentration demarre!")
        print(f"  - Travail: {work_minutes} min (blanc)")
        print(f"  - Pause: {break_minutes} min (vert)")
        print(f"  - Cycles: {cycles}")
        print("  - Appuyez sur ENTREE pour arreter")
        print("=" * 60)
        
        thread = threading.Thread(target=wait_for_enter, daemon=True)
        thread.start()
        
        for cycle in range(1, cycles + 1):
            if stop_effect:
                break
            
            # PHASE TRAVAIL
            print(f"\n[POMODORO] Cycle {cycle}/{cycles} - TRAVAIL ({work_minutes} min)")
            await self.set_color(255, 255, 255)  # Blanc pour concentration
            await self.set_brightness(100)
            
            # Compte à rebours
            for minute in range(work_minutes):
                if stop_effect:
                    break
                remaining = work_minutes - minute
                print(f"[POMODORO] Travail - {remaining} min restantes...", end='\r')
                await asyncio.sleep(60)  # 1 minute
            
            if stop_effect:
                break
            
            # ALERTE FIN TRAVAIL
            print("\n[POMODORO] Temps de travail termine!")
            for _ in range(3):
                await self.set_color(0, 255, 0)  # Vert
                await asyncio.sleep(0.5)
                await self.set_color(0, 0, 0)
                await asyncio.sleep(0.5)
            
            # PHASE PAUSE (sauf au dernier cycle)
            if cycle < cycles:
                print(f"[POMODORO] PAUSE ({break_minutes} min) - Reposez-vous!")
                await self.set_color(0, 255, 0)  # Vert relaxant
                await self.set_brightness(70)
                
                for minute in range(break_minutes):
                    if stop_effect:
                        break
                    remaining = break_minutes - minute
                    print(f"[POMODORO] Pause - {remaining} min restantes...", end='\r')
                    await asyncio.sleep(60)
                
                if stop_effect:
                    break
                
                # ALERTE FIN PAUSE
                print("\n[POMODORO] Pause terminee! Retour au travail.")
                for _ in range(2):
                    await self.set_color(255, 255, 0)  # Jaune
                    await asyncio.sleep(0.5)
                    await self.set_color(0, 0, 0)
                    await asyncio.sleep(0.5)
        
        # FIN DES CYCLES
        if not stop_effect:
            print(f"\n[POMODORO] Session complete! {cycles} cycles termines. Bravo!")
            # Celebration
            for _ in range(5):
                await self.set_color(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
                await asyncio.sleep(0.3)
        
        await self.set_color(255, 255, 255)
        await self.set_brightness(100)
        print("[POMODORO] Mode arrete")

async def main_menu(led):
    """Menu principal interactif"""
    
    while True:
        print("\n" + "=" * 60)
        print("           CONTROLE DES LEDs BLEDDM")
        print("=" * 60)
        print("\n[CONTROLES DE BASE]")
        print("  1. Allumer/Eteindre")
        print("  2. Changer la couleur (RGB)")
        print("  3. Changer la luminosite")
        print("  4. Mode blanc")
        
        print("\n[EFFETS SPECIAUX] (En boucle jusqu'a ENTREE)")
        print("  5. Arc-en-ciel")
        print("  6. Respiration")
        print("  7. Stroboscope")
        print("  8. Sirene de police")
        print("  9. Transition douce")
        
        print("\n[NOUVEAUX EFFETS]")
        print("  F. Flammes / Feu")
        print("  A. Aurores boreales")
        print("  P. Mode Pomodoro (Concentration)")
        
        print("\n[COULEURS RAPIDES]")
        print("  R. Rouge    V. Vert      B. Bleu")
        print("  J. Jaune    M. Magenta   C. Cyan")
        
        print("\n[AUTRES]")
        print("  0. Quitter")
        print("=" * 60)
        
        choice = input("\nVotre choix: ").strip().upper()
        
        try:
            if choice == "0":
                print("\nAu revoir!")
                break
            
            elif choice == "1":
                if led.is_on:
                    await led.power_off()
                else:
                    await led.power_on()
            
            elif choice == "2":
                r = int(input("Rouge (0-255): "))
                g = int(input("Vert (0-255): "))
                b = int(input("Bleu (0-255): "))
                await led.set_color(r, g, b)
                print(f"[COLOR] RGB({r}, {g}, {b})")
            
            elif choice == "3":
                brightness = int(input("Luminosite (0-100): "))
                await led.set_brightness(brightness)
                print(f"[BRIGHTNESS] {brightness}%")
            
            elif choice == "4":
                brightness = int(input("Intensite du blanc (0-255, defaut=255): ") or "255")
                await led.set_white(brightness)
            
            elif choice == "5":
                await led.rainbow_effect()
            
            elif choice == "6":
                r = int(input("Rouge (0-255, defaut=0): ") or "0")
                g = int(input("Vert (0-255, defaut=0): ") or "0")
                b = int(input("Bleu (0-255, defaut=255): ") or "255")
                await led.breathing_effect(color=(r, g, b))
            
            elif choice == "7":
                r = int(input("Rouge (0-255, defaut=255): ") or "255")
                g = int(input("Vert (0-255, defaut=255): ") or "255")
                b = int(input("Bleu (0-255, defaut=255): ") or "255")
                await led.strobe_effect(color=(r, g, b))
            
            elif choice == "8":
                await led.police_effect()
            
            elif choice == "9":
                r = int(input("Rouge cible (0-255): "))
                g = int(input("Vert cible (0-255): "))
                b = int(input("Bleu cible (0-255): "))
                duration = float(input("Duree transition (secondes, defaut=2): ") or "2")
                await led.fade_to_color(r, g, b, duration)
            
            # NOUVEAUX EFFETS
            elif choice == "F":
                await led.fire_effect()
            
            elif choice == "A":
                await led.aurora_effect()
            
            elif choice == "P":
                print("\nConfiguration Pomodoro:")
                work = int(input("  Duree travail (minutes, defaut=25): ") or "25")
                pause = int(input("  Duree pause (minutes, defaut=5): ") or "5")
                cycles = int(input("  Nombre de cycles (defaut=4): ") or "4")
                await led.pomodoro_mode(work, pause, cycles)
            
            # Couleurs rapides
            elif choice == "R":
                await led.set_color(255, 0, 0)
                print("[COLOR] Rouge")
            elif choice == "V":
                await led.set_color(0, 255, 0)
                print("[COLOR] Vert")
            elif choice == "B":
                await led.set_color(0, 0, 255)
                print("[COLOR] Bleu")
            elif choice == "J":
                await led.set_color(255, 255, 0)
                print("[COLOR] Jaune")
            elif choice == "M":
                await led.set_color(255, 0, 255)
                print("[COLOR] Magenta")
            elif choice == "C":
                await led.set_color(0, 255, 255)
                print("[COLOR] Cyan")
            
            else:
                print("[ERROR] Choix invalide")
        
        except ValueError:
            print("[ERROR] Valeur invalide, reessayez")
        except Exception as e:
            print(f"[ERROR] Erreur: {e}")

async def main():
    """Fonction principale"""
    led = LEDController(LED_ADDRESS)
    
    if await led.connect():
        try:
            await main_menu(led)
        except KeyboardInterrupt:
            print("\n\nInterruption detectee")
        except Exception as e:
            print(f"\n[ERROR] Erreur fatale: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await led.disconnect()
    else:
        print("[ERROR] Impossible de se connecter aux LEDs")
        print("\nQue faire:")
        print("1. Deconnecte les LEDs dans Parametres Bluetooth Windows")
        print("2. Verifie qu'aucune autre app n'utilise les LEDs")
        print("3. Relance ce programme")

if __name__ == "__main__":
    print("\nDemarrage du systeme de controle...\n")
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n[ERROR] Erreur au demarrage: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nAppuyez sur Entree pour quitter...")
