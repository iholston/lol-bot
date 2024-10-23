"""
Handles launching League of Legends and logging into an account
"""

import logging
import subprocess
from pathlib import Path
from time import sleep

import lolbot.common.config as config
import lolbot.common.proc as proc
from lolbot.lcu.lcu_api import LCUApi, LCUError

log = logging.getLogger(__name__)

MAX_RETRIES = 30


class LaunchError(Exception):
    """Indicates that League could not be opened."""
    pass


def open_league_with_account(username: str, password: str) -> None:
    """Ensures that League is open and logged into a specific account"""
    api = LCUApi()
    login_attempted = False
    for i in range(MAX_RETRIES):
        if proc.is_league_running() and verify_account(api, username):
            # League is running and account is logged in
            return
        elif proc.is_league_running():
            # League is running and wrong account is logged in
            api.logout_on_close()
            proc.close_all_processes()
            sleep(10)
            continue
        elif proc.is_rc_running() and api.access_token_exists():
            # Riot Client is open and a user is logged in
            launch_league()
        elif proc.is_league_running():
            # Riot Client is open and waiting for login
            login_attempted = True
            log.info("Logging into Riot Client")
            try:
                api.login(username, password)
            except LCUError:
                sleep(2)
                continue
            launch_league()
        else:
            # Nothing is running
            launch_league()
        sleep(2)

    if login_attempted:
        raise LaunchError("Launch Error. Most likely the Riot Client or League needs an update from within RC")
    else:
        raise LaunchError("Could not launch League of Legends")


def launch_league():
    """Launches League of Legends from Riot Client."""
    log.info('Launching League of Legends')
    c = config.load_config()
    riot_client_dir = Path(c['league_dir']).parent.absolute().parent.absolute()
    riot_client_path = str(riot_client_dir) + "/Riot Client/RiotClientServices"
    subprocess.Popen([riot_client_path, "--launch-product=league_of_legends", "--launch-patchline=live"])
    sleep(3)


def verify_account(api: LCUApi, username: str = None) -> bool:
    """Checks if account username match the account that is currently logged in."""
    log.info("Verifying logged-in account credentials")
    name = ""
    try:
        name = api.get_display_name()
    except LCUError:
        return False

    if username == name:
        log.info("Account Verified")
        return True
    else:
        log.warning("Accounts do not match!")
        return False
