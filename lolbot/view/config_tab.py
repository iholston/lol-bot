"""
View tab that sets configurations for the bot
"""

import webbrowser
import os

import dearpygui.dearpygui as dpg

from lolbot.common.config import ConfigRW


class ConfigTab:
    """Class that creates the ConfigTab and sets configurations for the bot"""

    def __init__(self) -> None:
        self.id = None
        self.lobbies = {
            'Intro': 870,
            'Beginner': 880,
            'Intermediate': 890
        }
        self.config = ConfigRW()

    def create_tab(self, parent: int) -> None:
        """Creates Settings Tab"""
        with dpg.tab(label="Config", parent=parent) as self.id:
            dpg.add_spacer()
            with dpg.group(horizontal=True):
                dpg.add_button(label='Configuration', enabled=False, width=180)
                dpg.add_button(label="Value", enabled=False, width=380)
            dpg.add_spacer()
            dpg.add_spacer()
            with dpg.group(horizontal=True):
                dpg.add_input_text(default_value='League Installation Path', width=180, enabled=False)
                dpg.add_input_text(tag="LeaguePath", default_value=self.config.get_data('league_dir'), width=380, callback=self._set_dir)
            with dpg.group(horizontal=True):
                dpg.add_input_text(default_value='Game Mode', width=180, readonly=True)
                lobby = int(self.config.get_data('lobby'))
                if lobby < 870:
                    lobby += 40
                dpg.add_combo(tag="GameMode", items=list(self.lobbies.keys()), default_value=list(self.lobbies.keys())[
                    list(self.lobbies.values()).index(lobby)], width=380, callback=self._set_mode)
            with dpg.group(horizontal=True):
                dpg.add_input_text(default_value='Account Max Level', width=180, enabled=False)
                dpg.add_input_int(tag="MaxLevel", default_value=self.config.get_data('max_level'), min_value=0, step=1, width=380, callback=self._set_level)
            with dpg.group(horizontal=True):
                dpg.add_input_text(default_value='Champ Pick Order', width=180, enabled=False)
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("If blank or if all champs are taken, the bot\nwill select a random free to play champion.\nAdd champs with a comma between each number.\nIt will autosave if valid.")
                dpg.add_input_text(default_value=str(self.config.get_data('champs')).replace("[", "").replace("]", ""), width=334, callback=self._set_champs)
                b = dpg.add_button(label="list", width=42, indent=526, callback=lambda: webbrowser.open('ddragon.leagueoflegends.com/cdn/{}/data/en_US/champion.json'.format(self.config.get_data('patch'))))
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("Open ddragon.leagueoflegends.com in webbrowser")
                dpg.bind_item_theme(b, "__hyperlinkTheme")
            with dpg.group(horizontal=True):
                dpg.add_input_text(default_value='Ask for Mid Dialog', width=180, enabled=False)
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("The bot will type a random phrase in the\nchamp select lobby. Each line is a phrase.\nIt will autosave.")
                x = ""
                for dia in self.config.get_data('dialog'):
                    x += dia.replace("'", "") + "\n"
                dpg.add_input_text(default_value=x, width=380, multiline=True, height=215, callback=self._set_dialog)

    def _set_dir(self, sender: int) -> None:
        """Checks if directory exists and sets the Client Directory path"""
        _dir = dpg.get_value(sender)  # https://stackoverflow.com/questions/42861643/python-global-variable-modified-prior-to-multiprocessing-call-is-passed-as-ori
        if os.path.exists(_dir):
            self.config.set_league_dir(_dir)

    def _set_mode(self, sender: int) -> None:
        """Sets the game mode"""
        self.config.set_data('lobby', self.lobbies.get(dpg.get_value(sender)))

    def _set_level(self, sender: int) -> None:
        """Sets account max level"""
        self.config.set_data('max_level', dpg.get_value(sender))

    def _set_champs(self, sender: int) -> None:
        """Sets champ pick order"""
        x = dpg.get_value(sender)
        try:
            champs = [int(s) for s in x.split(',')]
        except ValueError:
            dpg.configure_item(sender, default_value=str(self.config.get_data('champs')).replace("[", "").replace("]", ""))
            return
        self.config.set_data('champs', champs)

    def _set_dialog(self, sender: int) -> None:
        """Sets dialog options"""
        self.config.set_data('dialog', dpg.get_value(sender).strip().split("\n"))
