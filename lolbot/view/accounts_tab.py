"""
View tab that handles creation/editing of accounts
"""

import subprocess
import time
import shutil
import threading
from typing import Any

import dearpygui.dearpygui as dpg
from lolbot.common.config import Constants
from lolbot.common.account import Account, AccountManager


class AccountsTab:
    """Class that creates the Accounts Tab and handles creation/editing of accounts"""

    def __init__(self) -> None:
        self.id = None
        self.am = AccountManager()
        self.accounts = None
        self.accounts_table = None

    def create_tab(self, parent: int) -> None:
        """Creates Accounts Tab"""
        with dpg.tab(label="Accounts", parent=parent) as self.id:
            dpg.add_text("Options")
            dpg.add_spacer()
            with dpg.theme(tag="clear_background"):
                with dpg.theme_component(dpg.mvInputText):
                    dpg.add_theme_color(dpg.mvThemeCol_FrameBg, [0, 0, 0, 0])
            with dpg.window(label="Add New Account", modal=True, show=False, tag="AccountSubmit", height=125, width=250, pos=[155, 110]):
                dpg.add_input_text(tag="UsernameField", hint="Username", width=234)
                dpg.add_input_text(tag="PasswordField", hint="Password", width=234)
                dpg.add_input_int(tag="LevelField", default_value=0, width=234)
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Submit", width=113, callback=self.add_account)
                    dpg.add_button(label="Cancel", width=113, callback=lambda: dpg.configure_item("AccountSubmit", show=False))
            with dpg.group(horizontal=True):
                dpg.add_button(label="Add New Account", width=184, callback=lambda: dpg.configure_item("AccountSubmit", show=True))
                dpg.add_button(label="Show in File Explorer", width=184, callback=lambda: subprocess.Popen('explorer /select, {}'.format(Constants.ACCOUNT_PATH)))
                dpg.add_button(tag="BackupButton", label="Create Backup", width=184, callback=self.create_backup)
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("Creates a backup of the accounts.json file in the bak folder")
            dpg.add_spacer()
            dpg.add_spacer()
            dpg.add_text("Accounts")
            with dpg.tooltip(dpg.last_item()):
                dpg.add_text("Bot will start leveling accounts from bottom up")
            dpg.add_spacer()
            dpg.add_separator()
            self.create_accounts_table()

    def create_accounts_table(self) -> None:
        """Creates a table from account data"""
        if self.accounts_table is not None:
            dpg.delete_item(self.accounts_table)
        self.accounts = self.am.get_all_accounts()
        with dpg.group(parent=self.id) as self.accounts_table:
            with dpg.group(horizontal=True):
                dpg.add_input_text(default_value="      Username", width=147)
                dpg.bind_item_theme(dpg.last_item(), "clear_background")
                dpg.add_input_text(default_value="      Password", width=147)
                dpg.bind_item_theme(dpg.last_item(), "clear_background")
                dpg.add_input_text(default_value="        Level", width=147)
                dpg.bind_item_theme(dpg.last_item(), "clear_background")
            for acc in reversed(self.accounts):
                with dpg.group(horizontal=True):
                    dpg.add_button(label=acc['username'], width=147, callback=self.copy_2_clipboard)
                    with dpg.tooltip(dpg.last_item()):
                        dpg.add_text("Copy")
                    dpg.add_button(label=acc['password'], width=147, callback=self.copy_2_clipboard)
                    with dpg.tooltip(dpg.last_item()):
                        dpg.add_text("Copy")
                    dpg.add_button(label=acc['level'], width=147)
                    dpg.add_button(label="Edit", callback=self.edit_account_dialog, user_data=acc)
                    dpg.add_button(label="Delete", callback=self.delete_account_dialog, user_data=acc)

    def add_account(self) -> None:
        """Adds a new account to accounts.json and updates view"""
        dpg.configure_item("AccountSubmit", show=False)
        self.am.add_account(Account(dpg.get_value("UsernameField"), dpg.get_value("PasswordField"), dpg.get_value("LevelField")))
        dpg.configure_item("UsernameField", default_value="")
        dpg.configure_item("PasswordField", default_value="")
        dpg.configure_item("LevelField", default_value=False)
        self.create_accounts_table()

    def edit_account(self, sender, app_data, user_data: Any) -> None:
        self.am.edit_account(user_data, Account(dpg.get_value("EditUsernameField"), dpg.get_value("EditPasswordField"), dpg.get_value("EditLevelField")))
        dpg.delete_item("EditAccount")
        self.create_accounts_table()

    def edit_account_dialog(self, sender, app_data, user_data: Any) -> None:
        with dpg.window(label="Edit Account", modal=True, show=True, tag="EditAccount", height=125, width=250, pos=[155, 110], on_close=lambda: dpg.delete_item("EditAccount")):
            dpg.add_input_text(tag="EditUsernameField", default_value=user_data['username'], width=234)
            dpg.add_input_text(tag="EditPasswordField", default_value=user_data['password'], width=234)
            dpg.add_input_int(tag="EditLevelField", default_value=user_data['level'], width=234)
            with dpg.group(horizontal=True):
                dpg.add_button(label="Submit", width=113, callback=self.edit_account, user_data=user_data['username'])
                dpg.add_button(label="Cancel", width=113, callback=lambda: dpg.delete_item("EditAccount"))

    def delete_account(self, sender, app_data, user_data: Any) -> None:
        self.am.delete_account(Account(user_data['username'], user_data['password'], user_data['level']))
        dpg.delete_item("DeleteAccount")
        self.create_accounts_table()

    def delete_account_dialog(self, sender, app_data, user_data: Any) -> None:
        with dpg.window(label="Delete Account", modal=True, show=True, tag="DeleteAccount", pos=[125, 130], on_close=lambda: dpg.delete_item("DeleteAccount")):
            dpg.add_text("Account: {} will be deleted".format(user_data['username']))
            dpg.add_separator()
            dpg.add_spacer()
            dpg.add_spacer()
            dpg.add_spacer()
            with dpg.group(horizontal=True):
                dpg.add_button(label="OK", width=140, callback=self.delete_account, user_data=user_data)
                dpg.add_button(label="Cancel", width=140, callback=lambda: dpg.delete_item("DeleteAccount"))

    @staticmethod
    def create_backup(sender: int) -> None:
        bak = "{}{}".format(time.strftime("%Y%m%d-%H%M%S"), ".json")
        shutil.copyfile(Constants.ACCOUNT_PATH, '{}/{}'.format(Constants.BAK_DIR, bak))
        dpg.configure_item("BackupButton", label="Backup Created!")
        threading.Timer(1, lambda: dpg.configure_item("BackupButton", label="Create Backup")).start()

    @staticmethod
    def copy_2_clipboard(sender: int):
        subprocess.run("clip", text=True, input=dpg.get_item_label(sender))
