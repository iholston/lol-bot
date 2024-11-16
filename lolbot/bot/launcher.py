"""
Handles launching League of Legends and logging into an account.
"""

import logging
import subprocess
from pathlib import Path
from time import sleep

from lolbot.system import utils
from lolbot.common import config
from lolbot.api.lcu import LCUApi, LCUError

log = logging.getLogger(__name__)

MAX_RETRIES = 5


class LaunchError(Exception):
    """Indicates that League could not be opened."""
    pass


def launch_league(username: str, password: str) -> None:
    """Ensures that League is open and logged into a specific account"""
    api = LCUApi()
    api.update_auth()
    login_attempted = False
    logins = 0
    for i in range(30):
        try:
            if utils.is_league_running():
                if login_attempted:
                    log.info("Launch success")
                    utils.close_riot_client()
                else:
                    log.warning("League opened with prior login")
                    verify_account(api, username)
                return
            elif utils.is_rc_running():
                if api.access_token_exists():
                    if not login_attempted:
                        log.warning("Riot Client already logged in")
                    try:
                        api.launch_league_from_rc()
                        sleep(2)
                    except LCUError:
                        pass
                    continue
                else:
                    if logins == MAX_RETRIES:
                        raise LaunchError("Max login attempts exceeded. Check username and password")
                    else:
                        logins += 1
                    log.info("Logging into Riot Client")
                    login_attempted = True
                    # api.login(username, password)  # they turned this off
                    manual_login(username, password)
                    if not api.access_token_exists():
                        log.warning("Login attempt failed")
                        utils.close_riot_client()
                        sleep(5)
            else:
                start_league()
                sleep(10)
        except LCUError:
            sleep(2)
    raise LaunchError("Could not launch league. Ensure there are no pending updates.")


def manual_login(username: str, password: str):
    log.info('Manually logging into Riot Client')
    utils.write(username)
    sleep(.5)
    utils.keypress('tab')
    sleep(.5)
    utils.write(password)
    sleep(.5)
    utils.keypress('enter')
    sleep(10)


def start_league():
    """Launches League of Legends from Riot Client."""
    log.info('Launching League of Legends')
    c = config.load_config()
    riot_client_dir = Path(c['league_dir']).parent.absolute()
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
