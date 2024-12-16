"""
View tab that sets configurations for the bot.
"""

import os
from tkinter import Tk
from tkinter.filedialog import askdirectory

import dearpygui.dearpygui as dpg

import lolbot.common.config as config
from lolbot.system import OS, font_path

TAG_LEAGUE_PATH = "LeaguePath"
TAG_LOBBY = "Lobby"
TAG_MAX_LEVEL = "AccountMaxLevel"
TAG_FPS = "FPS"


class ConfigTab:
    """Class that creates the ConfigTab and sets configurations for the bot"""

    def __init__(self) -> None:
        self.id = None
        self.config = config.load_config()
        try:
            dpg.create_context()
            with dpg.font_registry():
                with dpg.font(font_path, 13) as self.font:
                    dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)
                    dpg.add_font_range_hint(dpg.mvFontRangeHint_Japanese)
                    dpg.add_font_range_hint(dpg.mvFontRangeHint_Korean)
        except:
            self.font = None

    def create_tab(self, parent: int) -> None:
        """Creates Settings Tab"""
        with dpg.tab(label="Config", parent=parent) as self.id:
            self.add_config_header()
            self.add_install_path_entry()
            self.add_game_mode_entry()
            self.add_max_level_entry()
            self.add_fps_entry()

    @staticmethod
    def add_config_header():
        dpg.add_spacer()
        with dpg.group(horizontal=True):
            dpg.add_button(label="Configuration", enabled=False, width=180)
            dpg.add_button(label="Value", enabled=False, width=380)
        dpg.add_spacer()
        dpg.add_spacer()

    def add_install_path_entry(self):
        if OS == "Windows":
            dv = self.config.windows_install_dir
        else:
            dv = self.config.macos_install_dir
        with dpg.group(horizontal=True):
            dpg.add_input_text(default_value="League Install Folder", width=180, enabled=False)
            dpg.add_input_text(tag=TAG_LEAGUE_PATH, default_value=dv, width=320, callback=self.save_config)
            dpg.add_button(label="Browse", width=52, callback=self.open_file_selector)
            if self.font:
                dpg.bind_item_font(TAG_LEAGUE_PATH, self.font)

    def open_file_selector(self):
        Tk().withdraw()
        filename = askdirectory()
        if filename:
            dpg.configure_item(TAG_LEAGUE_PATH, default_value=filename)
            self.save_config()

    def add_game_mode_entry(self):
        with dpg.group(horizontal=True):
            dpg.add_input_text(default_value="Game Mode", width=180, readonly=True)
            lobby = int(self.config.lobby)
            if lobby < 870:
                lobby += 40
            dpg.add_combo(tag=TAG_LOBBY,
                          items=list(config.BOT_LOBBIES.keys()),
                          default_value=list(config.BOT_LOBBIES.keys())[list(config.BOT_LOBBIES.values()).index(lobby)],
                          width=380,
                          callback=self.save_config)

    def add_max_level_entry(self):
        with dpg.group(horizontal=True):
            dpg.add_input_text(default_value='Account Max Level', width=180, enabled=False)
            dpg.add_input_int(tag=TAG_MAX_LEVEL,
                              default_value=self.config.max_level,
                              min_value=0,
                              step=1,
                              width=380,
                              callback=self.save_config)

    def add_fps_entry(self):
        with dpg.group(horizontal=True):
            dpg.add_input_text(default_value="FPS", width=180, enabled=False)
            dpg.add_combo(tag=TAG_FPS,
                          items=list(config.FPS_OPTIONS.keys()),
                          default_value=list(config.FPS_OPTIONS.keys())[list(config.FPS_OPTIONS.values()).index(self.config.fps_type)],
                          width=380,
                          callback=self.save_config)

    def save_config(self):
        if OS == "Windows":
            if os.path.exists(dpg.get_value(TAG_LEAGUE_PATH)):
                self.config.windows_install_dir = dpg.get_value(TAG_LEAGUE_PATH)
        else:
            if os.path.exists(dpg.get_value(TAG_LEAGUE_PATH)):
                self.config.macos_install_dir = dpg.get_value(TAG_LEAGUE_PATH)
        self.config.lobby = config.BOT_LOBBIES.get(dpg.get_value(TAG_LOBBY))
        self.config.max_level = dpg.get_value(TAG_MAX_LEVEL)
        self.config.fps_type = config.FPS_OPTIONS.get(dpg.get_value(TAG_FPS))
        config.save_config(self.config)
