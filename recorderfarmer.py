import time
import json
import pygetwindow as gw
import pyautogui
from pynput import mouse, keyboard
import sys
import subprocess

if sys.platform == "win32":
    import pygetwindow as gw

events = []
recording = False
start_time = None
shift_held = False  # Track if Shift is currently held
game_window = None  # Store the game window


def focus_game_window():
    """Find and activate the game window containing 'Lost-Ocr' for Windows and macOS."""
    
    if sys.platform == "win32":  # Windows
        windows = gw.getWindowsWithTitle("Lost-Ocr")#name of the char to invoke the window
        if windows:
            game_window = windows[0]
            game_window.activate()
            print("Game window activated on Windows!")
            return True
        else:
            print("Game window not found on Windows!")
            return False
    
    elif sys.platform == "darwin":  # macOS
        try:
            script = 'tell application "Lost-Ocr" to activate'
            subprocess.run(["osascript", "-e", script], check=True)
            time.sleep(1)  # Small delay to ensure window is focused
            print("Game window activated on macOS!")
            return True
        except Exception as e:
            print(f"Error activating game window on macOS: {e}")
            return False
    
    else:
        print("Unsupported OS!")
        return False


def on_click(x, y, button, pressed):
    """Record mouse clicks instantly without time property."""
    global recording

    if recording and pressed:
        events.append({"type": "mouse_click", "x": x, "y": y})
        print(f"Mouse Click at ({x}, {y}) recorded")


def on_press(key):
    """Handle key presses, toggle recording on `.` and track Shift state."""
    global recording, start_time, events, shift_held

    try:
        key_data = key.char
    except AttributeError:
        key_data = str(key)

    if key_data == ".":
        if not recording:
            events = []  # Reset events list
            recording = True
            print("Recording started!")
        else:
            recording = False
            print("Recording stopped!")
            with open("events.json", "w") as file:
                json.dump(events, file, indent=4)
            print("Recorded events saved to events.json")

    if recording:
        if key_data == "Key.shift" and not shift_held:
            shift_held = True
            events.append({"type": "shift_down"})
            print("Shift pressed")

        elif key_data != "Key.shift":
            events.append({"type": "key_press", "key": key_data})


def on_release(key):
    """Detect when Shift is released."""
    global shift_held

    try:
        key_data = key.char
    except AttributeError:
        key_data = str(key)

    if key_data == "Key.shift" and shift_held:
        shift_held = False
        events.append({"type": "shift_up"})
        print("Shift released")


# Start listeners
focus_game_window()
mouse_listener = mouse.Listener(on_click=on_click)
keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)

mouse_listener.start()
keyboard_listener.start()

# Wait for user to press `.`
while True:
    time.sleep(0.1)
