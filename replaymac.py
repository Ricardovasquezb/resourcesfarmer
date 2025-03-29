import time
import json
import pyautogui as pg
import keyboard
import sys
import subprocess

def focus_game_window():
    """Find and activate the game window containing 'Lost-Ocr' for Windows and macOS."""
    
    try:
        script = 'tell application "Dofus" to activate'
        subprocess.run(["osascript", "-e", script], check=True)
        time.sleep(1)  # Small delay to ensure window is focused
        print("Game window activated on macOS!")
        return True
    except Exception as e:
        print(f"Error activating game window on macOS: {e}")
        return False
    

def load_events(filename="events.json"):
    """Load recorded events from a JSON file."""
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print("Error: events.json not found!")
        return []

def execute_events(events):
    """Replay the recorded events while handling shift key issues."""
    global running
    running = True
    shift_held = False  # Tracks shift key state
    ctrl_held = False  # Tracks ctrl key state

    while running:

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
                pg.mouseDown()
                pg.mouseUp()
                print(f"Clicked at ({x}, {y}) {'with SHIFT' if shift_held else ''}")
            
            elif event_type == "shift_down":    
                if not shift_held:  # Prevent redundant key presses
                    pg.keyDown("shift")
                    shift_held = True
                    print("Shift pressed")
            
            elif event_type == "shift_up":
                if shift_held:  # Prevent redundant key releases
                    pg.keyUp("shift")
                    shift_held = False
                    print("Shift released")

            elif event_type == "ctrl_down":    
                if not ctrl_held:  # Prevent redundant key presses
                    pg.keyDown("ctrl")
                    ctrl_held = True
                    print("ctrl pressed")
            
            elif event_type == "ctrl_up":
                if ctrl_held:  # Prevent redundant key releases
                    pg.keyUp("ctrl")
                    ctrl_held = False
                    print("ctrl released")

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
