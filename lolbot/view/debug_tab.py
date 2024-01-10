"""
View tab that handles bot controls and displays bot output
"""

import multiprocessing
import threading

import dearpygui.dearpygui as dpg

from lolbot.bot.game import Game
from lolbot.common import utils


class DebugTab:
    """Class that displays the BotTab and handles bot controls/output"""

    def __init__(self) -> None:
        return

    def create_tab(self, parent) -> None:
        """Creates Bot Tab"""
        with dpg.tab(label="Debug", parent=parent) as self.status_tab:
            dpg.add_spacer()
            with dpg.group(horizontal=True):
                dpg.add_button(tag="Click Minimap Mid Turret", label='Click Minimap Mid Turret', width=180, callback=self.click_mid_turret)  # width=136
                dpg.add_button(tag="Click Minimap Mid Center", label='Click Minimap Mid Center', width=180, callback=self.click_mid_center)  # width=136
                dpg.add_button(tag="Click Minimap Enemy Nexus", label='Click Minimap Enemy Nexus', width=180, callback=self.click_enemy_nexus)  # width=136
            dpg.add_spacer()


    def click_mid_turret(self):
        utils.click(Game.MINI_MAP_UNDER_TURRET, utils.LEAGUE_GAME_CLIENT_WINNAME);


    def click_mid_center(self):
        utils.click(Game.MINI_MAP_CENTER_MID, utils.LEAGUE_GAME_CLIENT_WINNAME);


    def click_enemy_nexus(self):
        utils.click(Game.MINI_MAP_ENEMY_NEXUS, utils.LEAGUE_GAME_CLIENT_WINNAME);
