"""
Where bot execution starts
"""

from lolbot.view.main_window import MainWindow


if __name__ == '__main__':
    gui: MainWindow = MainWindow(600, 420)
    gui.show()
