"""
A simple implementation of account.py using a json file
"""

import os
import json

from lolbot.common.config import ACCOUNT_PATH


def get_username() -> str:
    """Gets an available account username from JSON file"""
    with open(ACCOUNT_PATH, 'r') as f:
        data = json.load(f)
    for account in data['accounts']:
        if not account['leveled']:
            return account['username']


def get_password() -> str:
    """Gets an available account password from JSON file"""
    with open(ACCOUNT_PATH, 'r') as f:
        data = json.load(f)
    for account in data['accounts']:
        if not account['leveled']:
            return account['password']


def set_account_as_leveled() -> None:
    """Sets account as leveled in the JSON file"""
    with open(ACCOUNT_PATH, 'r') as f:
        data = json.load(f)
    for account in data['accounts']:
        if not account['leveled']:
            account['leveled'] = True
            with open(ACCOUNT_PATH, 'w') as json_file:
                json.dump(data, json_file)
            return


def add_account(account) -> None:
    """Writes account to JSON"""
    with open(ACCOUNT_PATH, 'r') as f:
        data = json.load(f)
    data['accounts'].append(account)
    with open(ACCOUNT_PATH, 'w') as outfile:
        outfile.write(json.dumps(data, indent=4))


def edit_account(og_name, account) -> None:
    with open(ACCOUNT_PATH, 'r') as f:
        data = json.load(f)
    index = -1
    for i in range(len(data['accounts'])):
        if data['accounts'][i]['username'] == og_name:
            index = i
            break
    data['accounts'][index]['username'] = account['username']
    data['accounts'][index]['password'] = account['password']
    data['accounts'][index]['leveled'] = account['leveled']
    with open(ACCOUNT_PATH, 'w') as outfile:
        outfile.write(json.dumps(data, indent=4))


def delete_account(account) -> None:
    with open(ACCOUNT_PATH, 'r') as f:
        data = json.load(f)
    data['accounts'].remove(account)
    with open(ACCOUNT_PATH, 'w') as outfile:
        outfile.write(json.dumps(data, indent=4))


def get_all_accounts() -> dict:
    """Returns all account information"""
    with open(ACCOUNT_PATH, 'r') as f:
        try:
            accounts = json.load(f)
        except:
            accounts = {'accounts': {}}
    return accounts
