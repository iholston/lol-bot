"""
Where bot execution starts
"""

from lolbot.view.main_window import MainWindow

if __name__ == '__main__':
    import lolbot.system.windows.cmd as cmd

    #cmd.run(cmd.LAUNCH_CLIENT)
    gui: MainWindow = MainWindow()
    gui.show()
