import dearpygui.dearpygui as dpg
from ..common import constants

class AboutTab:

    def __init__(self):
        pass

    def create_tab(self, parent) -> None:
        """Creates About Tab"""
        with dpg.tab(label="About", parent=parent) as self.about_tab:
            dpg.add_spacer()
            with dpg.group(horizontal=True):
                dpg.add_button(label='Bot Version', width=100, enabled=False)
                dpg.add_text(default_value=constants.VERSION)
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
        return "\t\t\t\t\t\t\t\t\tNotes\n\nIf you have any problems create an issue on the github repo\nLeave a star maybe <3\n\nKnown Issues:\n\n- {Issue List}"
