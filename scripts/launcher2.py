import logging
import api
import shutil
import requests
import account
import json
from base64 import b64encode
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

    # If league is already running, check to make sure it is running the correct account
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
    while True:
        subprocess.run([LEAGUE_CLIENT_PATH])
        sleep(10)

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

    # Get Lockfile Data
    lockfile = open(RIOT_CLIENT_LOCKFILE_PATH, 'r')
    lockfile_data = lockfile.read()
    log.debug(lockfile_data)
    lockfile.close()

    # Parse data for pwd
    lock = lockfile_data.split(':')
    rcu_username = 'riot'
    rcu_procname = lock[0]
    rcu_pid = lock[1]
    rcu_port = lock[2]
    rcu_password = lock[3]
    rcu_protocol = lock[4]

    # Headers
    log.debug('{}:{}'.format(rcu_username, rcu_password))
    userpass = b64encode(bytes('{}:{}'.format(rcu_username, rcu_password), 'utf-8')).decode('ascii')
    rcu_headers = {'Authorization': 'Basic {}'.format(userpass), "Content-Type": "application/json"}
    log.debug(rcu_headers['Authorization'])

    # Login
    session = requests.session()
    fn = getattr(session, "post")
    url = "https://127.0.0.1:{}/rso-auth/v2/authorizations".format(rcu_port)
    body = {"clientId": "riot-client", 'trustLevels': ['always_trusted']}
    r = fn(url, verify=False, headers=rcu_headers, data=json.dumps(body))
    if r.status_code != 200:
        log.warning(url)
        log.warning(r.status_code)
        log.warning(r.json())
        log.error("Failed Authorization Request")
        raise LauncherError
    else:
        log.debug(r.status_code)
        log.debug(r.json())

    fn = getattr(session, "put")
    url = "https://127.0.0.1:{}/rso-auth/v1/session/credentials".format(rcu_port)
    body = {"username": username, "password": password, "persistLogin": False}
    r = fn(url, verify=False, headers=rcu_headers, data=json.dumps(body))
    if r.status_code != 201:
        log.warning(url)
        log.warning(r.status_code)
        log.warning(r.json())
        log.error("Failed Authentication Request")
        raise LauncherError
    else:
        log.debug(r.status_code)
        log.debug(r.json())


def verify_account(username):
    log.info("Verifying logged-in account credentials")
    connection = api.Connection()
    connection.init()
    r = connection.request('get', '/lol-login/v1/session')
    if r.json()['username'] != username:
        log.info("Incorrect Account")
        return False
    else:
        log.info("Account Verified")
        return True