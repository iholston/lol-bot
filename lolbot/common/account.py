"""
Handles accounts for the bot, persists to a JSON file
"""

import os
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict

from lolbot.common.config import Constants


@dataclass
class Account:
    username: str
    password: str
    level: int


class AccountGenerator(ABC):

    @abstractmethod
    def get_account(self) -> Account:
        pass

    @abstractmethod
    def get_all_accounts(self) -> list:
        pass

    @abstractmethod
    def add_account(self):
        pass

    @abstractmethod
    def edit_account(self):
        pass

    @abstractmethod
    def delete_account(self):
        pass

    @abstractmethod
    def set_account_as_leveled(self):
        pass


class AccountManager(AccountGenerator):
    """Class that handles account persistence"""

    def __init__(self):
        self.default_data = {'accounts': []}
        if not os.path.exists(Constants.ACCOUNT_PATH):
            with open(Constants.ACCOUNT_PATH, 'w+') as f:
                json.dump(self.default_data, f, indent=4)
        try:
            with open(Constants.ACCOUNT_PATH, 'r') as f:
                json.load(f)
        except:
            with open(Constants.ACCOUNT_PATH, 'w') as f:
                json.dump(self.default_data, f, indent=4)

    def get_account(self, max_level: int) -> Account:
        """Gets an account username from JSON file where level is < max_level"""
        with open(Constants.ACCOUNT_PATH, "r") as f:
            data = json.load(f)
            for account in data['accounts']:
                if account['level'] < max_level:
                    return Account(account['username'], account['password'], account['level'])
        return Account('', '', 0)

    def add_account(self, account: Account) -> None:
        """Writes account to JSON, will not write duplicates"""
        with open(Constants.ACCOUNT_PATH, 'r+') as f:
            data = json.load(f)
        if asdict(account) in data['accounts']:
            return
        data['accounts'].append(asdict(account))
        with open(Constants.ACCOUNT_PATH, 'r+') as outfile:
            json.dump(data, outfile, indent=4)

    def edit_account(self, og_uname: str, account: Account) -> None:
        """Edit an account"""
        with open(Constants.ACCOUNT_PATH, 'r') as f:
            data = json.load(f)
        index = -1
        for i in range(len(data['accounts'])):
            if data['accounts'][i]['username'] == og_uname:
                index = i
                break
        data['accounts'][index]['username'] = account.username
        data['accounts'][index]['password'] = account.password
        data['accounts'][index]['level'] = account.level
        with open(Constants.ACCOUNT_PATH, 'w') as outfile:
            json.dump(data, outfile, indent=4)

    def delete_account(self, account: Account) -> None:
        """Deletes account"""
        with open(Constants.ACCOUNT_PATH, 'r') as f:
            data = json.load(f)
        data['accounts'].remove(asdict(account))
        with open(Constants.ACCOUNT_PATH, 'w') as outfile:
            json.dump(data, outfile, indent=4)

    def get_all_accounts(self) -> list:
        """Returns all accounts as dictionary"""
        with open(Constants.ACCOUNT_PATH, 'r') as f:
            data = json.load(f)
        return data['accounts']

    def set_account_as_leveled(self, account: Account, max_level: int) -> None:
        """Sets account level to user configured max level in the JSON file"""
        with open(Constants.ACCOUNT_PATH, 'r') as f:
            data = json.load(f)
        for _account in data['accounts']:
            if _account['username'] == account.username:
                _account['level'] = max_level
                with open(Constants.ACCOUNT_PATH, 'w') as outfile:
                    json.dump(data, outfile, indent=4)
                return
