"""
Where bot execution starts
"""

import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(0)  # This must be set before importing pyautogui
from app.gui.gui import Gui

if __name__ == '__main__':
    gui: Gui = Gui(600, 420)
    gui.render()
