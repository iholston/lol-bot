"""
Main window that displays all the tabs.
"""

import ctypes; ctypes.windll.shcore.SetProcessDpiAwareness(0)  # This must be set before importing pyautogui/dpg
import multiprocessing; multiprocessing.freeze_support()  # https://stackoverflow.com/questions/24944558/pyinstaller-built-windows-exe-fails-with-multiprocessing
import time

import dearpygui.dearpygui as dpg

from lolbot.lcu.lcu_api import LCUApi
from lolbot.view.bot_tab import BotTab
from lolbot.view.accounts_tab import AccountsTab
from lolbot.view.config_tab import ConfigTab
from lolbot.view.http_tab import HTTPTab
from lolbot.view.logs_tab import LogsTab
from lolbot.view.about_tab import AboutTab

ICON_PATH = 'lolbot/resources/images/a.ico'


class MainWindow:
    """Class that displays the view"""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.tab_bar = None
        self.api = LCUApi()
        self.bot_tab = BotTab(self.api)
        self.accounts_tab = AccountsTab()
        self.config_tab = ConfigTab()
        self.https_tab = HTTPTab(self.api)
        self.logs_tab = LogsTab()
        self.about_tab = AboutTab()
        self.api.update_auth_timer()

    def show(self) -> None:
        """Renders view"""
        dpg.create_context()
        with dpg.window(label='', tag='primary window', width=self.width, height=self.height, no_move=True, no_resize=True, no_title_bar=True):
            with dpg.theme(tag="__hyperlinkTheme"):
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, [0, 0, 0, 0])
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [0, 0, 0, 0])
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [29, 151, 236, 25])
                    dpg.add_theme_color(dpg.mvThemeCol_Text, [29, 151, 236])
            with dpg.tab_bar() as self.tab_bar:
                self.bot_tab.create_tab(self.tab_bar)
                self.accounts_tab.create_tab(self.tab_bar)
                self.config_tab.create_tab(self.tab_bar)
                self.https_tab.create_tab(self.tab_bar)
                self.logs_tab.create_tab(self.tab_bar)
                self.about_tab.create_tab(self.tab_bar)
        dpg.create_viewport(title='LoL Bot', width=self.width, height=self.height, small_icon=ICON_PATH, resizable=False)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window('primary window', True)
        dpg.set_exit_callback(self.on_exit)
        panel_update_time = time.time()
        while dpg.is_dearpygui_running():
            current_time = time.time()
            if current_time - panel_update_time >= 0.3:
                self.bot_tab.update_bot_panel()
                self.bot_tab.update_info_panel()
                self.bot_tab.update_output_panel()
                panel_update_time = current_time
            dpg.render_dearpygui_frame()
        dpg.destroy_context()

    def on_exit(self):
        self.api.stop_timer()
        self.bot_tab.stop_bot()
