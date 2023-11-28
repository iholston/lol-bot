"""
User interface module that contains the main window
"""

import ctypes; ctypes.windll.shcore.SetProcessDpiAwareness(0)  # This must be set before importing pyautogui/dpg
import threading
import datetime
import multiprocessing

import dearpygui.dearpygui as dpg

from lolbot.common import api
from lolbot.common import utils
from lolbot.common.account import AccountManager
from lolbot.common.config import Constants
from lolbot.view.bot_tab import BotTab
from lolbot.view.accounts_tab import AccountsTab
from lolbot.view.config_tab import ConfigTab
from lolbot.view.http_tab import HTTPTab
from lolbot.view.logs_tab import LogsTab
from lolbot.view.about_tab import AboutTab


class MainWindow:
    """Class that displays the view"""

    def __init__(self, width: int, height: int) -> None:
        multiprocessing.freeze_support()  # https://stackoverflow.com/questions/24944558/pyinstaller-built-windows-exe-fails-with-multiprocessing
        Constants.create_dirs()

        self.account_manager = AccountManager()
        self.accounts = self.account_manager.get_all_accounts()
        self.message_queue = multiprocessing.Queue()
        self.output_queue = []
        self.connection = api.Connection()
        self.width = width
        self.height = height
        self.terminate = threading.Event()
        self.tab_bar = None
        self.bot_tab = BotTab(self.message_queue, self.terminate)
        self.accounts_tab = AccountsTab()
        self.config_tab = ConfigTab()
        self.https_tab = HTTPTab()
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
            with dpg.tab_bar(callback=self._tab_selected) as self.tab_bar:
                self.bot_tab.create_tab(self.tab_bar)
                self.accounts_tab.create_tab(self.tab_bar)
                self.config_tab.create_tab(self.tab_bar)
                self.https_tab.create_tab(self.tab_bar)
                self.logs_tab.create_tab(self.tab_bar)
                self.about_tab.create_tab(self.tab_bar)
        dpg.create_viewport(title='LoL Bot', width=self.width, height=self.height, small_icon=utils.resource_path(Constants.ICON_PATH), resizable=False)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window('primary window', True)
        dpg.set_exit_callback(self.bot_tab.stop_bot)
        while dpg.is_dearpygui_running():
            self._gui_updater()
            dpg.render_dearpygui_frame()
        self.terminate.set()
        dpg.destroy_context()

    def _tab_selected(self, sender, app_data, user_data) -> None:
        """Callback for tab select"""
        if app_data == self.logs_tab.id:
            self.logs_tab.create_log_table()
        if app_data == self.accounts_tab.id:
            self.accounts_tab.create_accounts_table()

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
