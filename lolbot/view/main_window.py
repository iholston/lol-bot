"""
User interface module that contains the main window
"""

import ctypes; ctypes.windll.shcore.SetProcessDpiAwareness(0)  # This must be set before importing pyautogui/dpg
import datetime
import multiprocessing

import dearpygui.dearpygui as dpg

from lolbot.common import api, account
from .bot_tab import BotTab
from .accounts_tab import AccountsTab
from .config_tab import ConfigTab
from .http_tab import HTTPTab
from .ratio_tab import RatioTab
from .logs_tab import LogsTab
from .about_tab import AboutTab
from ..common.config import ICON_PATH


class MainWindow:
    """Class that displays the view"""

    def __init__(self, width: int, height: int) -> None:
        self.accounts = account.get_all_accounts()
        self.message_queue = multiprocessing.Queue()
        self.output_queue = []
        self.connection = api.Connection()
        self.width = width
        self.height = height
        self.terminate = False
        self.tab_bar = None
        self.bot_tab = BotTab(self.message_queue, self.terminate)
        self.accounts_tab = AccountsTab()
        self.config_tab = ConfigTab()
        self.https_tab = HTTPTab()
        self.ratio_tab = RatioTab()
        self.logs_tab = LogsTab()
        self.about_tab = AboutTab()

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
                # self.ratio_tab.create_tab(self.tab_bar)
                self.logs_tab.create_tab(self.tab_bar)
                self.about_tab.create_tab(self.tab_bar)
        dpg.create_viewport(title='LoL Bot', width=self.width, height=self.height, small_icon=ICON_PATH, resizable=False)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window('primary window', True)
        dpg.set_exit_callback(self.bot_tab.stop_bot)
        while dpg.is_dearpygui_running():
            self._gui_updater()
            dpg.render_dearpygui_frame()
        self.terminate = True
        dpg.destroy_context()

    def _gui_updater(self) -> None:
        """Updates view each frame, displays up-to-date bot info"""
        if not self.message_queue.empty():
            display_message = ""
            self.output_queue.append(self.message_queue.get())
            if len(self.output_queue) > 12:
                self.output_queue.pop(0)
            for msg in self.output_queue:
                if "Clear" in msg:
                    self.output_queue = []
                    display_message = ""
                    break
                elif "INFO" not in msg and "ERROR" not in msg and "WARNING" not in msg:
                    display_message += "[{}] [INFO   ] {}\n".format(datetime.datetime.now().strftime("%H:%M:%S"), msg)
                else:
                    display_message += msg + "\n"
            dpg.configure_item("Output", default_value=display_message.strip())
            if "Bot Successfully Terminated" in display_message:
                self.output_queue = []
