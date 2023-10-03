"""
Where bot execution starts
"""

from gui import Gui

if __name__ == '__main__':
    gui: Gui = Gui(600, 420)
    gui.render()
