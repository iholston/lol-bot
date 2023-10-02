import dearpygui.dearpygui as dpg
import ctypes
import os
import subprocess
import datetime
import webbrowser
import constants
import ast
import json
import threading
import shutil

class Gui:
    """Class that displays the gui"""

    def __init__(self, width: int, height: int) -> None:
        user32 = ctypes.windll.user32
        f = open(constants.LOCAL_ACCOUNTS_PATH)
        self.screen_w = user32.GetSystemMetrics(78)
        self.screen_h = user32.GetSystemMetrics(79)
        self.width = width
        self.height = height
        self.tab_bar = None

        # Status Tab
        self.status_tab = None

        self.accounts_tab = None
        self.account_label_widget = None
        self.input_username_widget = None
        self.input_password_widget = None
        self.accounts_group = None

        self.logs_tab = None
        self.log_group = None

        self.settings_tab = None
        self.about_tab = None

        # Widgets
        self.start_button_widget = None
        self.path_feedback_widget = None
        self.color_picker_widget = None
        self.bot_status_text_widget = None

        # Vars
        self.red = (220, 20, 60)
        self.green = (124, 252, 0)
        self.color = ast.literal_eval(constants.TEXT_COLOR)
        self.color_update = False
        self.account_max_level = constants.ACCOUNT_MAX_LEVEL
        self.accounts = json.load(f)

        # Init
        dpg.create_context()

    def render(self):
        with dpg.window(label='',
                        tag='primary window',
                        width=self.width,
                        height=self.height,
                        no_move=True,
                        no_resize=True,
                        no_title_bar=True):
            with dpg.tab_bar() as self.tab_bar:
                self._create_status_tab()
                self._create_accounts_tab()
                self._create_logs_tab()
                self._create_settings_tab()
                self._create_about_tab()
        dpg.create_viewport(title='LoL Bot',
                            width=self.width,
                            height=self.height,
                            small_icon='a.ico',
                            large_icon='b.ico',
                            resizable=False,
                            x_pos=int(int(self.screen_w)/2 + self.width),
                            y_pos=int(int(self.screen_h)/2 - self.height/2)
                            )
        self._set_color()
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window('primary window', True)
        while dpg.is_dearpygui_running():
            self._updater()
            dpg.render_dearpygui_frame()


    def _create_status_tab(self):
        with dpg.tab(label="Status") as self.status_tab:
            dpg.add_spacer()
            with dpg.group(horizontal=True):
                dpg.add_input_text(
                    default_value='Bot Status',
                    width=90,
                    enabled=False
                )
                dpg.add_text(
                    tag="StatusText",
                    default_value="Ready to run",
                    color=self.green
                )
            dpg.add_spacer()
            dpg.add_text("Controls")
            with dpg.group(horizontal=True):
                dpg.add_button(label='Start', width=90)
                dpg.add_button(label='Pause', width=90)
                dpg.add_button(label='Update Path', width=90, callback=lambda: dpg.set_value(self.tab_bar, self.settings_tab))
            dpg.add_spacer()
            dpg.add_text(tag="Output", default_value="Output")
            dpg.add_input_text(multiline=True, default_value="", height=235, width=568, tab_input=True)

    def _create_accounts_tab(self):
        with dpg.tab(label="Accounts") as self.accounts_tab:
            dpg.add_spacer()
            dpg.add_text(tag="AccountsLabel", default_value="Add New Account", color=self.color)
            with dpg.group(horizontal=True):
                dpg.add_input_text(
                    default_value='Username',
                    width=100,
                    enabled=False
                )
                self.new_username_text_widget = dpg.add_input_text(
                    width=350,
                )
            with dpg.group(horizontal=True):
                dpg.add_input_text(
                    default_value='Password',
                    width=100,
                    enabled=False
                )
                self.new_password_text_widget = dpg.add_input_text(
                    width=350,
                )
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label='Submit',
                    width=100,
                    callback=self._submit_account
                )
                dpg.add_button(
                    label='Show in File Explorer',
                    callback=lambda: subprocess.Popen(
                        'explorer /select, {}'.format(os.path.dirname(os.getcwd()) + '\\resources\\accounts.json')),
                    width=350
                )
            dpg.add_spacer()
            dpg.add_spacer()
            dpg.add_separator()
            dpg.add_spacer()
            dpg.add_spacer()
            with dpg.collapsing_header(label="All Accounts", indent=3) as self.accounts_group:
                for account in reversed(self.accounts['accounts']):
                    with dpg.group(horizontal=True):
                        dpg.add_input_text(
                            default_value=account['username'],
                            width=150,
                            enabled=False
                        )
                        dpg.add_input_text(
                            default_value=account['password'],
                            width=150,
                            enabled=False
                        )
                        dpg.add_input_text(
                            default_value=account['leveled'],
                            width=150,
                            enabled=False
                        )

    def _create_logs_tab(self) -> None:
        """Creates Log Tab"""
        with dpg.tab(label="Logs") as self.logs_tab:
            with dpg.group(horizontal=True):
                dpg.add_text(tag="LogUpdatedTime", default_value='Last Updated: {}'.format(datetime.datetime.now()))
                dpg.add_button(label='Update', callback=self._refresh_logs)
                dpg.add_button(label='Clear', callback=self._clear_logs)
                dpg.add_button(
                    label='Show in File Explorer',
                    callback=lambda: subprocess.Popen(
                        'explorer /select, {}'.format(os.path.dirname(os.getcwd()) + '\\logs\\')),
                )
            dpg.add_spacer()
            dpg.add_separator()
            dpg.add_spacer()
            self._refresh_logs()

    def _create_settings_tab(self) -> None:
        """Creates Setttings Tab"""
        with dpg.tab(label="Settings") as self.settings_tab:
            dpg.add_spacer()
            dpg.add_text(
                tag="SettingsLabel",
                default_value="You may need/want to update some of these values",
                color=self.color
            )
            dpg.add_text(
                tag="LeagueDirDialog",
                default_value="Your League Installation Path is VALID",
                color=self.green
            )
            dpg.add_spacer()
            dpg.add_separator()
            dpg.add_spacer()
            with dpg.group(horizontal=True):
                dpg.add_input_text(
                    default_value='League Installation Path',
                    width=180,
                    enabled=False
                )
                dpg.add_input_text(
                    default_value=constants.LEAGUE_CLIENT_DIR,
                    width=350,
                    callback=self._set_dir
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
                    width=350,
                    callback=self._set_mode
                )
            with dpg.group(horizontal=True):
                dpg.add_input_text(
                    default_value='Account Max Level',
                    width=180,
                    enabled=False
                )
                dpg.add_input_int(
                    default_value=constants.ACCOUNT_MAX_LEVEL,
                    min_value=0,
                    step=1,
                    width=350,
                    callback=self._set_level
                )
            with dpg.group(horizontal=True):
                dpg.add_input_text(
                    default_value='App Text Color',
                    width=180,
                    enabled=False
                )
                with dpg.tree_node(label='Color', selectable=False):
                    dpg.add_color_picker(
                        self.color,
                        tag="ColorPicker",
                        label="Color Picker",
                        width=200,
                        callback=self._set_color
                    )

    def _create_about_tab(self) -> None:
        """Creates About Tab"""
        with dpg.tab(label="About") as self.about_tab:
            dpg.add_spacer()
            with dpg.group(horizontal=True):
                dpg.add_input_text(
                    default_value='Version',
                    width=100,
                    enabled=False
                )
                dpg.add_text(constants.VERSION)
            with dpg.group(horizontal=True):
                dpg.add_input_text(
                    default_value='Github',
                    width=100,
                    enabled=False
                )
                dpg.add_button(
                    label='www.github.com/iholston/lol-bot',
                    callback=lambda: webbrowser.open('www.github.com/iholston/lol-bot'))

    def _submit_account(self) -> None:
        """Adds a new account to accounts.json and updates gui"""
        self.accounts['accounts'].append({"username": dpg.get_value(self.new_username_text_widget),
                                          "password": dpg.get_value(self.new_password_text_widget),
                                          "leveled": False
                                          })
        dpg.configure_item(self.new_username_text_widget, default_value="")
        dpg.configure_item(self.new_password_text_widget, default_value="")
        with open(constants.LOCAL_ACCOUNTS_PATH, 'w') as outfile:
            outfile.write(json.dumps(self.accounts))
        dpg.configure_item("AccountsLabel", default_value="Account Successfully Added")
        threading.Timer(3.0, lambda: dpg.configure_item("AccountsLabel", default_value="Add New Account")).start()
        dpg.delete_item(self.accounts_group)
        with dpg.collapsing_header(label="All Accounts", indent=3, parent=self.accounts_tab) as self.accounts_group:
            for account in reversed(self.accounts['accounts']):
                with dpg.group(horizontal=True):
                    dpg.add_input_text(
                        default_value=account['username'],
                        width=150,
                        enabled=False
                    )
                    dpg.add_input_text(
                        default_value=account['password'],
                        width=150,
                        enabled=False
                    )
                    dpg.add_input_text(
                        default_value=account['leveled'],
                        width=150,
                        enabled=False
                    )

    def _refresh_logs(self) -> None:
        """Reads the logs folder and repopulates the logs tab"""
        if self.log_group is not None:
            dpg.delete_item(self.log_group)
        dpg.set_value('LogUpdatedTime', 'Last Updated: {}'.format(datetime.datetime.now()))
        with dpg.group(parent=self.logs_tab) as self.group:
            for filename in os.listdir(constants.LOCAL_LOG_PATH):
                f = os.path.join(constants.LOCAL_LOG_PATH, filename)
                if os.path.isfile(f):
                    with dpg.collapsing_header(label=filename, indent=3):
                        f = open(f, "r")
                        dpg.add_input_text(multiline=True, default_value=f.read(), height=300, width=600, tab_input=True)

    @staticmethod
    def _clear_logs(self) -> None:
        """Empties the log folder"""
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


    def _set_dir(self, sender) -> None:
        """Checks if directory exists and sets the Client Directory path"""
        constants.LEAGUE_CLIENT_DIR = dpg.get_value(sender)
        if os.path.exists(constants.LEAGUE_CLIENT_DIR):
            constants.persist()

    @staticmethod
    def _set_mode(self, sender) -> None:
        """Sets the game mode"""
        mode = dpg.get_value(sender)
        match mode:
            case "Intro":
                constants.GAME_LOBBY_ID = 830
            case "Beginner":
                constants.GAME_LOBBY_ID = 840
            case "Intermediate":
                constants.GAME_LOBBY_ID = 850
        constants.persist()

    @staticmethod
    def _set_level(self, sender) -> None:
        """Sets account max level"""
        constants.ACCOUNT_MAX_LEVEL = dpg.get_value(sender)
        constants.persist()

    def _set_color(self) -> None:
        """Sets text color"""
        constants.TEXT_COLOR = str(dpg.get_value(self.color_picker_widget))
        self.color = dpg.get_value(self.color_picker_widget)
        self.color_update = True
        constants.persist()

    def _updater(self) -> None:
        """Updates gui each frame"""

        # Check if League Path is correct
        if not os.path.exists(constants.LEAGUE_CLIENT_DIR):
            dpg.configure_item("StatusText", default_value="League Path is Invalid", color=self.red)
            dpg.configure_item("LeagueDirDialog", default_value="Your League Installation Path is INVALID", color=self.red)
        else:
            dpg.configure_item("StatusText", default_value="Ready to Run", color=self.color)
            dpg.configure_item("LeagueDirDialog", default_value="Your League Installation Path is VALID", color=self.color)

        # Update Text Colors
