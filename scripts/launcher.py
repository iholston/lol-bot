import logging
import api
import shutil
import account
import utils
import subprocess
from time import sleep
from constants import *

log = logging.getLogger(__name__)
conn = api.Connection()

class LauncherError(Exception):
    pass

def launch_league():
    # Ensure game config file is correct
    log.info("Overwriting/creating game config")
    if os.path.exists(LEAGUE_GAME_CONFIG_PATH):
        shutil.copyfile(LOCAL_GAME_CONFIG_PATH, LEAGUE_GAME_CONFIG_PATH)
    else:
        shutil.copy2(LOCAL_GAME_CONFIG_PATH, LEAGUE_GAME_CONFIG_PATH)

    # Get account username and password
    log.info("Retrieving account credentials")
    username = account.get_username()
    password = account.get_password()

    # Assess game state and launch
    launch_handler(username, password)

def launch_handler(username, password):
    conn.init(api.Client.RIOT_CLIENT)
    logged_in = False

    for i in range(100):
        # League is running
        if utils.is_league_running():
            log.info("League is already running...")
            verify_account(username)
            return

        # League is not running but Riot Client is running
        elif not utils.is_league_running() and utils.is_rc_running():

            # Not logged in
            r = conn.request("get", "/rso-auth/v1/authorization/userinfo")
            if r.status_code == 404 and not logged_in:
                login(username, password)
                logged_in = True
                sleep(3)

            # Somehow randomly logged in
            elif r.status_code == 200 and not logged_in:
                conn.request("delete", "/rso-auth/v1/session")  # log out
                sleep(3)

            # Logged in
            elif r.status_code == 200 and logged_in:

                # Patching
                r = conn.request("get", "/patch-proxy/v1/active-updates")
                while len(r.json()) != 0:
                    sleep(2)
                    log.info("Riot Client is patching...")
                    log.debug(r.json())
                    r = conn.request("get", "/patch-proxy/v1/active-updates")

                # Not patching (can choose a game to launch)
                subprocess.run([LEAGUE_CLIENT_PATH])
                sleep(3)

        # Nothing is running
        elif not utils.is_league_running() and not utils.is_rc_running():
            subprocess.run([LEAGUE_CLIENT_PATH])
            sleep(3)

        sleep(2)

def login(username, password):
    log.info("Logging in")
    body = {"clientId": "riot-client", 'trustLevels': ['always_trusted']}
    r = conn.request("post", "/rso-auth/v2/authorizations", data=body)
    if r.status_code != 200:
        log.error("Failed Authorization Request. Response: {}".format(r.status_code))
        raise LauncherError
    body = {"username": username, "password": password, "persistLogin": False}
    r = conn.request("put", '/rso-auth/v1/session/credentials', data=body)
    if r.status_code != 201:
        log.error("Failed Authentication Request. Response: {}".format(r.status_code))
        raise LauncherError
    elif r.json()['error'] == 'auth_failure':
        log.error("Invalid Credentials. Please ensure username/password is correct")
        raise LauncherError

def verify_account(username):
    log.info("Verifying logged-in account credentials")
    connection = api.Connection()
    connection.init(api.Client.LEAGUE_CLIENT)
    r = connection.request('get', '/lol-login/v1/session')
    if r.json()['username'] != username:
        log.warning("Incorrect Account!")
        return False
    else:
        log.info("Account Verified")
        return True