import logging
import api
import shutil
import account
import utils
import subprocess
from time import sleep
from constants import *

log = logging.getLogger(__name__)

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

    # Check league already running
    if utils.is_league_running():
        log.info("League is already running...")
        if verify_account(username):
            return
        else:
            log.warning("The currently logged-in account is incorrect. Closing.")
            utils.close_processes()
            sleep(3)

    # Launch League
    log.info("Launching League of Legends")
    subprocess.run([LEAGUE_CLIENT_PATH])
    sleep(5)
    while True:
        if utils.exists(LEAGUE_CLIENT_WINNAME):
            log.info("League Client opened with Prior Login")
            if verify_account(username):
                return
            else:
                log.warning("The currently logged-in account is incorrect. Closing.")
                utils.close_processes()
                sleep(3)
        elif utils.exists(RIOT_CLIENT_WINNAME):
            log.info("Riot Client opened. Logging in")
            login(username, password)
            break

    for i in range(30):
        sleep(1)
        if utils.exists(LEAGUE_CLIENT_WINNAME):
            log.info("Game Successfully Launched")
            try:
                output = subprocess.check_output(KILL_RIOT_CLIENT, shell=False)
                log.info(str(output, 'utf-8').rstrip())
            except:
                log.warning("Could not kill riot client")
            return

    log.error("Application failed to launch after successful login")
    raise LauncherError

def login(username, password):
    conn = api.Connection()
    conn.init(api.Client.RIOT_CLIENT)
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

def verify_account(username):
    log.info("Verifying logged-in account credentials")
    connection = api.Connection()
    connection.init(api.Client.LEAGUE_CLIENT)
    r = connection.request('get', '/lol-login/v1/session')
    if r.json()['username'] != username:
        log.info("Incorrect Account")
        return False
    else:
        log.info("Account Verified")
        return True