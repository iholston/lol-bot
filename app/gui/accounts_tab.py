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
            with dpg.theme(tag="clear_background"):
                with dpg.theme_component(dpg.mvInputText):
                    dpg.add_theme_color(dpg.mvThemeCol_FrameBg, [0, 0, 0, 0])
            dpg.add_spacer()
            with dpg.window(label="Add New Account", modal=True, show=False, tag="AccountSubmit", height=90, width=250, pos=[155, 110]):
                dpg.add_input_text(tag="UsernameField", hint="Username", width=234)
                dpg.add_input_text(tag="PasswordField", hint="Password", width=234)
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Submit", width=113, callback=self._add_account)
                    dpg.add_button(label="Cancel", width=113,
                                   callback=lambda: dpg.configure_item("AccountSubmit", show=False))
            with dpg.group(horizontal=True):
                dpg.add_button(label="Add New Account", width=184,
                               callback=lambda: dpg.configure_item("AccountSubmit", show=True))
                dpg.add_button(label="Show in File Explorer", width=184, callback=lambda: subprocess.Popen('explorer /select, {}'.format(os.getcwd() + "\\app\\resources\\accounts.json")))
                dpg.add_button(label="Refresh", width=184, callback=self.create_accounts_table)
            dpg.add_spacer()
            self.create_accounts_table()

    def create_accounts_table(self) -> None:
        """Creates a table from account data"""
        if self.accounts_table is not None:
            dpg.delete_item(self.accounts_table)
            dpg.delete_item("AccountsNote")
        self.accounts = account.get_all_accounts()
        with dpg.table(row_background=True, resizable=True,
                       borders_innerV=True, borders_outerV=True, borders_innerH=True, scrollY=True,
                       borders_outerH=True, parent=self.id, height=275) as self.accounts_table:
            dpg.add_table_column(label="Username", width_stretch=True)
            dpg.add_table_column(label="Password", width_stretch=True)
            dpg.add_table_column(label="Leveled")
            for _account in reversed(self.accounts['accounts']):
                with dpg.table_row():
                    dpg.add_input_text(default_value=_account['username'])
                    dpg.bind_item_theme(dpg.last_item(), "clear_background")
                    dpg.add_input_text(default_value=_account['password'])
                    dpg.bind_item_theme(dpg.last_item(), "clear_background")
                    dpg.add_input_text(default_value=_account['leveled'])
                    dpg.bind_item_theme(dpg.last_item(), "clear_background")
        dpg.add_text(tag="AccountsNote", parent=self.id, indent=1, wrap=560, default_value='To edit account information, click "Show in File Explorer" and edit information in the accounts.json file')

    def _add_account(self) -> None:
        """Adds a new account to accounts.json and updates gui"""
        dpg.configure_item("AccountSubmit", show=False)
        account.add_account({"username": dpg.get_value("UsernameField"), "password": dpg.get_value("PasswordField"), "leveled": False})
        dpg.configure_item("UsernameField", default_value="")
        dpg.configure_item("PasswordField", default_value="")
        self.create_accounts_table()