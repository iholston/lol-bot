"""
View tab that displays information about the bot.
"""

import webbrowser
from pathlib import Path
import requests

import dearpygui.dearpygui as dpg


def _load_project_version() -> str:
    """Load version from pyproject.toml so version is maintained in one place."""
    pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
    if not pyproject.exists():
        return "0.0.0"

    try:
        content = pyproject.read_text(encoding="utf-8")
    except OSError:
        return "0.0.0"

    in_project_section = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_project_section = stripped == "[project]"
            continue
        if in_project_section and stripped.startswith("version") and "=" in stripped:
            _, value = stripped.split("=", 1)
            return value.strip().strip('"').strip("'")
    return "0.0.0"


VERSION = _load_project_version()


class AboutTab:
    """Class that displays the About Tab and information about the bot"""

    def __init__(self) -> None:
        self.version = f"v{VERSION}"
        try:
            response = requests.get("https://api.github.com/repos/iholston/lol-bot/releases/latest")
            self.release_version = response.json()["name"]
        except:
            self.release_version = self.version
        self.need_update = False
        if self.release_version != self.version:
            self.need_update = True

    def create_tab(self, parent: int) -> None:
        """Creates About Tab"""
        with dpg.tab(label="About", parent=parent) as self.about_tab:
            dpg.add_spacer()
            with dpg.group(horizontal=True):
                dpg.add_button(label='Bot Version', width=100, enabled=False)
                dpg.add_text(default_value=self.version)
                if self.need_update:
                    update = dpg.add_button(label="- Update Available ({})".format(self.release_version), callback=lambda: webbrowser.open("https://github.com/iholston/lol-bot/releases/latest"))
                    with dpg.tooltip(dpg.last_item()):
                        dpg.add_text("Get latest release")
                    dpg.bind_item_theme(update, "__hyperlinkTheme")
            with dpg.group(horizontal=True):
                dpg.add_button(label='Github', width=100, enabled=False)
                dpg.add_button(label='www.github.com/iholston/lol-bot', callback=lambda: webbrowser.open("https://www.github.com/iholston/lol-bot"))
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("Open link in webbrowser")
            dpg.add_spacer()
            dpg.add_input_text(multiline=True, default_value=self._notes_text(), height=288, width=568, enabled=False)

    @staticmethod
    def _notes_text() -> str:
        """Sets text in About Text box"""
        notes = "\t\t\t\t\t\t\t\t\tNotes\n"

        notes += """
This bot supports macOS only.

If you have any problems create an issue on the github repo.
"""

        return notes
