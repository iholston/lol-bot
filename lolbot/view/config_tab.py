"""
View tab that sets configurations for the bot.
"""

import os

import dearpygui.dearpygui as dpg

import lolbot.common.config as config

TAG_LEAGUE_PATH = "LeaguePath"
TAG_LOBBY = "Lobby"
TAG_MAX_LEVEL = "AccountMaxLevel"
TAG_FPS = "FPS"
TAG_FONT_PATH = "FontPath"
TAG_FONT_SIZE = "FontSize"
TAG_FONT_SCALE = "FontScale"
TAG_FONT_STATUS = "FontStatus"
TAG_FONT_RESTART_NOTICE = "FontRestartNotice"


class ConfigTab:
    """Class that creates the ConfigTab and sets configurations for the bot"""

    def __init__(self) -> None:
        self.id = None
        self.font = None
        self.font_registry = None
        self.config = config.load_config()

    def create_tab(self, parent: int) -> None:
        """Creates Settings Tab"""
        with dpg.tab(label="Config", parent=parent) as self.id:
            self.add_config_header()
            self.add_install_path_entry()
            self.add_game_mode_entry()
            self.add_max_level_entry()
            self.add_fps_entry()
            self.add_font_settings()
        

    @staticmethod
    def add_config_header():
        dpg.add_spacer()
        with dpg.group(horizontal=True):
            dpg.add_button(label="Configuration", enabled=False, width=180)
            dpg.add_button(label="Value", enabled=False, width=380)
        dpg.add_spacer()
        dpg.add_spacer()

    def add_install_path_entry(self):
        dv = self.config.macos_install_dir
        with dpg.group(horizontal=True):
            dpg.add_input_text(default_value="League Install Folder", width=180, enabled=False)
            dpg.add_input_text(tag=TAG_LEAGUE_PATH, default_value=dv, width=380, callback=self.save_config) # tkinter dialog does not work on mac with dearpygui https://github.com/hoffstadt/DearPyGui/issues/2338

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

    def add_font_settings(self):
        with dpg.group(horizontal=True):
            dpg.add_input_text(default_value="Font Path", width=180, enabled=False)
            dpg.add_input_text(tag=TAG_FONT_PATH, default_value=self.config.font_path, width=380, callback=self.apply_font_settings)
        with dpg.group(horizontal=True):
            dpg.add_input_text(default_value="Font Size", width=180, enabled=False)
            dpg.add_input_int(tag=TAG_FONT_SIZE,
                              default_value=self.config.font_size,
                              min_value=8,
                              max_value=36,
                              step=1,
                              width=380,
                              callback=self.on_font_size_change)
        with dpg.group(horizontal=True):
            dpg.add_input_text(default_value="Font Scale", width=180, enabled=False)
            dpg.add_input_float(tag=TAG_FONT_SCALE,
                                default_value=self.config.font_scale,
                                min_value=0.4,
                                max_value=1.0,
                                step=0.05,
                                width=380,
                                callback=self.apply_font_settings)
        dpg.add_text(tag=TAG_FONT_STATUS, default_value="", color=(255, 92, 92))
        dpg.add_text(tag=TAG_FONT_RESTART_NOTICE, default_value="", color=(255, 200, 92))


    def apply_font_settings(self):
        font_path = dpg.get_value(TAG_FONT_PATH).strip()
        font_scale = round(dpg.get_value(TAG_FONT_SCALE), 2)
        try:
            if font_path and os.path.exists(font_path):
                dpg.set_global_font_scale(max(0.4, min(1.0, font_scale)))
                dpg.set_value(TAG_FONT_STATUS, "")
            else:
                dpg.set_value(TAG_FONT_STATUS, "Font path not found. Please enter a valid file path.")
        except Exception:
            dpg.set_value(TAG_FONT_STATUS, "Font path not found. Please enter a valid file path.")
        self.save_config()

    def on_font_size_change(self):
        dpg.set_value(TAG_FONT_RESTART_NOTICE, "Font size changes require app restart to take effect.")
        self.save_config()

    def save_config(self):
        if os.path.exists(dpg.get_value(TAG_LEAGUE_PATH)):
            self.config.macos_install_dir = dpg.get_value(TAG_LEAGUE_PATH)
        self.config.lobby = config.BOT_LOBBIES.get(dpg.get_value(TAG_LOBBY))
        self.config.max_level = dpg.get_value(TAG_MAX_LEVEL)
        self.config.fps_type = config.FPS_OPTIONS.get(dpg.get_value(TAG_FPS))
        self.config.font_path = dpg.get_value(TAG_FONT_PATH).strip()
        self.config.font_size = dpg.get_value(TAG_FONT_SIZE)
        self.config.font_scale = round(dpg.get_value(TAG_FONT_SCALE), 2)
        config.save_config(self.config)
