import json.decoder
import webbrowser
import os
from json import load, dump
import dearpygui.dearpygui as dpg
from ..common import constants


class ConfigTab:

    def __init__(self):
        self.id = None
        self.lobbies = {
            'Intro': 830,
            'Beginner': 840,
            'Intermediate': 850
        }
        self.file_name = constants.LOCAL_APP_CONFIG_PATH
        self.file = open(self.file_name, "r+")
        self.configs = load(self.file)
        self._config_update()

    def create_tab(self, parent):
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
                dpg.add_input_text(tag="LeaguePath", default_value=constants.LEAGUE_CLIENT_DIR, width=380, callback=self._set_dir)
            with dpg.group(horizontal=True):
                dpg.add_input_text(default_value='Game Mode', width=180, readonly=True)
                dpg.add_combo(tag="GameMode", items=list(self.lobbies.keys()), default_value=list(self.lobbies.keys())[
                    list(self.lobbies.values()).index(self.configs['lobby'])], width=380, callback=self._set_mode)
            with dpg.group(horizontal=True):
                dpg.add_input_text(default_value='Account Max Level', width=180, enabled=False)
                dpg.add_input_int(tag="MaxLevel", default_value=constants.ACCOUNT_MAX_LEVEL, min_value=0, step=1, width=380, callback=self._set_level)
            with dpg.group(horizontal=True):
                dpg.add_input_text(default_value='Champ Pick Order', width=180, enabled=False)
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("If blank or if all champs are taken, the bot\nwill select a random free to play champion.\nAdd champs with a comma between each number.\nIt will autosave if valid.")
                dpg.add_input_text(default_value=str(constants.CHAMPS).replace("[", "").replace("]", ""), width=334, callback=self._set_champs)
                b = dpg.add_button(label="list", width=42, indent=526, callback=lambda: webbrowser.open('ddragon.leagueoflegends.com/cdn/12.6.1/data/en_US/champion.json'))
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("Open ddragon.leagueoflegends.com in webbrowser")
                dpg.bind_item_theme(b, "__demo_hyperlinkTheme")
            with dpg.group(horizontal=True):
                dpg.add_input_text(default_value='Ask for Mid Dialog', width=180, enabled=False)
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text(
                        "The bot will type a random phrase in the\nchamp select lobby. Each line is a phrase.\nIt will autosave.")
                x = ""
                for dia in constants.ASK_4_MID_DIALOG:
                    x += dia.replace("'", "") + "\n"
                dpg.add_input_text(default_value=x, width=380, multiline=True, height=200, callback=self._set_dialog)

    def _config_update(self) -> None:
        """Dumps settings into config file. Updates values based on constants.py which reads config.json in"""
        self.configs['league_path'] = constants.LEAGUE_CLIENT_DIR
        self.configs['lobby'] = constants.GAME_LOBBY_ID
        self.configs['max_level'] = constants.ACCOUNT_MAX_LEVEL
        self.configs['champs'] = constants.CHAMPS
        self.configs['dialog'] = constants.ASK_4_MID_DIALOG
        self.file.seek(0)
        dump(self.configs, self.file, indent=4)
        self.file.truncate()

    def _set_dir(self, sender) -> None:
        """Checks if directory exists and sets the Client Directory path"""
        constants.LEAGUE_CLIENT_DIR = dpg.get_value(sender)  # https://stackoverflow.com/questions/42861643/python-global-variable-modified-prior-to-multiprocessing-call-is-passed-as-ori
        if os.path.exists(constants.LEAGUE_CLIENT_DIR):
            self.configs['league_path'] = constants.LEAGUE_CLIENT_DIR
            self._config_update()
            constants.update()

    def _set_mode(self, sender) -> None:
        """Sets the game mode"""
        match dpg.get_value(sender):
            case "Intro":
                constants.GAME_LOBBY_ID = 830
            case "Beginner":
                constants.GAME_LOBBY_ID = 840
            case "Intermediate":
                constants.GAME_LOBBY_ID = 850
        self.configs['mode'] = constants.GAME_LOBBY_ID
        self._config_update()

    def _set_level(self, sender) -> None:
        """Sets account max level"""
        constants.ACCOUNT_MAX_LEVEL = dpg.get_value(sender)
        self.configs['max_level'] = constants.ACCOUNT_MAX_LEVEL
        self._config_update()

    def _set_champs(self, sender) -> None:
        """Sets champ pick order"""
        x = dpg.get_value(sender)
        try:
            champs = [int(s) for s in x.split(',')]
        except ValueError:
            dpg.configure_item(sender, default_value=str(constants.CHAMPS).replace("[", "").replace("]", ""))
            return
        constants.CHAMPS = champs
        self._config_update()

    def _set_dialog(self, sender) -> None:
        """Sets dialog options"""
        constants.ASK_4_MID_DIALOG = dpg.get_value(sender).strip().split("\n")
        self._config_update()
