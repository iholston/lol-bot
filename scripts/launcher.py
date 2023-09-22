"""
Handles the Riot Client and launches League of Legends
"""

import logging
import api
import shutil
import utils
import os
import subprocess
from time import sleep
from constants import *

class Launcher:
    """Handles the Riot Client and launches League of Legends"""

    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.connection = api.Connection()
        self.username = ""
        self.password = ""

    def launch_league(self, username, password):
        """Runs setup logic and starts launch sequence"""
        self.set_game_config()
        self.username = username
        self.password = password
        self.launch_loop()

    def set_game_config(self):
        """Overwrites the League of Legends game config"""
        self.log.info("Overwriting/creating game config")
        if os.path.exists(LEAGUE_GAME_CONFIG_PATH):
            shutil.copyfile(LOCAL_GAME_CONFIG_PATH, LEAGUE_GAME_CONFIG_PATH)
        else:
            shutil.copy2(LOCAL_GAME_CONFIG_PATH, LEAGUE_GAME_CONFIG_PATH)

    def launch_loop(self):
        """Handles tasks necessary to open the League of Legends client"""
        logged_in = False

        for i in range(100):

            # League is running and there was a successful login attempt
            if utils.is_league_running() and logged_in:
                self.log.info("Launch Success!")
                try:
                    output = subprocess.check_output(KILL_RIOT_CLIENT, shell=False)
                    self.log.info(str(output, 'utf-8').rstrip())
                except:
                    self.log.warning("Could not kill riot client")
                return

            # League is running without a login attempt
            elif utils.is_league_running() and not logged_in:
                self.log.warning("League opened with prior login")
                self.verify_account()
                return

            # League is not running but Riot Client is running
            elif not utils.is_league_running() and utils.is_rc_running():

                # Get session state
                self.connection.connect_rc()
                r = self.connection.request("get", "/rso-auth/v1/authorization/access-token")

                # Already logged in
                if r.status_code == 200 and not logged_in:
                    self.log.info("Already logged in. Launching League...")
                    subprocess.run([LEAGUE_CLIENT_PATH])
                    sleep(3)

                # Not logged in and haven't logged in
                if r.status_code == 404 and not logged_in:
                    self.login()
                    logged_in = True
                    sleep(1)

                # Logged in
                elif r.status_code == 200 and logged_in:
                    self.log.info("Authenticated. Attempting to Launch League...")
                    subprocess.run([LEAGUE_CLIENT_PATH])
                    sleep(3)

            # Nothing is running
            elif not utils.is_league_running() and not utils.is_rc_running():
                self.log.info("Attempting to Launch League...")
                subprocess.run([LEAGUE_CLIENT_PATH])
                sleep(3)
            sleep(2)

        if logged_in:
            raise Exception("Launch Error. Most likely the Riot Client needs an update or League needs an update from within Riot Client")
        else:
            raise Exception("Could not launch League of legends")


    def login(self):
        """Sends account credentials to Riot Client"""
        self.log.info("Logging in.")
        body = {"clientId": "riot-client", 'trustLevels': ['always_trusted']}
        r = self.connection.request("post", "/rso-auth/v2/authorizations", data=body)
        if r.status_code != 200:
            raise Exception("Failed Authorization Request. Response: {}".format(r.status_code))
        body = {"username": self.username, "password": self.password, "persistLogin": False}
        r = self.connection.request("put", '/rso-auth/v1/session/credentials', data=body)
        if r.status_code != 201:
            raise Exception("Failed Authentication Request. Response: {}".format(r.status_code))
        elif r.json()['error'] == 'auth_failure':
            raise ValueError("Invalid username or password.")

    def verify_account(self):
        """Checks if account credentials match the account on the League Client"""
        self.log.info("Verifying logged-in account credentials")
        connection = api.Connection()
        connection.connect_lcu(verbose=False)
        r = connection.request('get', '/lol-login/v1/session')
        if r.json()['username'] != self.username:
            self.log.warning("Incorrect Account! Proceeding anyways..")
            return False
        else:
            self.log.info("Account Verified")
            return True