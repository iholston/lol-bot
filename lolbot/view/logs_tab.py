"""
View tab that displays logs in the /logs folder
"""

import subprocess
import os
import shutil
from datetime import datetime

import dearpygui.dearpygui as dpg

from lolbot.common.config import Constants


class LogsTab:
    """Class that displays the Log Tab"""

    def __init__(self) -> None:
        self.id = None
        self.logs_group = None

    def create_tab(self, parent) -> None:
        """Creates Log Tab"""
        with dpg.tab(label="Logs", parent=parent) as self.id:
            with dpg.window(label="Delete Files", modal=True, show=False, tag="DeleteFiles", pos=[115, 130]):
                dpg.add_text("All files in the logs folder will be deleted")
                dpg.add_separator()
                dpg.add_spacer()
                dpg.add_spacer()
                dpg.add_spacer()
                with dpg.group(horizontal=True, indent=75):
                    dpg.add_button(label="OK", width=75, callback=self.clear_logs)
                    dpg.add_button(label="Cancel", width=75, callback=lambda: dpg.configure_item("DeleteFiles", show=False))
            dpg.add_spacer()
            with dpg.group(horizontal=True):
                dpg.add_text(tag="LogUpdatedTime", default_value='Last Updated: {}'.format(datetime.now()))
                dpg.add_button(label='Update', width=54, callback=self.create_log_table)
                dpg.add_button(label='Clear', width=54, callback=lambda: dpg.configure_item("DeleteFiles", show=True))
                dpg.add_button(label='Show in File Explorer', callback=lambda: subprocess.Popen('explorer /select, {}'.format(Constants.LOG_DIR)))
            dpg.add_spacer()
            dpg.add_separator()
            dpg.add_spacer()
            self.create_log_table()

    def create_log_table(self) -> None:
        """Reads in logs from the logs folder and populates the logs tab"""
        if self.logs_group is not None:
            dpg.delete_item(self.logs_group)
        dpg.set_value('LogUpdatedTime', 'Last Updated: {}'.format(datetime.now()))
        with dpg.group(parent=self.id) as self.logs_group:
            for filename in self.sorted_dir_creation_time(Constants.LOG_DIR):
                f = os.path.join(Constants.LOG_DIR, filename)
                if f.endswith('.1'):
                    os.unlink(f)
                    continue
                if os.path.isfile(f):
                    with dpg.collapsing_header(label=filename):
                        f = open(f, "r")
                        dpg.add_input_text(multiline=True, default_value=f.read(), height=300, width=600, tab_input=True)

    def clear_logs(self) -> None:
        """Empties the log folder"""
        dpg.configure_item("DeleteFiles", show=False)
        folder = Constants.LOG_DIR
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
        self.create_log_table()

    @staticmethod
    def sorted_dir_creation_time(directory: str) -> list:
        """Sorts directory by creation time. recent first"""
        def get_creation_time(item):
            item_path = os.path.join(directory, item)
            return os.path.getctime(item_path)

        items = os.listdir(directory)
        sorted_items = list(reversed(sorted(items, key=get_creation_time)))
        return sorted_items
