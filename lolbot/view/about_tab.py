"""
View tab that displays information about the bot
"""

import webbrowser
import requests

import dearpygui.dearpygui as dpg

from lolbot.common.config import Constants


class AboutTab:
    """Class that displays the About Tab and information about the bot"""

    def __init__(self) -> None:
        response = requests.get("https://api.github.com/repos/iholston/lol-bot/releases/latest")
        self.version = 'v' + Constants.VERSION
        self.latest_version = response.json()["name"]
        self.need_update = False
        if self.latest_version != self.version:
            self.need_update = True

    def create_tab(self, parent: int) -> None:
        """Creates About Tab"""
        with dpg.tab(label="About", parent=parent) as self.about_tab:
            dpg.add_spacer()
            with dpg.group(horizontal=True):
                dpg.add_button(label='Bot Version', width=100, enabled=False)
                dpg.add_text(default_value=self.version)
                if self.need_update:
                    update = dpg.add_button(label="- Update Available ({})".format(self.latest_version), callback=lambda: webbrowser.open('https://github.com/iholston/lol-bot/releases/latest'))
                    with dpg.tooltip(dpg.last_item()):
                        dpg.add_text("Get latest release")
                    dpg.bind_item_theme(update, "__hyperlinkTheme")
            with dpg.group(horizontal=True):
                dpg.add_button(label='Github', width=100, enabled=False)
                dpg.add_button(label='www.github.com/iholston/lol-bot', callback=lambda: webbrowser.open('www.github.com/iholston/lol-bot'))
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("Open link in webbrowser")
            dpg.add_spacer()
            dpg.add_input_text(multiline=True, default_value=self._notes_text(), height=288, width=568, enabled=False)

    @staticmethod
    def _notes_text() -> str:
        """Sets text in About Text box"""
        notes = "\t\t\t\t\t\t\t\t\tNotes\n"

        notes += """
Version 2.1.0+ processes accounts differently. Accounts must unfortunately 
be added through the accounts tab manually a single time to convert them to 
the new format. After that it should work normally.        

Alternatively, you can copy the old 'lolbot/resources/account.json' file to
the new location (select 'Show in Finder' on account tab). If you do this,
make sure to find and replace all instances of 'leveled' with 'level' and
'true' with 30 (or your max level) and false with 0.

If you have any problems create an issue on the github repo.
"""

        return notes
