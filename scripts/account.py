"""
Gets an account username and password for leveling

Implement this file to connect to your database of league accounts.
There is an example file in resources that can drop-in replace this for
those who want a quick and simple option.
"""

def get_username() -> str:
    """Gets username from database"""
    return 'account_username'

def get_password() -> str:
    """Gets password from database"""
    return 'account_password'

def set_account_as_leveled() -> None:
    """Sets account as leveled in database"""
    pass