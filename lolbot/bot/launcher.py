"""
Handles Riot Client and login to launch the League Client
"""

import logging
import subprocess
from time import sleep
from pathlib import Path

import lolbot.lcu.lcu_api as api
import lolbot.lcu.cmd as cmd
from lolbot.common import proc
import lolbot.common.config as config


class LauncherError(Exception):
    def __init__(self, msg=''):
        self.msg = msg

    def __str__(self):
        return self.msg


class Launcher:
    """Handles the Riot Client and launches League of Legends"""

    def __init__(self) -> None:
        self.log = logging.getLogger(__name__)
        self.config = config.load_config()
        self.api = api.LCUApi()
        self.api = self.api.update_auth()
        self.username = ""
        self.password = ""

    def launch_league(self, username: str, password: str) -> None:
        """Runs setup logic and starts launch sequence"""
        if not username or not password:
            self.log.warning('No account set. Add accounts on account page')
        self.username = username
        self.password = password
        self.launch_loop()

    def launch_loop(self) -> None:
        """Handles opening the League of Legends client"""
        attempted_login = False
        for i in range(100):

            # League is running and there was a successful login attempt
            if proc.is_league_running() and attempted_login:
                self.log.info("Launch Success")
                proc.close_riot_client()
                return

            # League is running without a login attempt
            elif proc.is_league_running() and not attempted_login:
                self.log.warning("League opened with prior login")
                self.verify_account()
                return

            # League is not running but Riot Client is running
            elif not proc.is_league_running() and proc.is_rc_running():
                token = self.api.check_access_token()
                if token:
                    self.start_league()
                else:
                    self.login()
                    attempted_login = True
                    sleep(1)

            # Nothing is running
            elif not proc.is_league_running() and not proc.is_rc_running():
                self.start_league()
            sleep(2)

        if attempted_login:
            raise LauncherError("Launch Error. Most likely the Riot Client needs an update or League needs an update from within Riot Client")
        else:
            raise LauncherError("Could not launch League of legends")

    def start_league(self):
        self.log.info('Launching League')
        rclient = Path(self.config['league_dir']).parent.absolute().parent.absolute()
        rclient = str(rclient) + "/Riot Client/RiotClientServices"
        subprocess.Popen([rclient, "--launch-product=league_of_legends", "--launch-patchline=live"])
        sleep(3)

    def login(self) -> None:
        """Sends account credentials to Riot Client"""
        self.log.info("Logging into Riot Client")
        self.api.login(self.username, self.password)

    def verify_account(self) -> bool:
        """Checks if account credentials match the account on the League Client"""
        self.log.info("Verifying logged-in account credentials")
        self.api = api.LCUApi()
        name = self.api.get_display_name()
        if name != self.username:
            self.log.warning("Accounts do not match! Proceeding anyways")
            return False
        else:
            self.log.info("Account Verified")
            return True
