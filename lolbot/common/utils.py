"""
Utility functions that interact with game windows and processes
"""

import logging
import subprocess
import os
import sys
from time import sleep

import keyboard
import mouse
import pyautogui
from win32gui import FindWindow, GetWindowRect


log = logging.getLogger(__name__)

# WINDOW NAMES
LEAGUE_CLIENT_WINNAME = "League of Legends"
LEAGUE_GAME_CLIENT_WINNAME = "League of Legends (TM) Client"

# PROCESS NAMES
LEAGUE_PROCESS_NAMES = ["LeagueClient.exe", "League of Legends.exe"]
RIOT_CLIENT_PROCESS_NAMES = ["RiotClientUx.exe", "RiotClientServices.exe", "Riot Client.exe"]

# COMMANDS
KILL_CRASH_HANDLER = 'TASKKILL /F /IM LeagueCrashHandler64.exe'
KILL_LEAGUE_CLIENT = 'TASKKILL /F /IM LeagueClient.exe'
KILL_LEAGUE = 'TASKKILL /F /IM "League of Legends.exe"'
KILL_RIOT_CLIENT = 'TASKKILL /F /IM RiotClientUx.exe'
KILL_HANDLER_WMIC = 'wmic process where "name=\'LeagueCrashHandler64.exe\'" delete'
KILL_LEAGUE_WMIC = 'wmic process where "name=\'LeagueClient.exe\'" delete'


class WindowNotFound(Exception):
    pass


def is_league_running() -> bool:
    """Checks if league processes exists"""
    res = subprocess.check_output(["TASKLIST"], creationflags=0x08000000)
    output = str(res)
    for name in LEAGUE_PROCESS_NAMES:
        if name in output:
            return True
    return False


def is_rc_running() -> bool:
    """Checks if riot client process exists"""
    res = subprocess.check_output(["TASKLIST"], creationflags=0x08000000)
    output = str(res)
    for name in RIOT_CLIENT_PROCESS_NAMES:
        if name in output:
            return True
    return False


def is_game_running() -> bool:
    """Checks if game process exists"""
    res = subprocess.check_output(["TASKLIST"], creationflags=0x08000000)
    output = str(res)
    if "League of Legends.exe" in output:
        return True
    return False


def close_all_processes() -> None:
    """Closes all league related processes"""
    log.info("Terminating league related processes")
    os.system(KILL_CRASH_HANDLER)
    os.system(KILL_LEAGUE)
    os.system(KILL_LEAGUE_CLIENT)
    os.system(KILL_RIOT_CLIENT)
    os.system(KILL_HANDLER_WMIC)
    os.system(KILL_LEAGUE_WMIC)
    sleep(5)


def close_game() -> None:
    """Closes the League of Legends game process"""
    log.info("Terminating game instance")
    os.system(KILL_LEAGUE)
    sleep(15)


