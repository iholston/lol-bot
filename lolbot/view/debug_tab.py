"""
View tab that handles bot controls and displays bot output
"""

import pygetwindow as gw
from pynput import mouse
import dearpygui.dearpygui as dpg

import logging


from lolbot.bot.game import Game
from lolbot.common import utils


class DebugTab:
    """Class that displays the BotTab and handles bot controls/output"""

    def __init__(self) -> None:
        self.is_tracking_enabled = False
        self.log = logging.getLogger(__name__)
        self.tracking_btn = None
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
                self.tracking_btn = dpg.add_button(label=f'Tracking coords: {"Enabled" if self.is_tracking_enabled else "Disabled"}', width=180, callback=self.toggle_tracking)
            dpg.add_spacer()


    def click_mid_turret(self):
        utils.click(Game.MINI_MAP_UNDER_TURRET, utils.LEAGUE_GAME_CLIENT_WINNAME);


    def click_mid_center(self):
        utils.click(Game.MINI_MAP_CENTER_MID, utils.LEAGUE_GAME_CLIENT_WINNAME);


    def click_enemy_nexus(self):
        utils.click(Game.MINI_MAP_ENEMY_NEXUS, utils.LEAGUE_GAME_CLIENT_WINNAME);

    def on_click(self, x, y, button, pressed):
        if pressed and button == mouse.Button.left and self.is_tracking_enabled:
            current_window = gw.getActiveWindow()
            window_title = current_window.title
            relative_x = (x - current_window.left) / current_window.width
            relative_y = (y - current_window.top) / current_window.height
            print(f"Button clicked in on '{window_title}', coords: ({relative_x}, {relative_y})")

    def toggle_tracking(self):
        self.is_tracking_enabled = not self.is_tracking_enabled
        dpg.set_item_label(self.tracking_btn, f'Tracking coords: {"Enabled" if self.is_tracking_enabled else "Disabled"}')
        listener = mouse.Listener(on_click=self.on_click)
        if self.is_tracking_enabled:
            listener.start()
        else:
            listener.stop()
