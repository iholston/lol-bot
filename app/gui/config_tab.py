import webbrowser
import os
import dearpygui.dearpygui as dpg
from ..common import constants


class ConfigTab:

    def __init__(self):
        self.id = None

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
                dpg.add_input_text(default_value=constants.LEAGUE_CLIENT_DIR, width=380, callback=self._set_dir)
            with dpg.group(horizontal=True):
                dpg.add_input_text(default_value='Game Mode', width=180, readonly=True)
                dpg.add_combo(items=['Intro', 'Beginner', 'Intermediate'], default_value='Beginner', width=380,
                              callback=self._set_mode)
            with dpg.group(horizontal=True):
                dpg.add_input_text(default_value='Account Max Level', width=180, enabled=False)
                dpg.add_input_int(default_value=constants.ACCOUNT_MAX_LEVEL, min_value=0, step=1, width=380,
                                  callback=self._set_level)
            with dpg.group(horizontal=True):
                dpg.add_input_text(default_value='Champ Pick Order', width=180, enabled=False)
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text(
                        "If blank or if champs are taken, the bot\nwill select a random free to play champion.\nAdd champs with a comma between each number")
                dpg.add_input_text(default_value="43, 54, 12, 21", width=334)
                b = dpg.add_button(label="list", callback=lambda: webbrowser.open('ddragon.leagueoflegends.com/cdn/12.6.1/data/en_US/champion.json'))
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("Open ddragon.leagueoflegends.com in webbrowser")
                dpg.bind_item_theme(b, "__demo_hyperlinkTheme")
            with dpg.group(horizontal=True):
                dpg.add_input_text(default_value='Ask for Mid Dialog', width=180, enabled=False)
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("The bot will type a random phrase in the\nchamp select lobby")
                dpg.add_input_text(
                    default_value='mid ples\nplanning on going mid team\nmid por favor\nbienvenidos, mid\nhowdy, mid\ngoing mid\nmid',
                    width=380, multiline=True, height=80)

    @staticmethod
    def _set_dir(sender) -> None:
        """Checks if directory exists and sets the Client Directory path"""
        constants.LEAGUE_CLIENT_DIR = dpg.get_value(sender)  # https://stackoverflow.com/questions/42861643/python-global-variable-modified-prior-to-multiprocessing-call-is-passed-as-ori
        if os.path.exists(constants.LEAGUE_CLIENT_DIR):
            constants.persist()

    @staticmethod
    def _set_mode(sender) -> None:
        """Sets the game mode"""
        match dpg.get_value(sender):
            case "Intro":
                constants.GAME_LOBBY_ID = 830
            case "Beginner":
                constants.GAME_LOBBY_ID = 840
            case "Intermediate":
                constants.GAME_LOBBY_ID = 850
        constants.persist()

    @staticmethod
    def _set_level(sender) -> None:
        """Sets account max level"""
        constants.ACCOUNT_MAX_LEVEL = dpg.get_value(sender)
        constants.persist()
