"""
Utility functions that interact processes.
"""

import logging
import subprocess
import os
import sys
from time import sleep

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
