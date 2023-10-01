"""
Where bot execution starts
"""

import multiprocessing
from ctypes import windll
import sys
from gui import Gui
import dearpygui.dearpygui as dpg
import dearpygui.demo as demo

def is_admin():
    try:
        return windll.shell32.IsUserAnAdmin()
    except:
        return False

def demo1():
    dpg.create_context()
    dpg.create_viewport(title='Custom Title', width=600, height=600)

    demo.show_demo()

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == '__main__':
    # if not is_admin():
    #     windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    #     sys.exit()

    # demo1()
    width, height = 600, 420
    gui: Gui = Gui(width, height)
    gui.render()
    dpg.destroy_context()
