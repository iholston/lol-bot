"""
Where bot execution starts
"""

from lolbot.view.main_window import MainWindow

if __name__ == '__main__':
    gui: MainWindow = MainWindow()
    gui.show()