def resource_path(relative_path: str) -> str:
    """Returns pyinstaller path if exe or abs path"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def close_riot_client() -> None:
    """Closes the League of Legends game process"""
    log.info("Closing riot client")
    try:
        os.system(KILL_RIOT_CLIENT)
    except:
        log.warning("Could not kill riot client")
    sleep(2)


def size(window_title: str = LEAGUE_CLIENT_WINNAME) -> tuple:
    """Gets the size of an open window"""
    window_handle = FindWindow(None, window_title)
    if window_handle == 0:
        raise WindowNotFound
    window_rect = GetWindowRect(window_handle)
    return window_rect[0], window_rect[1], window_rect[2], window_rect[3]


def exists(window_title: str) -> bool:
    """Checks if a window exists"""
    if FindWindow(None, window_title) == 0:
        return False
    return True


def click(ratio: tuple, expected_window_name: str = '', wait: int or float = 1) -> None:
    """Makes a click in an open window"""
    if expected_window_name != '' and not exists(expected_window_name):
        log.debug("Cannot click on {}, {} does not exist".format(ratio, expected_window_name))
        raise WindowNotFound
    elif expected_window_name != '':
        window_name = expected_window_name
    else:  # check if game is running and default to game otherwise set window to league client
        if exists(LEAGUE_GAME_CLIENT_WINNAME):
            window_name = LEAGUE_GAME_CLIENT_WINNAME
        elif exists(LEAGUE_CLIENT_WINNAME):
            window_name = LEAGUE_CLIENT_WINNAME
        else:
            log.debug("Cannot click on {}, no available window".format(ratio))
            return
    log.debug('Clicking on ratio {}: {}, {}. Waiting: {}'.format(ratio, ratio[0], ratio[1], wait))
    x, y, l, h = size(window_name)
    updated_x = ((l - x) * ratio[0]) + x
    updated_y = ((h - y) * ratio[1]) + y
    pyautogui.moveTo(updated_x, updated_y)
    sleep(.5)
    mouse.click()  # pyautogui clicks do not work with league/directx
    sleep(wait)


def right_click(ratio: tuple, expected_window: str = '', wait: int or float = 1) -> None:
    """Makes a right click in an open window"""
    if expected_window != '' and not exists(expected_window):
        log.debug("Cannot click on {}, {} does not exist".format(ratio, expected_window))
        raise WindowNotFound
    elif expected_window != '':
        window_name = expected_window
    else:  # check if game is running and default to game otherwise set window to league client
        if exists(LEAGUE_GAME_CLIENT_WINNAME):
            window_name = LEAGUE_GAME_CLIENT_WINNAME
        elif exists(LEAGUE_CLIENT_WINNAME):
            window_name = LEAGUE_CLIENT_WINNAME
        else:
            log.debug("Cannot click on {}, no available window".format(ratio))
            return
    log.debug('Clicking on ratio {}: {}, {}. Waiting: {}'.format(ratio, ratio[0], ratio[1], wait))
    x, y, l, h = size(window_name)
    updated_x = ((l - x) * ratio[0]) + x
    updated_y = ((h - y) * ratio[1]) + y
    pyautogui.moveTo(updated_x, updated_y)
    sleep(.5)
    mouse.right_click()  # pyautogui clicks do not work with league/directx
    sleep(wait)


def attack_move_click(ratio: tuple, wait: int or float = 1) -> None:
    """Attack move clicks in an open League of Legends game window"""
    if not exists(LEAGUE_GAME_CLIENT_WINNAME):
        log.debug("Cannot attack move when game is not running")
        raise WindowNotFound
    log.debug('Attack Moving on ratio {}: {}, {}. Waiting: {}'.format(ratio, ratio[0], ratio[1], wait))
    x, y, l, h = size(LEAGUE_GAME_CLIENT_WINNAME)
    updated_x = ((l - x) * ratio[0]) + x
    updated_y = ((h - y) * ratio[1]) + y
    pyautogui.moveTo(updated_x, updated_y)
    sleep(.5)
    keyboard.press('a')
    sleep(.1)
    mouse.click()
    sleep(.1)
    mouse.click()
    keyboard.release('a')
    sleep(wait)


def press(key: str, expected_window: str = '', wait: int or float = 1) -> None:
    """Sends a keypress to a window"""
    if expected_window != '' and not exists(expected_window):
        log.debug("Cannot press {}, {} does not exist".format(key, expected_window))
        raise WindowNotFound
    log.debug("Pressing key: {}. Waiting: {}".format(key, wait))
    keyboard.press_and_release(key)
    sleep(wait)


def write(keys: str, expected_window: str = '', wait: int or float = 1) -> None:
    """Sends a string of key presses to a window"""
    if expected_window != '' and not exists(expected_window):
        log.debug("Cannot type {}, {} does not exist".format(keys, expected_window))
        raise WindowNotFound
    log.debug("Typewriting {}. Waiting: {}".format(keys, wait))
    pyautogui.typewrite(keys)
    sleep(wait)


def seconds_to_min_sec(seconds: str or float or int) -> str:
    """Converts League of Legends game time to minute:seconds format"""
    try:
        if isinstance(seconds, int) or isinstance(seconds, float):
            if len(str(int(seconds % 60))) == 1:
                return str(int(seconds / 60)) + ":0" + str(int(seconds % 60))
            else:
                return str(int(seconds / 60)) + ":" + str(int(seconds % 60))
        elif isinstance(seconds, str):
            seconds = float(seconds)
            if len(str(int(seconds % 60))) == 1:
                return str(int(seconds / 60)) + ":0" + str(int(seconds % 60))
            else:
                return str(int(seconds / 60)) + ":" + str(int(seconds % 60))
    except ValueError:
        return "XX:XX"


def print_ascii() -> None:
    """Prints some ascii art"""
    print("""\n\n            
                ──────▄▌▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌
                ───▄▄██▌█ BEEP BEEP
                ▄▄▄▌▐██▌█ -15 LP DELIVERY
                ███████▌█▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌
                ▀(⊙)▀▀▀▀▀▀▀(⊙)(⊙)▀▀▀▀▀▀▀▀▀▀(⊙)\n\n\t\t\tLoL Bot\n\n""")
