"""
View tab that sets configurations for the bot.
"""

import os
from tkinter import Tk
from tkinter.filedialog import askdirectory

import dearpygui.dearpygui as dpg

import lolbot.common.config as config
from lolbot.common.config import FONT_PATH
from lolbot.system import OS

TAG_LEAGUE_PATH = "LeaguePath"
TAG_LOBBY = "Lobby"
TAG_MAX_LEVEL = "AccountMaxLevel"
TAG_FPS = "FPS"
TAG_CJK_SUPPORT = "CJKSupport"
TAG_FONT_SCALE_GROUP = "FontScaleGroup"
TAG_FONT_SCALE = "FontScale"


class ConfigTab:
    """Class that creates the ConfigTab and sets configurations for the bot"""

    def __init__(self) -> None:
        self.id = None
        self.font = None
        self.config = config.load_config()

    def create_tab(self, parent: int) -> None:
        """Creates Settings Tab"""
        with dpg.tab(label="Config", parent=parent) as self.id:
            self.add_config_header()
            self.add_install_path_entry()
            self.add_game_mode_entry()
            self.add_max_level_entry()
            self.add_fps_entry()
            if OS == "Windows":
                self.add_language_support()
        if OS == "Windows":
            self.language_support()

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
            with dpg.group(horizontal=True):
                dpg.add_input_text(default_value="League Install Folder", width=180, enabled=False)
                dpg.add_input_text(tag=TAG_LEAGUE_PATH, default_value=dv, width=320, callback=self.save_config)
                dpg.add_button(label="Browse", width=52, callback=self.open_file_selector)
        else:
            dv = self.config.macos_install_dir
            with dpg.group(horizontal=True):
                dpg.add_input_text(default_value="League Install Folder", width=180, enabled=False)
                dpg.add_input_text(tag=TAG_LEAGUE_PATH, default_value=dv, width=380, callback=self.save_config) # tkinter dialog does not work on mac with dearpygui https://github.com/hoffstadt/DearPyGui/issues/2338

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

    def add_language_support(self):
        with dpg.group(horizontal=True):
            dpg.add_input_text(default_value="CJK Language Support", width=180, enabled=False)
            dpg.add_checkbox(tag=TAG_CJK_SUPPORT, default_value=self.config.cjk_support, callback=self.language_support)
        with dpg.group(tag=TAG_FONT_SCALE_GROUP, horizontal=True):
            dpg.add_input_text(default_value="Font Scaling", width=180, enabled=False)
            dpg.add_input_float(tag=TAG_FONT_SCALE,
                              default_value=self.config.font_scale,
                              min_value=0,
                              step=.1,
                              width=380,
                              callback=self.language_support)

    def language_support(self):
        if dpg.get_value(TAG_CJK_SUPPORT):
            if not self.font:
                with dpg.font_registry():
                    with dpg.font(FONT_PATH, 30) as self.font:
                        dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)
                        dpg.add_font_range_hint(dpg.mvFontRangeHint_Japanese)
                        dpg.add_font_range_hint(dpg.mvFontRangeHint_Korean)
            dpg.bind_font(self.font)
            dpg.show_item(TAG_FONT_SCALE_GROUP)
            dpg.set_global_font_scale(dpg.get_value(TAG_FONT_SCALE))
        else:
            dpg.bind_font("ProggyClean.ttf")
            dpg.set_global_font_scale(1)
            dpg.hide_item(TAG_FONT_SCALE_GROUP)
        self.save_config()

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
        self.config.cjk_support = dpg.get_value(TAG_CJK_SUPPORT)
        self.config.font_scale = round(dpg.get_value(TAG_FONT_SCALE), 1)
        config.save_config(self.config)
