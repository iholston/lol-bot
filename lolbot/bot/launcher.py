"""
Handles launching League of Legends and logging into an account.
"""

import logging
from time import sleep

from lolbot.system import cmd, keys
from lolbot.lcu.league_client import LeagueClient, LCUError

log = logging.getLogger(__name__)


class LaunchError(Exception):
    """Indicates that League could not be opened."""
    pass

class Launcher:
    """Handles launching the League of Legends client and logging in"""

    def __init__(self):
        self.api = LeagueClient()
        self.username = ''
        self.password = ''
        self.attempts = 0
        self.success = False

    def launch_league(self, username: str = '', password: str = ''):
        self.username = username
        self.password = password
        for i in range(30):
            self.launch_sequence()
            if self.success:
                sleep(30)
                return
        raise LaunchError("Could not open League. Ensure there are no pending updates.")

    def launch_sequence(self):
        self.api.update_auth()

        # League is Running
        if cmd.run(cmd.IS_CLIENT_RUNNING):
            if self.attempts == 0:
                log.warning("League opened with prior login")
                self.verify_account()
            else:
                log.info("Launch success")
                #cmd.run(cmd.CLOSE_LAUNCHER)
            self.success = True

        # Riot Client is opened and Logged In
        elif cmd.run(cmd.IS_LAUNCHER_RUNNING) and self.api.access_token_exists():
            if self.attempts == 0:
                log.warning("Riot Client has previous login")
            try:
                log.info("Logged into client. Launching League")
                self.api.launch_league_from_rc()
            except LCUError:
                pass
            return

        # Riot Client is opened and Not Logged In
        elif cmd.run(cmd.IS_LAUNCHER_RUNNING):
            if self.attempts == 5:
                raise LaunchError("Max login attempts exceeded. Check username and password")
            log.info("Logging into Riot Client")
            self.attempts += 1
            # self.lcu.login(self.username, self.password)
            self.manual_login()

        # Nothing is opened
        else:
            log.info("Launching League of Legends")
            cmd.run(cmd.LAUNCH_CLIENT)
            sleep(15)

    def manual_login(self):
        """
        Sends keystrokes into username and password fields. Only use if
        Riot Client lcu login does not work.
        """
        log.info('Manually logging into Riot Client')
        keys.write(self.username)
        sleep(.5)
        keys.press_and_release('tab')
        sleep(.5)
        keys.write(self.password)
        sleep(.5)
        keys.press_and_release('enter')
        sleep(10)
        if not self.api.access_token_exists():
            log.warning("Login attempt failed")
            cmd.run(cmd.CLOSE_ALL)
            sleep(5)

    def verify_account(self) -> bool:
        """Checks if account username match the account that is currently logged in."""
        log.info("Verifying logged-in account credentials")
        try:
            if self.username == self.api.get_summoner_name():
                log.info("Account Verified")
                return True
            else:
                log.warning("Accounts do not match!")
                return False
        except LCUError:
            log.warning("Could not get account information")
            return False
