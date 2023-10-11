import ctypes
import os
import subprocess
import webbrowser
import multiprocessing
import ast
import shutil
from time import sleep
from datetime import datetime
import dearpygui.dearpygui as dpg
import pyautogui
from app.common import constants, api, utils, account
from .bot_tab import BotTab
from .accounts_tab import AccountsTab
from  .config_tab import ConfigTab
from .http_tab import HTTPTab


class Gui:
    """Class that displays the gui"""

    def __init__(self, width: int, height: int) -> None:
        user32 = ctypes.windll.user32
        self.accounts = account.get_all_accounts()
        self.message_queue = multiprocessing.Queue()
        self.connection = api.Connection()
        self.width = width
        self.height = height
        self.x_pos = int(int(user32.GetSystemMetrics(78)) / 2 + self.width)
        self.y_pos = int(int(user32.GetSystemMetrics(79)) / 2 - self.height / 2)
        self.terminate = False

        self.tab_bar = None
        self.bot_tab = BotTab(self.message_queue, self.terminate)
        self.accounts_tab = AccountsTab()
        self.config_tab = ConfigTab()
        self.https_tab = HTTPTab()
        self.info_terminate = False
        self.output_queue = []

        self.ratio_tab = None
        self.lcu_tab = None
        self.logs_tab = None
        self.logs_group = None
        self.ratio_window_title = ""
        self.league_patch = ''
        self.color = ast.literal_eval(constants.TEXT_COLOR)
        self.color_update = False
        self.color_editable = []
        self.about_tab = None

        dpg.create_context()

    def render(self):
        """Displays dpg gui"""
        with dpg.window(label='', tag='primary window', width=self.width, height=self.height, no_move=True, no_resize=True, no_title_bar=True):
            with dpg.tab_bar() as self.tab_bar:
                self.bot_tab.create_tab(self.tab_bar)
                self.accounts_tab.create_tab(self.tab_bar)
                self.config_tab.create_tab(self.tab_bar)
                self.https_tab.create_tab(self.tab_bar)
                self.create_ratio_tab()
                self.create_logs_tab()
                self.create_about_tab()
        dpg.create_viewport(title='LoL Bot', width=self.width, height=self.height, small_icon='a.ico', large_icon='b.ico', resizable=False, x_pos=self.x_pos, y_pos=self.y_pos)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window('primary window', True)
        while dpg.is_dearpygui_running():
            self._gui_updater()
            dpg.render_dearpygui_frame()
        dpg.destroy_context()
        self.bot_tab.stop_bot()

    def create_ratio_tab(self):
        with dpg.tab(label="Ratio") as self.https_tab:
            dpg.add_text("Build Ratio")
            dpg.add_combo(items=['Riot Client', 'League Client', 'Game'], default_value='League Client', width=500)
            dpg.add_spacer()
            with dpg.group(horizontal=True):
                dpg.add_input_text(label="BuildRatio", default_value="Start capture and hover mouse to capture coordinates", multiline=True, width=500, height=109, callback=self._build_ratio)
                dpg.add_button(label="Capture", width=60)
            dpg.add_spacer()
            dpg.add_spacer()
            dpg.add_spacer()
            dpg.add_separator()
            dpg.add_spacer()
            dpg.add_text("Test Ratio")
            dpg.add_combo(items=['Riot Client', 'League Client', 'Game'], default_value='League Client', width=500)
            dpg.add_spacer()
            with dpg.group(horizontal=True):
                dpg.add_input_text(default_value="Add ratio with parenthesis, separate multiple with a comma\ni.e. (.2023, .3033), (.3333, .4444)", multiline=True, width=500, height=109)
                dpg.add_button(label="Test", width=60)

    def _build_ratio(self):
        while True:
            sleep(1)
            p = pyautogui.position()
            x1, y1, x2, y2 = utils.size()
            rx = (p[0] - x1) / (x2 - x1)
            ry = (p[1] - y1) / (y2 - y1)
            x = dpg.get_value("BuildRatio")
            x += "\n({}, {})".format(round(rx, 4), round(ry, 4))
            dpg.configure_item("BuildRatio", default_value=x)

    def create_logs_tab(self) -> None:
        """Creates Log Tab"""
        with dpg.tab(label="Logs") as self.logs_tab:
            with dpg.window(label="Delete Files", modal=True, show=False, tag="DeleteFiles", pos=[115, 130]):
                dpg.add_text("All files in the logs folder will be deleted")
                dpg.add_separator()
                dpg.add_spacer()
                dpg.add_spacer()
                dpg.add_spacer()
                with dpg.group(horizontal=True, indent=75):
                    dpg.add_button(label="OK", width=75, callback=self._clear_logs)
                    dpg.add_button(label="Cancel", width=75, callback=lambda: dpg.configure_item("DeleteFiles", show=False))
            dpg.add_spacer()
            with dpg.group(horizontal=True):
                self.color_editable.append(dpg.add_text(tag="LogUpdatedTime", default_value='Last Updated: {}'.format(datetime.now()), color=self.color))
                dpg.add_button(label='Update', callback=self.create_log_table)
                dpg.add_button(label='Clear', callback=lambda: dpg.configure_item("DeleteFiles", show=True))
                dpg.add_button(label='Show in File Explorer', callback=lambda: subprocess.Popen('explorer /select, {}'.format(os.path.dirname(os.getcwd()) + '\\logs\\')))
            dpg.add_spacer()
            dpg.add_separator()
            dpg.add_spacer()
            self.create_log_table()

    def create_log_table(self) -> None:
        """Reads in logs from the logs folder and populates the logs tab"""
        if self.logs_group is not None:
            dpg.delete_item(self.logs_group)
        dpg.set_value('LogUpdatedTime', 'Last Updated: {}'.format(datetime.now()))
        with dpg.group(parent=self.logs_tab) as self.logs_group:
            for filename in os.listdir(constants.LOCAL_LOG_PATH):
                f = os.path.join(constants.LOCAL_LOG_PATH, filename)
                if os.path.isfile(f):
                    with dpg.collapsing_header(label=filename):
                        f = open(f, "r")
                        dpg.add_input_text(multiline=True, default_value=f.read(), height=300, width=600, tab_input=True)

    def _clear_logs(self) -> None:
        """Empties the log folder"""
        dpg.configure_item("DeleteFiles", show=False)
        folder = constants.LOCAL_LOG_PATH
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
        self.create_log_table()



    def _update_color(self, sender) -> None:
        """Sets text color"""
        constants.TEXT_COLOR = str(dpg.get_value(sender))
        self.color = dpg.get_value(sender)
        self.color_update = True
        constants.persist()

    def create_about_tab(self) -> None:
        """Creates About Tab"""
        with dpg.tab(label="About") as self.about_tab:
            dpg.add_spacer()
            with dpg.group(horizontal=True):
                dpg.add_button(label='Bot Version', width=100, enabled=False)
                self.color_editable.append(dpg.add_text(default_value=constants.VERSION, color=self.color))
            with dpg.group(horizontal=True):
                dpg.add_button(label='Github', width=100, enabled=False)
                dpg.add_button(label='www.github.com/iholston/lol-bot', callback=lambda: webbrowser.open('www.github.com/iholston/lol-bot'))
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("Open link in webbrowser")
            dpg.add_spacer()
            dpg.add_input_text(multiline=True, default_value=self._notes_text(), height=288, width=568, enabled=False)

    def _gui_updater(self) -> None:
        """Updates gui each frame, displays up to date bot info"""
        if not self.message_queue.empty():
            display_message = ""
            self.output_queue.append(self.message_queue.get())
            if len(self.output_queue) > 12:
                self.output_queue.pop(0)
            for msg in self.output_queue:
                display_message += msg + "\n"
            dpg.configure_item("Output", default_value=display_message)
            if "Bot Successfully Terminated" in display_message:
                self.output_queue = []
        if self.color_update:
            self.color_update = False
            for item in self.color_editable:
                dpg.configure_item(item, color=self.color)




    @staticmethod
    def _notes_text() -> str:
        """Sets text in About Text box"""
        return "\t\t\t\t\t\t\t\t\tNotes\n\nIf you have any problems create an issue on the github repo\nLeave a star maybe <3\n\nKnown Issues:\n\n- {Issue List}"
