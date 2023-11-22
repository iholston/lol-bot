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
    def get_all_accounts(self) -> dict:
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
        if not os.path.exists(Constants.ACCOUNT_PATH):
            data = {'Accounts': []}
            with open(Constants.ACCOUNT_PATH, 'w+') as f:
                json.dump(data, f, indent=4)

    def get_account(self, max_level: int) -> Account:
        """Gets an account username from JSON file where level is < max_level"""
        with open(Constants.ACCOUNT_PATH, "r") as f:
            data = json.load(f)
            for account in data['Accounts']:
                if account['level'] < max_level:
                    return Account(account['username'], account['password'], account['level'])

    def add_account(self, account: Account):
        """Writes account to JSON, will not write duplicates"""
        with open(Constants.ACCOUNT_PATH, 'r+') as f:
            data = json.load(f)
        if asdict(account) in data['Accounts']:
            return
        data['Accounts'].append(asdict(account))
        with open(Constants.ACCOUNT_PATH, 'r+') as outfile:
            outfile.write(json.dumps(data, indent=4))

    def edit_account(self, og_uname: str, account: Account):
        """Edit an account"""
        with open(Constants.ACCOUNT_PATH, 'r') as f:
            data = json.load(f)
        index = -1
        for i in range(len(data['Accounts'])):
            if data['Accounts'][i]['username'] == og_uname:
                index = i
                break
        data['Accounts'][index]['username'] = account.username
        data['Accounts'][index]['password'] = account.password
        data['Accounts'][index]['level'] = account.level
        with open(Constants.ACCOUNT_PATH, 'w') as outfile:
            outfile.write(json.dumps(data, indent=4))

    def delete_account(self, account: Account):
        """Deletes account"""
        with open(Constants.ACCOUNT_PATH, 'r') as f:
            data = json.load(f)
        data['Accounts'].remove(asdict(account))
        with open(Constants.ACCOUNT_PATH, 'w') as outfile:
            outfile.write(json.dumps(data, indent=4))

    def get_all_accounts(self) -> dict:
        """Returns all accounts as dictionary"""
        with open(Constants.ACCOUNT_PATH, 'r') as f:
            data = json.load(f)
        return data['Accounts']

    def set_account_as_leveled(self, account: Account, max_level: int):
        """Sets account level to user configured max level in the JSON file"""
        with open(Constants.ACCOUNT_PATH, 'r') as f:
            data = json.load(f)
        for account in data['Accounts']:
            if account['username'] == account.username:
                account['level'] = max_level
                with open(Constants.ACCOUNT_PATH, 'w') as json_file:
                    json.dump(data, json_file)
                return
