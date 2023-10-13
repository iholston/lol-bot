import os
import subprocess
import dearpygui.dearpygui as dpg
from ..common import account


class AccountsTab:

    def __init__(self):
        self.id = None
        self.accounts = None
        self.accounts_table = None

    def create_tab(self, parent):
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
                dpg.add_checkbox(tag="LeveledField", label="Leveled", default_value=False)
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Submit", width=113, callback=self.add_account)
                    dpg.add_button(label="Cancel", width=113, callback=lambda: dpg.configure_item("AccountSubmit", show=False))
            with dpg.group(horizontal=True):
                dpg.add_button(label="Add New Account", width=182,
                               callback=lambda: dpg.configure_item("AccountSubmit", show=True))
                dpg.add_button(label="Show in File Explorer", width=182, callback=lambda: subprocess.Popen('explorer /select, {}'.format(os.getcwd() + "\\app\\resources\\accounts.json")))
                dpg.add_button(label="Refresh", width=182, callback=self.create_accounts_table)
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
        self.accounts = account.get_all_accounts()
        with dpg.group(parent=self.id) as self.accounts_table:
            with dpg.group(horizontal=True):
                dpg.add_input_text(default_value="      Username", width=147)
                dpg.bind_item_theme(dpg.last_item(), "clear_background")
                dpg.add_input_text(default_value="      Password", width=147)
                dpg.bind_item_theme(dpg.last_item(), "clear_background")
                dpg.add_input_text(default_value="      Leveled", width=147)
                dpg.bind_item_theme(dpg.last_item(), "clear_background")
            for acc in reversed(self.accounts['accounts']):
                with dpg.group(horizontal=True):
                    dpg.add_button(label=acc['username'], width=147)
                    with dpg.tooltip(dpg.last_item()):
                        dpg.add_text("Copy")
                    dpg.add_button(label=acc['password'], width=147)
                    with dpg.tooltip(dpg.last_item()):
                        dpg.add_text("Copy")
                    dpg.add_button(label=acc['leveled'], width=147)
                    dpg.add_button(label="Edit", callback=self.edit_account_dialog, user_data=acc)
                    dpg.add_button(label="Delete", callback=self.delete_account_dialog, user_data=acc)


    def add_account(self) -> None:
        """Adds a new account to accounts.json and updates gui"""
        dpg.configure_item("AccountSubmit", show=False)
        account.add_account({"username": dpg.get_value("UsernameField"), "password": dpg.get_value("PasswordField"), "leveled": dpg.get_value("LeveledField")})
        dpg.configure_item("UsernameField", default_value="")
        dpg.configure_item("PasswordField", default_value="")
        dpg.configure_item("LeveledField", default_value=False)
        self.create_accounts_table()

    def edit_account(self, sender, app_data, user_data) -> None:
        account.edit_account(user_data, {"username": dpg.get_value("EditUsernameField"), "password": dpg.get_value("EditPasswordField"), "leveled": dpg.get_value("EditLeveledField")})
        dpg.delete_item("EditAccount")
        self.create_accounts_table()

    def edit_account_dialog(self, sender, app_data, user_data) -> None:
        with dpg.window(label="Edit Account", modal=True, show=True, tag="EditAccount", height=125, width=250, pos=[155, 110], on_close=lambda: dpg.delete_item("EditAccount")):
            dpg.add_input_text(tag="EditUsernameField", default_value=user_data['username'], width=234)
            dpg.add_input_text(tag="EditPasswordField", default_value=user_data['password'], width=234)
            dpg.add_checkbox(tag="EditLeveledField", label="Leveled", default_value=user_data['leveled'])
            with dpg.group(horizontal=True):
                dpg.add_button(label="Submit", width=113, callback=self.edit_account, user_data=user_data['username'])
                dpg.add_button(label="Cancel", width=113, callback=lambda: dpg.delete_item("EditAccount"))

    def delete_account(self, sender, app_data, user_data) -> None:
        account.delete_account(user_data)
        dpg.delete_item("DeleteAccount")
        self.create_accounts_table()

    def delete_account_dialog(self, sender, app_data, user_data) -> None:
        with dpg.window(label="Delete Account", modal=True, show=True, tag="DeleteAccount", pos=[125, 130], on_close=lambda: dpg.delete_item("DeleteAccount")):
            dpg.add_text("Account: {} will be deleted".format(user_data['username']))
            dpg.add_separator()
            dpg.add_spacer()
            dpg.add_spacer()
            dpg.add_spacer()
            with dpg.group(horizontal=True):
                dpg.add_button(label="OK", width=140, callback=self.delete_account, user_data=user_data)
                dpg.add_button(label="Cancel", width=140, callback=lambda: dpg.delete_item("DeleteAccount"))

