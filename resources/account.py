"""
This is a simple implementation of account.py. To use it, add your accounts to the accounts.json
file. The "leveled" parameter is determined by whether the account level is at the
ACCOUNT_MAX_LEVEL as defined in constants.py (default is 30 for ranked play). So
if your account is less than 30 then it would be set to false and when it hits level 30 it will
be set to true.
"""

import json
import os

accounts_path = os.path.dirname(os.getcwd()) + "/resources/accounts.json"
with open(accounts_path, 'r') as f:
    data = json.load(f)

def get_username():
    for account in data['accounts']:
        if not account['leveled']:
            return account['username']

def get_password():
    for account in data['accounts']:
        if not account['leveled']:
            return account['password']

def set_account_as_leveled():
    for account in data['accounts']:
        if not account['leveled']:
            account['leveled'] = True
            with open(accounts_path, 'w') as json_file:
                json.dump(data, json_file)
            return