"""
Handles Riot Client and login to launch the League Client
"""

import logging
import subprocess
from time import sleep
from pathlib import Path

from lolbot.common import api
from lolbot.common import utils
from lolbot.common.config import ConfigRW


class LauncherError(Exception):
    def __init__(self, msg=''):
        self.msg = msg

    def __str__(self):
        return self.msg


class Launcher:
    """Handles the Riot Client and launches League of Legends"""

    def __init__(self) -> None:
        self.log = logging.getLogger(__name__)
        self.connection = api.Connection()
        self.config = ConfigRW()
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
        """Handles tasks necessary to open the League of Legends client"""
        logged_in = False
        for i in range(100):

            # League is running and there was a successful login attempt
            if utils.is_league_running() and logged_in:
                self.log.info("Launch Success")
                utils.close_riot_client()
                return

            # League is running without a login attempt
            elif utils.is_league_running() and not logged_in:
                self.log.warning("League opened with prior login")
                self.verify_account()
                return

            # League is not running but Riot Client is running
            elif not utils.is_league_running() and utils.is_rc_running():
                # Get session state
                self.connection.set_rc_headers()
                r = self.connection.request("get", "/rso-auth/v1/authorization/access-token")

                # Already logged in
                if r.status_code == 200 and not logged_in:
                    self.start_league()

                # Not logged in and haven't logged in
                if r.status_code == 404 and not logged_in:
                    self.login()
                    logged_in = True
                    sleep(1)

                # Logged in
                elif r.status_code == 200 and logged_in:
                    self.start_league()

            # Nothing is running
            elif not utils.is_league_running() and not utils.is_rc_running():
                self.start_league()
            sleep(2)

        if logged_in:
            raise LauncherError("Launch Error. Most likely the Riot Client needs an update or League needs an update from within Riot Client")
        else:
            raise LauncherError("Could not launch League of legends")

    def start_league(self):
        self.log.info('Launching League')
        rclient = Path(self.config.get_data('league_path')).parent.absolute().parent.absolute()
        rclient = str(rclient) + "/Riot Client/RiotClientServices"
        subprocess.Popen([rclient, "--launch-product=league_of_legends", "--launch-patchline=live"])
        sleep(3)

    def login(self) -> None:
        """Sends account credentials to Riot Client"""
        self.log.info("Logging into Riot Client")
        body = {"clientId": "riot-client", 'trustLevels': ['always_trusted']}
        r = self.connection.request("post", "/rso-auth/v2/authorizations", data=body)
        if r.status_code != 200:
            raise LauncherError("Failed Authorization Request. Response: {}".format(r.status_code))
        body = {"username": self.username, "password": self.password, "persistLogin": False}
        r = self.connection.request("put", '/rso-auth/v1/session/credentials', data=body)
        if r.status_code != 201:
            raise LauncherError("Failed Authentication Request. Response: {}".format(r.status_code))
        elif r.json()['error'] == 'auth_failure':
            raise LauncherError("Invalid username or password")

    def verify_account(self) -> bool:
        """Checks if account credentials match the account on the League Client"""
        self.log.info("Verifying logged-in account credentials")
        connection = api.Connection()
        connection.connect_lcu(verbose=False)
        r = connection.request('get', '/lol-login/v1/session')
        if r.json()['username'] != self.username:
            self.log.warning("Accounts do not match! Proceeding anyways")
            return False
        else:
            self.log.info("Account Verified")
            return True
