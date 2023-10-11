"""
A simple implementation of account.py using a json file
"""

import json
import os
from app.common import constants

accounts_path = os.getcwd() + "/app/resources/accounts.json"
with open(accounts_path, 'r') as f:
    data = json.load(f)

def get_username() -> str:
    """Gets an available account username from JSON file"""
    for account in data['accounts']:
        if not account['leveled']:
            return account['username']

def get_password() -> str:
    """Gets an available account password from JSON file"""
    for account in data['accounts']:
        if not account['leveled']:
            return account['password']

def set_account_as_leveled() -> None:
    """Sets account as leveled in the JSON file"""
    for account in data['accounts']:
        if not account['leveled']:
            account['leveled'] = True
            with open(accounts_path, 'w') as json_file:
                json.dump(data, json_file)
            return

def add_account(account) -> None:
    """Writes account to JSON"""
    data['accounts'].append(account)
    with open(accounts_path, 'w') as outfile:
        outfile.write(json.dumps(data, indent=4))

def get_all_accounts() -> dict:
    """Returns all account information"""
    with open(accounts_path, 'r') as f:
        accounts = json.load(f)
    return accounts