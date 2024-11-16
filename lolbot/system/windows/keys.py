import keyboard

def press_and_release(key: str):
    keyboard.press_and_release(key)

def key_down(key: str):
    keyboard.press(key)

def key_up(key: str):
    keyboard.release(key)

