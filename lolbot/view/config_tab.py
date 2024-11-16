"""
View tab that sets configurations for the bot.
"""

import webbrowser
import os

import dearpygui.dearpygui as dpg

import lolbot.common.config as config
from lolbot.system import OS


class ConfigTab:
    """Class that creates the ConfigTab and sets configurations for the bot"""

    def __init__(self) -> None:
        self.id = None
        self.config = config.load_config()

    def create_tab(self, parent: int) -> None:
        """Creates Settings Tab"""
        with dpg.tab(label="Config", parent=parent) as self.id:
            dpg.add_spacer()
            with dpg.group(horizontal=True):
                dpg.add_button(label='Configuration', enabled=False, width=180)
                dpg.add_button(label="Value", enabled=False, width=380)
            dpg.add_spacer()
            dpg.add_spacer()
            if OS == 'Windows':
                with dpg.group(horizontal=True):
                    dpg.add_input_text(default_value='League Installation Path', width=180, enabled=False)
                    dpg.add_input_text(tag="LeaguePath", default_value=self.config['league_dir'], width=380, callback=self.save_config)
            with dpg.group(horizontal=True):
                dpg.add_input_text(default_value='Game Mode', width=180, readonly=True)
                lobby = int(self.config['lobby'])
                if lobby < 870:
                    lobby += 40
                dpg.add_combo(tag="GameMode", items=list(config.BOT_LOBBIES.keys()), default_value=list(config.BOT_LOBBIES.keys())[
                    list(config.BOT_LOBBIES.values()).index(lobby)], width=380, callback=self.save_config)
            with dpg.group(horizontal=True):
                dpg.add_input_text(default_value='Account Max Level', width=180, enabled=False)
                dpg.add_input_int(tag="MaxLevel", default_value=self.config['max_level'], min_value=0, step=1, width=380, callback=self.save_config)
            with dpg.group(horizontal=True):
                dpg.add_input_text(default_value='Champ Pick Order', width=180, enabled=False)
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("If blank or if all champs are taken, the bot\nwill select a random free to play champion.\nAdd champs with a comma between each number.\nIt will autosave if valid.")
                dpg.add_input_text(tag="Champs", default_value=str(self.config['champs']).replace("[", "").replace("]", ""), width=334, callback=self.save_config)
                b = dpg.add_button(label="list", width=42, indent=526, callback=lambda: webbrowser.open('ddragon.leagueoflegends.com/cdn/{}/data/en_US/champion.json'.format('14.21')))
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("Open ddragon.leagueoflegends.com in webbrowser")
                dpg.bind_item_theme(b, "__hyperlinkTheme")
            with dpg.group(horizontal=True):
                dpg.add_input_text(default_value='Ask for Mid Dialog', width=180, enabled=False)
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("The bot will type a random phrase in the\nchamp select lobby. Each line is a phrase.\nIt will autosave.")
                x = ""
                for dia in self.config['dialog']:
                    x += dia.replace("'", "") + "\n"
                if OS == "Windows":
                    height = 215
                else:
                    height = 238
                dpg.add_input_text(tag="Dialog", default_value=x, width=380, multiline=True, height=height, callback=self.save_config)

    def save_config(self):
        if os.path.exists(dpg.get_value('LeaguePath')):
            self.config['league_dir'] = dpg.get_value('LeaguePath')
        self.config['lobby'] = config.BOT_LOBBIES.get(dpg.get_value('GameMode'))
        self.config['max_level'] = dpg.get_value('MaxLevel')
        champs = dpg.get_value('Champs')
        self.config['champs'] = [int(s) for s in champs.split(',')]
        self.config['dialog'] = dpg.get_value("Dialog").strip().split("\n")
        config.save_config(self.config)
