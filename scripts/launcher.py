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

class InvalidCredentials(Exception):
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
    logged_in = False

    for i in range(100):
        # League is running and there was a successful login attempt
        if utils.is_league_running() and logged_in:
            log.info("Launch Success!")
            try:
                output = subprocess.check_output(KILL_RIOT_CLIENT, shell=False)
                log.info(str(output, 'utf-8').rstrip())
            except:
                log.warning("Could not kill riot client")
            return

        # League is running without a login attempt
        elif utils.is_league_running() and not logged_in:
            log.info("League already running")
            verify_account(username)
            return

        # League is not running but Riot Client is running
        elif not utils.is_league_running() and utils.is_rc_running():

            # Get session state
            try:
                conn.init(api.Client.RIOT_CLIENT)
                r = conn.request("get", "/rso-auth/v1/session")
            except:
                log.warning("Could not get session state")
                continue

            # Not logged in and haven't logged in
            if r.status_code == 404 and not logged_in:
                login(username, password)
                logged_in = True
                sleep(1)

            # Somehow randomly logged in
            elif r.status_code == 200 and not logged_in:
                log.info("Deleting rso session..")
                conn.request("delete", "/rso-auth/v1/session")  # log out
                sleep(1)

            # Logged in
            elif r.status_code == 200 and logged_in:

                # Patching
                # r = conn.request("get", "/patch-proxy/v1/active-updates")  # figure out correct endpoint to see if league needs update
                # while len(r.json()) != 0:
                #     sleep(2)
                #     log.info("Riot Client is patching...")
                #     log.debug(r.json())
                #     r = conn.request("get", "/patch-proxy/v1/active-updates")

                # Not patching (can choose a game to launch)
                log.info("Authenticated. Attempting to Launch League...")
                subprocess.run([LEAGUE_CLIENT_PATH])
                sleep(3)

        # Nothing is running
        elif not utils.is_league_running() and not utils.is_rc_running():
            log.info("Attempting to Launch League...")
            subprocess.run([LEAGUE_CLIENT_PATH])
            sleep(3)

        sleep(2)

    if logged_in:
        log.error("Launch Error. Most likely the Riot Client needs an update or League needs an update from within Riot Client")
    else:
        log.error("Could not launch League of legends")
    raise LauncherError

def login(username, password):
    log.info("Logging in.")
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
        log.error("Invalid Credentials.")
        raise InvalidCredentials

def verify_account(username):
    log.info("Verifying logged-in account credentials...")
    connection = api.Connection()
    connection.init(api.Client.LEAGUE_CLIENT, verbose=False)
    r = connection.request('get', '/lol-login/v1/session')
    if r.json()['username'] != username:
        log.warning("Incorrect Account! Proceeding anyways..")
        return False
    else:
        log.info("Account Verified")
        return True