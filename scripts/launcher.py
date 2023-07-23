"""
As far as I am aware there is no api that deals with the riot client
making this implementation a little jenky. If there are api endpoints
to log in through the riot client let me know
"""

import logging
import shutil
import account
import utils
import subprocess
import pyautogui
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
    username = account.get_username()
    password = account.get_password()

    # Start league
    log.info("Opening League of Legends")
    start_app(username, password)

def start_app(username, password):
    if utils.is_league_running():
        log.info("League is already running...")
        return
    log.info("Starting League of Legends")
    subprocess.run([LEAGUE_PATH])
    sleep(10)
    time_out = 0
    prior_login = True
    waiting = False
    while True:
        if time_out == 30:
            log.error("Application failed to launch")
            raise LauncherError
        if utils.exists(LEAGUE_CLIENT_WINNAME):
            if prior_login:
                log.info("League Client opened with Prior Login")
            else:
                log.info("Game Successfully Launched")
                output = subprocess.check_output(KILL_RIOT_CLIENT, shell=False)
                log.info(str(output, 'utf-8').rstrip())
            sleep(5)
            return
        if utils.exists(RIOT_CLIENT_WINNAME):
            if not waiting:
                log.info("Riot Client opened. Logging in")
                prior_login = False
                waiting = True
                time_out = 0

                # Login -> when login screen starts username field has focus
                pyautogui.getWindowsWithTitle(RIOT_CLIENT_WINNAME)
                sleep(3)
                pyautogui.typewrite(username)
                sleep(.5)
                pyautogui.press('tab')
                sleep(.5)
                pyautogui.typewrite(password)
                sleep(.5)
                pyautogui.press('enter')
                sleep(5)
            else:
                log.debug("Waiting for league to open...")
                sleep(1)
                pyautogui.press('enter')  # sometimes the riot client will force you to press 'play'
        sleep(1)
        time_out += 1