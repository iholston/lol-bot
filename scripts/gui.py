import dearpygui.dearpygui as dpg
from PIL import ImageColor
import constants
import ctypes
import os
import subprocess
import datetime
import webbrowser

class Gui:

    def __init__(self, width, height):
        user32 = ctypes.windll.user32
        self.screen_w = user32.GetSystemMetrics(78)
        self.screen_h = user32.GetSystemMetrics(79)
        self.width = width
        self.height = height
        self.tab_bar = None
        self.status_tab = None
        self.accounts_tab = None
        self.logs_tab = None
        self.settings_tab = None
        self.about_tab = None
        self.log_refresh_time = None
        self.color_picker = None
        self.minor_text_widgets = []
        dpg.create_context()

    def render(self):
        with dpg.window(label='', tag='primary window', width=self.width, height=self.height, no_move=True, no_resize=True, no_title_bar=True):
            with dpg.tab_bar() as self.tab_bar:
                self.create_status_tab()
                self.create_accounts_tab()
                self.create_logs_tab()
                self.create_settings_tab()
                self.create_about_tab()
        dpg.create_viewport(title='LoL Bot',
                            width=self.width,
                            height=self.height,
                            small_icon='a.ico',
                            large_icon='b.ico',
                            resizable=False,
                            x_pos=int(int(self.screen_w)/2 + self.width),
                            y_pos=int(int(self.screen_h)/2 - self.height/2)
                            )
        self.set_main_tab(self.status_tab)
        self.update_minor_text_color_callback()
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window('primary window', True)
        dpg.start_dearpygui()

    def create_status_tab(self):
        with dpg.tab(label="Status") as self.status_tab:
            dpg.add_spacer()
            with dpg.group(horizontal=True):
                dpg.add_input_text(
                    default_value='Bot Status',
                    width=100,
                    enabled=False
                )
                self.minor_text_widgets.append(dpg.add_text("Not Running.."))
            dpg.add_spacer()
            self.minor_text_widgets.append(dpg.add_text("Controls"))
            with dpg.group(horizontal=True):
                dpg.add_button(label='Start', width=100)
                dpg.add_button(label='Pause', width=100)
                dpg.add_button(label='Update Path', width=100, callback=self.update_path_callback)
            dpg.add_spacer()
            self.minor_text_widgets.append(dpg.add_text("Output"))
            dpg.add_input_text(multiline=True, default_value="", height=235, width=568, tab_input=True)


    def create_accounts_tab(self):
        with dpg.tab(label="Accounts") as self.accounts_tab:
            dpg.add_spacer()
            self.minor_text_widgets.append(dpg.add_text("Add New Account"))
            with dpg.group(horizontal=True):
                dpg.add_input_text(
                    default_value='Username',
                    width=100,
                    enabled=False
                )
                dpg.add_input_text(
                    width=350,
                )
            with dpg.group(horizontal=True):
                dpg.add_input_text(
                    default_value='Password',
                    width=100,
                    enabled=False
                )
                dpg.add_input_text(
                    password=True,
                    width=350,
                )
            dpg.add_button(
                label='Submit',
                width=100,
            )
            dpg.add_spacer()
            dpg.add_separator()
            dpg.add_spacer()
            dpg.add_button(
                    label='Show in File Explorer',
                    callback=lambda: subprocess.Popen('explorer /select, {}'.format(os.path.dirname(os.getcwd()) + '\\resources\\accounts.json')),
                    width=575
                )
            dpg.add_spacer()
            with dpg.collapsing_header(label="All Accounts", indent=3):
                pass

    def create_logs_tab(self):
        with dpg.tab(label="Logs") as self.logs_tab:
            dpg.add_spacer()
            dpg.add_button(
                label='Show in File Explorer',
                callback=lambda: subprocess.Popen(
                    'explorer /select, {}'.format(os.path.dirname(os.getcwd()) + '\\logs\\')),
                width=575
            )
            with dpg.group(horizontal=True):
                dpg.add_button(label='Update', callback=self.refresh_logs_callback)
                self.log_refresh_time = dpg.add_text('Last Updated: {}'.format(datetime.datetime.now()))
                self.minor_text_widgets.append(self.log_refresh_time)
            dpg.add_spacer()
            with dpg.group() as self.group:
                for filename in os.listdir(constants.LOG_PATH):
                    f = os.path.join(constants.LOG_PATH, filename)
                    if os.path.isfile(f):
                        with dpg.collapsing_header(label=filename, indent=3):
                            f = open(f, "r")
                            dpg.add_input_text(multiline=True, default_value=f.read(), height=300, width=600, tab_input=True)

    def create_settings_tab(self):
        with dpg.tab(label="Settings") as self.settings_tab:
            dpg.add_spacer()
            self.minor_text_widgets.append(dpg.add_text('You may need/want to update some of these values:'))
            with dpg.group(horizontal=True):
                dpg.add_input_text(
                    default_value='League Installation Path',
                    width=180,
                    enabled=False
                )
                dpg.add_input_text(
                    default_value=constants.LEAGUE_CLIENT_DIR,
                    width=350
                )
            with dpg.group(horizontal=True):
                dpg.add_input_text(
                    default_value='Game Mode',
                    width=180,
                    enabled=False
                )
                dpg.add_combo(
                    items=['Intro', 'Beginner', 'Intermediate'],
                    default_value='Beginner',
                    width=350
                )
            with dpg.group(horizontal=True):
                dpg.add_input_text(
                    default_value='Account Max Level',
                    width=180,
                    enabled=False
                )
                dpg.add_input_int(
                    default_value=30,
                    min_value=0,
                    step=1,
                    width=350
                )
            with dpg.group(horizontal=True):
                dpg.add_input_text(
                    default_value='App Minor Text Color',
                    width=180,
                    enabled=False
                )
                with dpg.tree_node(label='Color', selectable=False):
                    self.color_picker = dpg.add_color_picker((124,252,0), label="Color Picker", width=200, callback=self.update_minor_text_color_callback)

    def create_about_tab(self):
        with dpg.tab(label="About") as self.about_tab:
            dpg.add_spacer()
            dpg.add_input_text(
                default_value='Version',
                width=100,
                label=' ' + constants.VERSION,
                enabled=False
            )
            with dpg.group(horizontal=True):
                dpg.add_input_text(
                    default_value='Github',
                    width=100,
                    enabled=False
                )
                dpg.add_button(
                    label='www.github.com/iholston/lol-bot',
                    callback=lambda: webbrowser.open('www.github.com/iholston/lol-bot'))

    def set_main_tab(self, tab: str) -> None:
        dpg.set_value(self.tab_bar, tab)

    def refresh_logs_callback(self):
        dpg.delete_item(self.group)
        dpg.set_value(self.log_refresh_time, 'Last Updated: {}'.format(datetime.datetime.now()))
        with dpg.group(parent=self.logs_tab) as self.group:
            for filename in os.listdir(constants.LOG_PATH):
                f = os.path.join(constants.LOG_PATH, filename)
                if os.path.isfile(f):
                    with dpg.collapsing_header(label=filename, indent=3):
                        f = open(f, "r")
                        dpg.add_input_text(multiline=True, default_value=f.read(), height=300, width=600, tab_input=True)

    def update_minor_text_color_callback(self):
        for widget in self.minor_text_widgets:
            dpg.configure_item(widget, color=dpg.get_value(self.color_picker))

    def update_path_callback(self):
        self.set_main_tab(self.settings_tab)
        