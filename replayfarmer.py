import time
import json
import pyautogui as pg
import keyboard
import pygetwindow as gw
import cv2
import numpy as np
import sys

# Set the path to your indicator images (combat & inventory full)
COMBAT_IMAGE_PATH = "./indicators/combat_indicator.png"
INVENTORY_IMAGE_PATH = "./indicators/inventory_full_indicator.png"

CHECK_INTERVAL = 2  # Check every X seconds

def focus_game_window():
    """Find and activate the game window containing 'Lost-Ocr'."""
    windows = gw.getWindowsWithTitle("Lost-Ocr")
    if windows:
        game_window = windows[0]
        game_window.activate()
        print("Game window activated!")
        return True
    else:
        print("Game window not found!")
        return False

def load_events(filename="events.json"):
    """Load recorded events from a JSON file."""
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print("Error: events.json not found!")
        return []

def detect_combat():
    """Check if the combat indicator is on the screen."""
    screenshot = pg.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)  
    template = cv2.imread(COMBAT_IMAGE_PATH, 0)  

    if template is None:
        print("Error: Combat indicator image not found!")
        return False

    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8  
    loc = np.where(result >= threshold)

    if len(loc[0]) > 0:
        print("Combat detected!")
        return True
    return False

def check_inventory_full():
    """Check if the inventory is full by detecting the warning icon."""
    keyboard.press_and_release("i")
    time.sleep(1)  # Wait for the inventory to open
    screenshot = pg.screenshot()
    keyboard.press_and_release("i")
    time.sleep(1)  # Wait for the inventory to open
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)  
    template = cv2.imread(INVENTORY_IMAGE_PATH, 0)  

    if template is None:
        print("Error: Inventory warning image not found!")
        return False

    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8  
    loc = np.where(result >= threshold)

    if len(loc[0]) > 0:
        print("⚠️ Inventory is FULL!")
        return True
    return False

def empty_inventory():
    ZAAP_IMAGE_PATH = "./indicators/heavenzaap.png"
    AMAKNAVILLAGE_IMAGE_PATH="./indicators/amaknazaap.png"
    TPBUTTON_IMAGE_PATH= "./indicators/teleportbutton.png"
    AMAKNABANK_IMAGE_PATH = "./indicators/amaknabank.png"
    if findandclickimage(ZAAP_IMAGE_PATH):
        if locatecenterimage(AMAKNAVILLAGE_IMAGE_PATH):
            if findandclickimage(TPBUTTON_IMAGE_PATH):
                if findandclickimage(AMAKNABANK_IMAGE_PATH,ctrl=True):
                    return True
                return True
            return True
        return True
    
    return False



def findandclickimage(image_path, ctrl=False):
    print("🔍 Searching for image...")
    screenshot = pg.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)  
    template = cv2.imread(image_path, 0)  

    if template is None:
        print("Error: Zaap portal image not found!")
        return False

    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)  # Get best match location

    threshold = 0.8  
    if max_val >= threshold:
        x, y = max_loc
        pg.moveTo(x + template.shape[1] // 2, y + template.shape[0] // 2)  # Center on match
        if ctrl:
            keyboard.press_and_release("ctrl")
        pg.mouseDown()
        pg.mouseUp()
        print("✅ image found and clicked!")
        return True
    
    print("❌ image not found.")
    return False

def locatecenterimage(image_path, confidence=0.6):
    """Find an image on the screen and click it."""
    print(f"🔍 Searching for {image_path}...")
    
    location = pg.locateCenterOnScreen(image_path, confidence=confidence,grayscale=True)
    
    if location:
        x, y = location
        pg.moveTo(x, y)
        pg.mouseDown()
        pg.mouseUp()
        print(f"✅ Found and clicked {image_path} at ({x}, {y})")
        return True
    
    print(f"❌ {image_path} not found.")
    return False


def execute_events(events):
    """Replay the recorded events until stopped, combat is detected, or inventory is full."""
    global running
    running = True
    shift_held = False

    while running:
        if check_inventory_full():  
            print("📦 Inventory full! Stopping script and pressing 'H' to teleport.")
            keyboard.press_and_release("h")  # Simulate pressing 'H'
            running = False
            time.sleep(3)
            empty_inventory()

        if detect_combat():  
            print("⚔️ Stopping script due to combat detection!")
            running = False
            sys.exit(0)

        if not focus_game_window():
            time.sleep(1)
            continue
        
        for event in events:
            if not running:
                print("Replay stopped.")
                return
            
            event_type = event.get("type")
            delay = event.get("time", 0.01)  

            if event_type == "mouse_click":
                x, y = event["x"], event["y"]
                pg.moveTo(x, y)
                if shift_held:
                    keyboard.press("shift")
                pg.mouseDown()
                pg.mouseUp()
                if shift_held:
                    keyboard.release("shift")
                print(f"Clicked at ({x}, {y})")
            elif event_type == "shift_down":    
                shift_held = True
                keyboard.press("shift")
                print("Shift pressed")
            elif event_type == "shift_up":
                shift_held = False
                keyboard.release("shift")
                print("Shift released")

            time.sleep(delay)  

def stop_script():
    """Forcefully exit the script."""
    global running
    running = False
    print("Stopping script...")
    sys.exit(0)

# Hotkey to stop script
keyboard.add_hotkey("esc", stop_script)  

# Global flag
running = False
focus_game_window()
pg.FAILSAFE = True

print("Press ESC to force quit. Checking for combat & inventory every 2 seconds.")
execute_events(load_events())
