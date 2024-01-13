"""
View tab that handles bot controls and displays bot output
"""

import pygetwindow as gw
from pynput import mouse
import dearpygui.dearpygui as dpg

from lolbot.common import utils
from lolbot.common.config import ConfigRW


def with_config_rw(function):
    def wrapper(self, *args, **kwargs):
        self.config = ConfigRW()
        try:
            result = function(self, *args, **kwargs)
            return result
        finally:
            self.config.file.close()
    return wrapper


class DebugTab:
    """Class that displays the BotTab and handles bot controls/output"""

    def __init__(self) -> None:
        self.is_tracking_enabled = False
        self.tracking_btn = None
        self.config = None
        return

    def create_tab(self, parent) -> None:
        """Creates Bot Tab"""
        with dpg.tab(label="Debug", parent=parent) as self.status_tab:
            dpg.add_spacer()
            with dpg.group(horizontal=True):
                dpg.add_button(label='Click Minimap Mid Turret', width=180, callback=self.click_mid_turret)
                dpg.add_button(label='Click Minimap Mid Center', width=180, callback=self.click_mid_center)
                dpg.add_button(label='Click Minimap Enemy Nexus', width=180, callback=self.click_enemy_nexus)
            with dpg.group(horizontal=True):
                self.tracking_btn = dpg.add_button(tag="enable_tracking_btn", label=f'Tracking coords: {"Enabled" if self.is_tracking_enabled else "Disabled"}', width=180, callback=self.toggle_tracking)
                dpg.add_text(tag="coords", wrap=380)
                with dpg.tooltip(parent="enable_tracking_btn"):
                    dpg.add_text("If enabled, left mouse click will be registred and the coords will be printed")
            dpg.add_spacer()

    @with_config_rw
    def click_mid_turret(self):
        utils.click(tuple(self.config.get_data('ally_mid_turret')), utils.LEAGUE_GAME_CLIENT_WINNAME, 2);
        utils.click(tuple(self.config.get_data('ally_mid_turret')), utils.LEAGUE_GAME_CLIENT_WINNAME);

    @with_config_rw
    def click_mid_center(self):
        utils.click(tuple(self.config.get_data('attack_mid_turret')), utils.LEAGUE_GAME_CLIENT_WINNAME, 2);
        utils.click(tuple(self.config.get_data('attack_mid_turret')), utils.LEAGUE_GAME_CLIENT_WINNAME);

    @with_config_rw
    def click_enemy_nexus(self):
        utils.click(tuple(self.config.get_data('attack_nexus')), utils.LEAGUE_GAME_CLIENT_WINNAME, 2);
        utils.click(tuple(self.config.get_data('attack_nexus')), utils.LEAGUE_GAME_CLIENT_WINNAME);

    def on_click(self, x, y, button, pressed):
        if pressed and button == mouse.Button.right and self.is_tracking_enabled:
            current_window = gw.getActiveWindow()
            window_title = current_window.title
            relative_x = (x - current_window.left) / current_window.width
            relative_y = (y - current_window.top) / current_window.height
            dpg.set_value("coords", f"Title: '{window_title}', coords: ({relative_x:.5f}, {relative_y:.5f})")

    def toggle_tracking(self):
        self.is_tracking_enabled = not self.is_tracking_enabled
        dpg.set_item_label(self.tracking_btn, f'Tracking coords: {"Enabled" if self.is_tracking_enabled else "Disabled"}')
        listener = mouse.Listener(on_click=self.on_click)
        if self.is_tracking_enabled:
            listener.start()
        else:
            dpg.set_value("coords", "")
            listener.stop()